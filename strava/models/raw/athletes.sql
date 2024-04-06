SELECT 
-- convert string fields to lowercase to standardize data, ensuring case-insensitive matching for joins.
  id::INTEGER AS athlete_id
, LOWER(firstname) AS first_name
, LOWER(lastname) AS last_name
, LOWER(firstname) || ' ' || LOWER(lastname) AS full_name
, username
, LOWER(city) AS city
, LOWER(state) AS state
, LOWER(country) AS country
, sex
, premium::BOOLEAN AS has_premium_subscription
, summit::BOOLEAN AS summit_subscription
, TO_TIMESTAMP(created_at) AS created_at
, TO_TIMESTAMP(updated_at) AS updated_at
, badge_type_id
, weight::INTEGER AS weight_kg
, TO_TIMESTAMP(_airbyte_extracted_at) AS extracted_at

FROM {{ source('strava', 'athletes') }}
