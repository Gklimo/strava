from dagster import job, daily_partitioned_config
from analytics.ops.strava import create_strava_database, create_athlete_table, get_access_token, extract_athlete_data, load_athlete_data, create_activities_table, extract_strava_activities, load_into_database, print_op, get_access_token_2
from datetime import datetime

from dagster import daily_partitioned_config
from datetime import datetime

@daily_partitioned_config(start_date=datetime(2014, 1, 1))
def strava_etl_daily_partition(start: datetime, _end: datetime):
    # Format the start date as a string in 'YYYY-MM-DD' format
    formatted_date = start.strftime("%Y-%m-%d")

    # Return a config dictionary where the 'date' for each operation is set to the formatted start date
    return {
        "ops": {
            "extract_strava_activities": 
                {"config": {
                    "date": formatted_date
                }
            },
            "extract_strava_activities_2": 
                {"config": {
                    "date": formatted_date
                }
            },
            "get_access_token": 
                {"config": {
                    "date": formatted_date
                }
            },
            "get_access_token_2": {
                "config": {
                    "date": formatted_date
                }
            },
        }
    }

@job(config=strava_etl_daily_partition)
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

# @job(config=strava_etl_daily_partition)
# # athlete 2
# def run_strava_etl_2():
#     create_strava_database()
#     create_athlete_table()
#     create_activities_table()
#     access_token_2= get_access_token_2()
#     athlete_data_2 = extract_athlete_data(access_token_2)
#     activity_data_2 = extract_strava_activities(access_token_2, athlete_data_2)
#     load_activity_2 = load_into_database(activity_data_2)
#     load_athlete_2= load_athlete_data(athlete_data_2, activity_data_2)
#     printout_2 = print_op(athlete_data_2, activity_data_2)
