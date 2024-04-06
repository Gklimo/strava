from dagster import job, op
from analytics.ops.strava import process_athlete_data

@job()
def run_strava_etl():

    process_athlete_data()
