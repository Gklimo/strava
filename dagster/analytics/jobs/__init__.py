from dagster import job, daily_partitioned_config
from analytics.ops.strava import create_strava_database, create_athlete_table, get_access_token, extract_athlete_data, load_athlete_data, create_activities_table, extract_strava_activities, load_into_database, print_op, get_access_token_2
from datetime import datetime

# @daily_partitioned_config(strat_date)

# @job()
# def run_strava_etl():

#     process_athlete_data()


@job()
def run_strava_etl():
    create_strava_database()
    create_athlete_table()
    create_activities_table()
    # athlete 1
    access_token = get_access_token()
    athlete_data = extract_athlete_data(access_token)
    activity_data = extract_strava_activities(access_token, athlete_data)
    load_activity = load_into_database(activity_data)
    load_athlete= load_athlete_data(athlete_data, activity_data)
    printout = print_op(athlete_data, activity_data)

    # athlete 2
    access_token_2= get_access_token_2()
    athlete_data_2 = extract_athlete_data(access_token_2)
    activity_data_2 = extract_strava_activities(access_token_2, athlete_data_2)
    load_activity_2 = load_into_database(activity_data_2)
    load_athlete_2= load_athlete_data(athlete_data_2, activity_data_2)
    printout_2 = print_op(athlete_data_2, activity_data_2)
