import psycopg2
import requests
from dotenv import load_dotenv
import os
from dagster import op, EnvVar, Config, OpExecutionContext
import os
import datetime
from analytics.resources import PostgresqlDatabaseResource

class StravaConfig(Config):
    client_id: int = EnvVar("client_id")
    client_secret: str = EnvVar("client_secret")
    refresh_token: str = EnvVar("refresh_token")
    client_id_2: int = EnvVar("client_id_2")
    client_secret_2: str = EnvVar("client_secret_2")
    refresh_token_2: str = EnvVar("refresh_token_2")
    date: str

@op
def create_strava_database( context: OpExecutionContext, postgres_conn: PostgresqlDatabaseResource ):
    context.log.info('Creating strava database if it does not exist')
    connection = None
    try:
        # Connect to the database
        connection = psycopg2.connect(
                                      user=postgres_conn.postgres_user,
                                      password=postgres_conn.postgres_password,
                                      host=postgres_conn.postgres_host,
                                      port=postgres_conn.postgres_port, 
                                      database=postgres_conn.postgres_db)
        # Connecting to the default 'postgres' database
        connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()
        
        # Check if the 'strava' database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname='strava'")
        exists = cursor.fetchone()
        if not exists:

            # Create the 'strava' database if it doesn't exist
            cursor.execute("CREATE DATABASE strava")
            print("Database 'strava' created successfully")
        else:
            print("Database 'strava' already exists")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error while creating 'strava' database: {error}")

    finally:
        if connection:
            cursor.close()
            connection.close()

@op
def create_athlete_table( context: OpExecutionContext, postgres_conn: PostgresqlDatabaseResource ):
    context.log.info('Creating athlete table')
    command = (
        """
        CREATE TABLE IF NOT EXISTS athletes (
            id BIGINT PRIMARY KEY,
            username VARCHAR(255),
            resource_state INT,
            firstname VARCHAR(255),
            lastname VARCHAR(255),
            bio TEXT,
            city VARCHAR(255),
            state VARCHAR(255),
            country VARCHAR(255),
            sex CHAR(1),
            premium BOOLEAN,
            summit BOOLEAN,
            created_at TIMESTAMP WITHOUT TIME ZONE,
            updated_at TIMESTAMP WITHOUT TIME ZONE,
            badge_type_id INT,
            weight FLOAT,
            profile_medium VARCHAR(255),
            profile VARCHAR(255),
            friend BOOLEAN,
            follower BOOLEAN,
            last_activity_date TIMESTAMP WITHOUT TIME ZONE  -- New column for tracking the last activity date
        );
        """
    )
    connection = None
    try:
        connection = psycopg2.connect(user=postgres_conn.postgres_user,
                                      password=postgres_conn.postgres_password,
                                      host=postgres_conn.postgres_host,
                                      port=postgres_conn.postgres_port, 
                                      database=postgres_conn.postgres_db)
        cursor = connection.cursor()
        cursor.execute(command)
        cursor.close()
        connection.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error while creating athlete table:", error)
    finally:
        if connection is not None:
            connection.close()

@op
def extract_athlete_data( context: OpExecutionContext, access_token ):
    context.log.info('Extracting athlete data')
    athlete_url = "https://www.strava.com/api/v3/athlete"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(athlete_url, headers=headers)
    athlete_data = response.json()
    return athlete_data

@op
def load_athlete_data(  context: OpExecutionContext, athlete_data, activities_data, postgres_conn: PostgresqlDatabaseResource ):
    context.log.info('Loading athlete data')
    connection = psycopg2.connect(  user=postgres_conn.postgres_user,
                                      password=postgres_conn.postgres_password,
                                      host=postgres_conn.postgres_host,
                                      port=postgres_conn.postgres_port, 
                                      database=postgres_conn.postgres_db)
    cursor = connection.cursor()

    # Base insert query for athlete data without last_activity_date
    insert_query_base = """INSERT INTO athletes (id, username, resource_state, firstname, lastname, bio, city, state, country, sex, premium, summit, created_at, updated_at, badge_type_id, weight, profile_medium, profile, friend, follower) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO UPDATE SET username = EXCLUDED.username, resource_state = EXCLUDED.resource_state, firstname = EXCLUDED.firstname, lastname = EXCLUDED.lastname, bio = EXCLUDED.bio, city = EXCLUDED.city, state = EXCLUDED.state, country = EXCLUDED.country, sex = EXCLUDED.sex, premium = EXCLUDED.premium, summit = EXCLUDED.summit, created_at = EXCLUDED.created_at, updated_at = EXCLUDED.updated_at, badge_type_id = EXCLUDED.badge_type_id, weight = EXCLUDED.weight, profile_medium = EXCLUDED.profile_medium, profile = EXCLUDED.profile, friend = EXCLUDED.friend, follower = EXCLUDED.follower"""

    # Base data tuple without last_activity_date
    data_base = (
        athlete_data.get('id'),
        athlete_data.get('username'),
        athlete_data.get('resource_state'),
        athlete_data.get('firstname'),
        athlete_data.get('lastname'),
        athlete_data.get('bio'),
        athlete_data.get('city'),
        athlete_data.get('state'),
        athlete_data.get('country'),
        athlete_data.get('sex'),
        athlete_data.get('premium'),
        athlete_data.get('summit'),
        athlete_data.get('created_at'),
        athlete_data.get('updated_at'),
        athlete_data.get('badge_type_id'),
        athlete_data.get('weight'),
        athlete_data.get('profile_medium'),
        athlete_data.get('profile'),
        athlete_data.get('friend'),
        athlete_data.get('follower'),
    )

    if activities_data:
        # If there are new activities, include last_activity_date in the insert query
        most_recent_activity_date = activities_data[0]['start_date']
        insert_query = insert_query_base + ", last_activity_date = %s"
        data = data_base + (most_recent_activity_date,)
    else:
        # If there are no new activities, do not update last_activity_date
        insert_query = insert_query_base
        data = data_base

    cursor.execute(insert_query, data)
    connection.commit()
    cursor.close()
    connection.close()


@op
def create_activities_table( context: OpExecutionContext, postgres_conn: PostgresqlDatabaseResource, ):
    context.log.info('Creating activities table')
    command = (
        """
        CREATE TABLE IF NOT EXISTS activities (
            id BIGINT PRIMARY KEY,
            resource_state INT,
            athlete_id BIGINT,
            name VARCHAR(255),
            distance FLOAT,
            moving_time INT,
            elapsed_time INT,
            total_elevation_gain FLOAT,
            type VARCHAR(50),
            sport_type VARCHAR(50),
            workout_type VARCHAR(50),
            start_date TIMESTAMP WITHOUT TIME ZONE,
            start_date_local TIMESTAMP WITHOUT TIME ZONE,
            timezone VARCHAR(255),
            utc_offset FLOAT,
            location_city VARCHAR(255),
            location_state VARCHAR(255),
            location_country VARCHAR(255),
            achievement_count INT,
            kudos_count INT,
            comment_count INT,
            athlete_count INT,
            photo_count INT,
            map_id VARCHAR(255),
            trainer BOOLEAN,
            commute BOOLEAN,
            manual BOOLEAN,
            private BOOLEAN,
            visibility VARCHAR(50),
            flagged BOOLEAN,
            gear_id VARCHAR(255),
            start_latlng VARCHAR(255),
            end_latlng VARCHAR(255),
            average_speed FLOAT,
            max_speed FLOAT,
            average_cadence FLOAT,
            average_temp INT,
            has_heartrate BOOLEAN,
            average_heartrate FLOAT,
            max_heartrate FLOAT,
            heartrate_opt_out BOOLEAN,
            display_hide_heartrate_option BOOLEAN,
            elev_high FLOAT,
            elev_low FLOAT,
            upload_id BIGINT,
            upload_id_str VARCHAR(255),
            external_id VARCHAR(255),
            from_accepted_tag BOOLEAN,
            pr_count INT,
            total_photo_count INT,
            has_kudoed BOOLEAN
        );
        """
    )

    connection = None
    try:
        connection = psycopg2.connect(user=postgres_conn.postgres_user,
                                      password=postgres_conn.postgres_password,
                                      host=postgres_conn.postgres_host,
                                      port=postgres_conn.postgres_port, 
                                      database=postgres_conn.postgres_db)
        cursor = connection.cursor()
        cursor.execute(command)
        cursor.close()
        connection.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error while creating activities table:", error)
    finally:
        if connection is not None:
            connection.close()


@op
def get_access_token( context: OpExecutionContext, config: StravaConfig ):
    context.log.info('Getting access token for athlete 1')

    auth_url = "https://www.strava.com/oauth/token"
    payload = {
        'client_id': config.client_id,
        'client_secret': config.client_secret,
        'refresh_token': config.refresh_token,
        'grant_type': "refresh_token",
        'f': 'json'
    }
    response = requests.post(auth_url, data=payload, verify=False)
    access_token = response.json()['access_token']
    return access_token
@op
def get_access_token_2( context: OpExecutionContext, config: StravaConfig ):
    context.log.info('Getting access token for athlete 2')

    auth_url = "https://www.strava.com/oauth/token"
    payload = {
        'client_id': config.client_id_2,
        'client_secret': config.client_secret_2,
        'refresh_token': config.refresh_token_2,
        'grant_type': "refresh_token",
        'f': 'json'
    }
    response = requests.post(auth_url, data=payload, verify=False)
    access_token = response.json()['access_token']
    return access_token

@op
def extract_strava_activities( context: OpExecutionContext, access_token, athlete_data, postgres_conn: PostgresqlDatabaseResource, config: StravaConfig ):
    context.log.info('Extracting activity data')

    """
    Fetches Strava activities for a specified athlete that occurred after the athlete's last activity date stored in the database.

    This operation incrementally extracts new activities for an individual athlete, ensuring only activities not previously fetched are retrieved. It uses the 'after' parameter in the Strava API request to filter activities by date, based on the last recorded activity date for the athlete in the database.

    Parameters:
    - access_token (str): The OAuth token used for authenticating with the Strava API.
    - athlete_data (dict): A dictionary containing at least the 'id' of the athlete whose activities are to be fetched.
    - config (StravaConfig): A configuration object containing database connection parameters and possibly other Strava-specific settings.

    Returns:
    - list: A list of activity data in JSON format returned from the Strava API for the specified athlete, filtered to include only activities after the athlete's last activity date in the database.
    """

    athlete_id = athlete_data['id']
    partition_date = datetime.datetime.strptime(config.date, "%Y-%m-%d")
    # partition_date = datetime.datetime.strptime("2020-01-01", "%Y-%m-%d")
    connection = psycopg2.connect(user=postgres_conn.postgres_user,
                                      password=postgres_conn.postgres_password,
                                      host=postgres_conn.postgres_host,
                                      port=postgres_conn.postgres_port, 
                                      database=postgres_conn.postgres_db)
    cursor = connection.cursor()

    # Query to get the last_activity_date for the given athlete_id
    cursor.execute("SELECT last_activity_date FROM athletes WHERE id = %s", (athlete_id,))
    result = cursor.fetchone()
    last_activity_date = result[0] if result else None

    cursor.close()
    connection.close()

    # Determine the start point for fetching activities: use the later of the last activity date (if it exists) or the partition date.
    if last_activity_date and last_activity_date > partition_date:
        effective_after_date = last_activity_date
    else:
        effective_after_date = partition_date

    # Convert effective 'after' date to UNIX timestamp
    start_date_unix = int(effective_after_date.timestamp())
    
    activities_url = "https://www.strava.com/api/v3/athlete/activities"
    
    headers = {'Authorization': f'Bearer {access_token}'}
    
    params = {
        'after': start_date_unix
        }
    activities_response = requests.get(activities_url, headers=headers, params=params).json()
    return activities_response


@op
def get_latest_activity_date(postgres_conn: PostgresqlDatabaseResource):
    """
      Incrementally query the database for the most recent start_date of stored activities
    """ 
    connection = psycopg2.connect(user=postgres_conn.postgres_user,
                                      password=postgres_conn.postgres_password,
                                      host=postgres_conn.postgres_host,
                                      port=postgres_conn.postgres_port, 
                                      database=postgres_conn.postgres_db)
    cursor = connection.cursor()

    cursor.execute("SELECT MAX(start_date) FROM activities")
    latest_start_date = cursor.fetchone()[0]

    cursor.close()
    connection.close()

    return latest_start_date


@op
def load_into_database(context: OpExecutionContext, activities_data, postgres_conn: PostgresqlDatabaseResource ):
    context.log.info('Loading activity data')
    # Database connection
    connection = psycopg2.connect(user=postgres_conn.postgres_user,
                                      password=postgres_conn.postgres_password,
                                      host=postgres_conn.postgres_host,
                                      port=postgres_conn.postgres_port, 
                                      database=postgres_conn.postgres_db)
    cursor = connection.cursor()

    # SQL query to insert data
    insert_query = """INSERT INTO activities (id, resource_state, athlete_id, name, distance, moving_time, elapsed_time, total_elevation_gain, type, sport_type, workout_type, start_date, start_date_local, timezone, utc_offset, location_city, location_state, location_country, achievement_count, kudos_count, comment_count, athlete_count, photo_count, map_id, trainer, commute, manual, private, visibility, flagged, gear_id, start_latlng, end_latlng, average_speed, max_speed, average_cadence, average_temp, has_heartrate, average_heartrate, max_heartrate, heartrate_opt_out, display_hide_heartrate_option, elev_high, elev_low, upload_id, upload_id_str, external_id, from_accepted_tag, pr_count, total_photo_count, has_kudoed) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING;"""

    for activity in activities_data:
        # Extracting athlete id separately
        athlete_id = activity['athlete']['id'] if 'athlete' in activity and 'id' in activity['athlete'] else None
        # Prepare data for insertion
        data = (
            activity.get('id'),
            activity.get('resource_state'),
            athlete_id,
            activity.get('name'),
            activity.get('distance'),
            activity.get('moving_time'),
            activity.get('elapsed_time'),
            activity.get('total_elevation_gain'),
            activity.get('type'),
            activity.get('sport_type'),
            activity.get('workout_type'),
            activity.get('start_date'),
            activity.get('start_date_local'),
            activity.get('timezone'),
            activity.get('utc_offset'),
            activity.get('location_city'),
            activity.get('location_state'),
            activity.get('location_country'),
            activity.get('achievement_count'),
            activity.get('kudos_count'),
            activity.get('comment_count'),
            activity.get('athlete_count'),
            activity.get('photo_count'),
            activity.get('map', {}).get('id'),
            activity.get('trainer'),
            activity.get('commute'),
            activity.get('manual'),
            activity.get('private'),
            activity.get('visibility'),
            activity.get('flagged'),
            activity.get('gear_id'),
            str(activity.get('start_latlng')),
            str(activity.get('end_latlng')),
            activity.get('average_speed'),
            activity.get('max_speed'),
            activity.get('average_cadence'),
            activity.get('average_temp'),
            activity.get('has_heartrate'),
            activity.get('average_heartrate'),
            activity.get('max_heartrate'),
            activity.get('heartrate_opt_out'),
            activity.get('display_hide_heartrate_option'),
            activity.get('elev_high'),
            activity.get('elev_low'),
            activity.get('upload_id'),
            activity.get('upload_id_str'),
            activity.get('external_id'),
            activity.get('from_accepted_tag'),
            activity.get('pr_count'),
            activity.get('total_photo_count'),
            activity.get('has_kudoed')
        )
        # Insert data into the table
        cursor.execute(insert_query, data)

    # Commit the transaction and close the connection
    connection.commit()
    cursor.close()
    connection.close()

    
@op
def print_op(athlete_data, activities_data):
    """Prints output athlete and activities data"""
    print(athlete_data, activities_data)