from dagster import ScheduleDefinition, build_schedule_from_partitioned_job

from analytics.jobs import run_strava_etl
# , run_strava_etl_2
# Every minute 
# strava_etl_schedule = ScheduleDefinition(job=run_strava_etl, cron_schedule="* * * * *")
# Every hour at minute 0
# strava_etl_schedule = ScheduleDefinition(job=run_strava_etl, cron_schedule="0 * * * *")

# Daily schedule with partitions
strava_etl_schedule = build_schedule_from_partitioned_job(job=run_strava_etl)
# strava_etl_schedule_2 = build_schedule_from_partitioned_job(job=run_strava_etl_2)