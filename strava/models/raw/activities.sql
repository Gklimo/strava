SELECT 
  id::INTEGER AS activity_id
, lower(name) AS activity_name
, lower(type) AS activity_type
, manual::BOOLEAN AS is_manual_input
, map_id
, commute::BOOLEAN AS is_commute
, flagged::BOOLEAN AS is_flagged
, gear_id
, private::BOOLEAN AS is_private
, trainer::BOOLEAN AS is_indoor_trainer
, distance::FLOAT AS distance_m
, elev_low::FLOAT AS lowest_elevation
, pr_count::INTEGER AS pr_count
, timezone
, elev_high::FLOAT AS highest_elevation
, max_speed::FLOAT AS max_speed_ms
, upload_id::INTEGER AS upload_id
, athlete_id::INTEGER AS athlete_id
, lower(sport_type) AS sport_type
, TO_TIMESTAMP(start_date) AS start_date
, utc_offset::INTEGER AS utc_offset
, visibility
, external_id
, kudos_count::INTEGER AS kudos_count
, moving_time::INTEGER AS moving_time_s
, photo_count::INTEGER AS photo_count
, average_temp::INTEGER AS average_temp
, elapsed_time::INTEGER AS elapsed_time_s
, PARSE_JSON(start_latlng) AS start_latlng
, PARSE_JSON(end_latlng) AS end_latlng
, workout_type
, athlete_count::INTEGER AS athlete_count
, average_speed::FLOAT AS avg_speed_ms
, comment_count::INTEGER AS comment_count
, has_heartrate::BOOLEAN AS has_heartrate
, lower(location_city) AS location_city
, max_heartrate::INTEGER AS max_heartrate
, lower(location_state) AS location_state
, average_cadence::FLOAT AS average_cadence
, lower(location_country) AS location_country
, TO_TIMESTAMP(start_date_local) AS start_date_local
, achievement_count::INTEGER AS achievement_count
, average_heartrate::FLOAT AS average_heartrate
, total_photo_count::INTEGER AS total_photo_count
, total_elevation_gain::INTEGER AS total_elevation_gain
, to_timestamp(_airbyte_extracted_at) AS extracted_at

FROM {{ source('strava', 'activities') }}
