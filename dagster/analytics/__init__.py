from dagster import Definitions, EnvVar
from analytics.jobs import run_strava_etl
from analytics.resources import PostgresqlDatabaseResource
from analytics.schedules import strava_etl_schedule

defs = Definitions(
    jobs=[run_strava_etl],
    schedules=[strava_etl_schedule]
)
