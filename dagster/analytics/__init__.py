from dagster import Definitions, EnvVar, load_assets_from_package_module
from analytics.jobs import run_strava_etl
from analytics.resources import PostgresqlDatabaseResource
from analytics.schedules import strava_etl_schedule
from analytics.assets import strava

all_strava_assets = load_assets_from_package_module(strava, group_name='strava' )
defs = Definitions(
    assets=[*all_strava_assets],
    jobs=[run_strava_etl],
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
