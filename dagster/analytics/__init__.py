from dagster import Definitions, EnvVar
from analytics.jobs import run_strava_etl
# , run_strava_etl_2
from analytics.resources import PostgresqlDatabaseResource
from analytics.schedules import strava_etl_schedule
# , strava_etl_schedule_2

defs = Definitions(
    jobs=[run_strava_etl,
        #   run_strava_etl_2
          ],
    schedules=[strava_etl_schedule,
                # strava_etl_schedule_2
                ], 
    resources={
        "postgres_conn": PostgresqlDatabaseResource(
            postgres_host=EnvVar("postgres_host"),
            postgres_db=EnvVar("postgres_db"),
            postgres_user=EnvVar("postgres_user"),
            postgres_password=EnvVar("postgres_password"),
            postgres_port=EnvVar("postgres_port")
        )
    }
)
