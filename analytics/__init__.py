from dagster import Definitions, EnvVar, load_assets_from_package_module
from analytics.jobs import run_strava_etl, run_strava_etl_full_load
from analytics.resources import PostgresqlDatabaseResource
from analytics.schedules import strava_etl_schedule
from analytics.assets import strava
from analytics.assets.airbyte.airbyte import airbyte_assets
from analytics.assets.dbt.dbt import dbt_strava, dbt_strava_resource

all_strava_assets = load_assets_from_package_module(strava, group_name='strava' )
defs = Definitions(
    assets=[*all_strava_assets, 
            airbyte_assets,
              dbt_strava ],
    jobs=[run_strava_etl,
          run_strava_etl_full_load
          ],
    schedules=[strava_etl_schedule], 
    resources={
        "postgres_conn": PostgresqlDatabaseResource(
            postgres_host=EnvVar("postgres_host"),
            postgres_db=EnvVar("postgres_db"),
            postgres_user=EnvVar("postgres_user"),
            postgres_password=EnvVar("postgres_password"),
            postgres_port=EnvVar("postgres_port")
        ),
        "dbt_strava_resource": dbt_strava_resource,
    }
)
