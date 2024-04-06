import psycopg2
import requests
from dotenv import load_dotenv
import os
from dagster import op, EnvVar, Config, OpExecutionContext
import os
import datetime

class StravaConfig(Config):
    # TODO: use resources for postgres connection
    # TODO: set up partitions
    postgres_user: str = EnvVar("postgres_user")
    postgres_password: str = EnvVar("postgres_password")
    postgres_host: str = EnvVar("postgres_host")
    postgres_port: int = EnvVar("postgres_port")
    postgres_db: str = EnvVar("postgres_db")
    client_id: int = EnvVar("client_id")
    client_secret: str = EnvVar("client_secret")
    refresh_token: str = EnvVar("refresh_token")
    client_id_2: int = EnvVar("client_id_2")
    client_secret_2: str = EnvVar("client_secret_2")
    refresh_token_2: str = EnvVar("refresh_token_2")
    date: str


@op
def create_strava_database( config: StravaConfig):
    connection = None
    try:
        # Connect to the database
        connection = psycopg2.connect(
                                      user=config.postgres_user,
                                      password=config.postgres_password,
                                      host=config.postgres_host,
                                      port=config.postgres_port, 
                                      database=config.postgres_db)
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
def create_athlete_table( config: StravaConfig):
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
        connection = psycopg2.connect(user=config.postgres_user,
                                      password=config.postgres_password,
                                      host=config.postgres_host,
                                      port=config.postgres_port, 
                                      database=config.postgres_db)
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
def fetch_athlete_data(access_token):
    athlete_url = "https://www.strava.com/api/v3/athlete"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(athlete_url, headers=headers)
    athlete_data = response.json()
    return athlete_data

@op
def insert_athlete_data( athlete_data, activities_data, config: StravaConfig):
    connection = psycopg2.connect(user=config.postgres_user,
                                      password=config.postgres_password,
                                      host=config.postgres_host,
                                      port=config.postgres_port, 
                                      database=config.postgres_db)
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
def create_activities_table( config: StravaConfig):
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
        connection = psycopg2.connect(user=config.postgres_user,
                                      password=config.postgres_password,
                                      host=config.postgres_host,
                                      port=config.postgres_port, 
                                      database=config.postgres_db)
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
def get_access_token( client_id, client_secret, refresh_token):
    auth_url = "https://www.strava.com/oauth/token"
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': "refresh_token",
        'f': 'json'
    }
    response = requests.post(auth_url, data=payload, verify=False)
    access_token = response.json()['access_token']
    return access_token

@op
def fetch_strava_activities( access_token, athlete_id, config: StravaConfig):
    # First, get the last_activity_date for this athlete from the database
    connection = psycopg2.connect(user=config.postgres_user,
                                      password=config.postgres_password,
                                      host=config.postgres_host,
                                      port=config.postgres_port, 
                                      database=config.postgres_db)
    cursor = connection.cursor()

    # Query to get the last_activity_date for the given athlete_id
    cursor.execute("SELECT last_activity_date FROM athletes WHERE id = %s", (athlete_id,))
    result = cursor.fetchone()
    last_activity_date = result[0] if result else None

    cursor.close()
    connection.close()

    activities_url = "https://www.strava.com/api/v3/athlete/activities"
    # dt = int(datetime.datetime.strptime(config.date, ))
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {'per_page': 200, 'page': 1}
    
    # If there is a last_activity_date, set the 'after' parameter to fetch activities after this date
    if last_activity_date:
        start_date_unix = int(last_activity_date.timestamp())
        params['after'] = start_date_unix

    activities_response = requests.get(activities_url, headers=headers, params=params).json()
    return activities_response


@op
def get_latest_activity_date( config: StravaConfig):
    """
      Incrementally query the database for the most recent start_date of stored activities
    """ 
    connection = psycopg2.connect(user=config.postgres_user,
                                      password=config.postgres_password,
                                      host=config.postgres_host,
                                      port=config.postgres_port, 
                                      database=config.postgres_db)
    cursor = connection.cursor()

    cursor.execute("SELECT MAX(start_date) FROM activities")
    latest_start_date = cursor.fetchone()[0]

    cursor.close()
    connection.close()

    return latest_start_date


@op
def insert_into_database( activities_data, config: StravaConfig):
    # Database connection
    connection = psycopg2.connect(user=config.postgres_user,
                                      password=config.postgres_password,
                                      host=config.postgres_host,
                                      port=config.postgres_port, 
                                      database=config.postgres_db)
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
def process_athlete_data(context: OpExecutionContext, config: StravaConfig):
    context.log.info('Connecting to strava database')
    context.log.info('Creating strava database if it does not exist')
    create_strava_database()
    context.log.info('Creating activities table')
    create_activities_table()
    context.log.info('Creating athlete table')
    create_athlete_table()

# def process_athlete_data(client_id: int, client_secret: str, refresh_token: str):
    # Get the access token for athlete 1
    context.log.info('Getting access token for athlete 1')
    access_token = get_access_token(config.client_id, config.client_secret , config.refresh_token)
    # Get the date of the latest activity in the database
    context.log.info('Getting last activity date for athlete 1')
    latest_activity_date = get_latest_activity_date()

    # Fetch the athlete and activities data
    context.log.info('Extracting athlete data for athlete 1')
    athlete_data = fetch_athlete_data(access_token)
    context.log.info('Extracting activity data for athlete 1')
    activities_data = fetch_strava_activities(access_token, athlete_data['id'])
    # Insert the data into the database
    context.log.info('Inserting athelte data for athlete 1')
    insert_athlete_data(athlete_data, activities_data)
    context.log.info('Inserting activity data for athlete 1')
    insert_into_database(activities_data)

    # Get the access token for athlete 2
    context.log.info('Getting access token for athlete 2')
    access_token = get_access_token(config.client_id_2, config.client_secret_2 , config.refresh_token_2)

    # Get the date of the latest activity in the database
    context.log.info('Getting last activity date for athlete 2')
    latest_activity_date = get_latest_activity_date()

    # Fetch the athlete and activities data
    context.log.info('Extracting athlete data for athlete 2')
    athlete_data_2 = fetch_athlete_data(access_token)
    context.log.info('Extracting activity data for athlete 2')
    activities_data_2 = fetch_strava_activities(access_token, athlete_data_2['id'])
    # Insert the data into the database
    context.log.info('Inserting athelte data for athlete 2')
    insert_athlete_data(athlete_data_2, activities_data_2)
    context.log.info('Inserting activity data for athlete 2')
    insert_into_database(activities_data_2)
    print(athlete_data,athlete_data_2)
    return athlete_data
    
@op
def print_op(athlete_data):
    """Prints output of process_athlete_data"""
    print(athlete_data)