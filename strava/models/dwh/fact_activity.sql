SELECT
  {{ dbt_utils.generate_surrogate_key(['activity_id']) }} AS activity_key
, {{ dbt_utils.star(from=ref('activities'), relation_alias='activities', except=["start_latlng","end_latlng","location_city","location_country","location_state"]) }}
, PARSE_JSON(start_latlng)[0]::FLOAT AS start_latitude
, PARSE_JSON(start_latlng)[1]::FLOAT AS start_longitude
, PARSE_JSON(end_latlng)[0]::FLOAT AS end_latitude
, PARSE_JSON(end_latlng)[1]::FLOAT AS end_longitude
, dim_location.location_key AS location_id

FROM {{ ref('activities') }} activities
LEFT JOIN {{ ref('dim_location') }} dim_location ON activities.location_city = dim_location.city
    AND activities.location_state = dim_location.state
    AND activities.location_country = dim_location.country
LEFT JOIN {{ ref('dim_athlete') }} dim_athlete
    ON activities.athlete_id = dim_athlete.athlete_id
    AND activities.start_date::DATE BETWEEN dim_athlete.valid_from_date AND COALESCE(dim_athlete.valid_to_date, CURRENT_DATE)

-- Define foreign key constraint
-- ALTER TABLE fact_activity
-- ADD CONSTRAINT fk_athlete_id FOREIGN KEY (athlete_id) REFERENCES dim_athlete (athlete_id);
-- ALTER TABLE fact_activity
-- ADD CONSTRAINT fk_location_id FOREIGN KEY (location_id) REFERENCES dim_location (location_id);