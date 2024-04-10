from dagster import EnvVar, AutoMaterializePolicy, FreshnessPolicy
from dagster_airbyte import AirbyteResource, load_assets_from_airbyte_instance

airbyte_resource = AirbyteResource(
    host=EnvVar("airbyte_host"),
    port=EnvVar("airbyte_port"),
    username=EnvVar("airbyte_username"),
    password=EnvVar("airbyte_password")
)
# Data is considered fresh if updated within the past 24 hours
airbyte_assets = load_assets_from_airbyte_instance(
    airbyte_resource,
    key_prefix="strava",
    connection_to_freshness_policy_fn=lambda _: FreshnessPolicy(maximum_lag_minutes=1440),
    connection_to_auto_materialize_policy_fn=lambda _: AutoMaterializePolicy.eager(),
)
