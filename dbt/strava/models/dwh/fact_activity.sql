SELECT
  {{ dbt_utils.generate_surrogate_key(['activity_id']) }} AS activity_key
, {{ dbt_utils.star(from=ref('activities'), relation_alias='activities', except=["workout_type","sport_type","activity_type","start_latlng","end_latlng","location_city","location_country","location_state"]) }}
, PARSE_JSON(start_latlng)[0]::FLOAT AS start_latitude
, PARSE_JSON(start_latlng)[1]::FLOAT AS start_longitude
, PARSE_JSON(end_latlng)[0]::FLOAT AS end_latitude
, PARSE_JSON(end_latlng)[1]::FLOAT AS end_longitude
, dim_location.location_key AS location_id
, dim_activity.activity_key AS activity_type_id

FROM {{ ref('activities') }} activities
LEFT JOIN {{ ref('dim_location') }} dim_location ON activities.location_country = dim_location.country
    AND COALESCE(activities.location_state, '') = COALESCE(dim_location.state, '')
    AND COALESCE(activities.location_country, '') = COALESCE(dim_location.country, '')
LEFT JOIN {{ ref('dim_activity') }} dim_activity ON activities.activity_type = dim_activity.type
LEFT JOIN {{ ref('dim_athlete') }} dim_athlete
    ON activities.athlete_id = dim_athlete.athlete_id
    AND activities.start_date::DATE BETWEEN dim_athlete.valid_from_date AND COALESCE(dim_athlete.valid_to_date, CURRENT_DATE)