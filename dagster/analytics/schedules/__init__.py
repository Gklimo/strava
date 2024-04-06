from dagster import ScheduleDefinition

from analytics.jobs import run_strava_etl
# Every day every hour at minute 0
strava_etl_schedule = ScheduleDefinition(job=run_strava_etl, cron_schedule="0 * * * *")
