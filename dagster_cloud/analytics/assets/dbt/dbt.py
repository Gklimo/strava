import os
from pathlib import Path
from dagster_dbt import DbtCliResource, dbt_assets
from dagster import AssetExecutionContext

# step 1: configure dbt project resource
dbt_project_dir = Path(__file__).joinpath("..","..","..","..","dbt","strava").resolve()
dbt_strava_resource = DbtCliResource(project_dir=os.fspath(dbt_project_dir))

# step 2: generate manifest
dbt_manifest_path = (
    dbt_strava_resource.cli(
        ["--quiet", "parse"],
        target_path=Path("target"),
    )
    .wait()
    .target_path.joinpath("manifest.json")
)

# step 3: load manifest to produce asset definition
@dbt_assets(manifest=dbt_manifest_path)
def dbt_strava(context: AssetExecutionContext, dbt_strava_resource: DbtCliResource):
    yield from dbt_strava_resource.cli(["run"], context=context).stream()