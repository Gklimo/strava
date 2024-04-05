SELECT 
  id::INTEGER AS athlete_id
, LOWER(firstname) AS first_name
, LOWER(lastname) AS last_name
, LOWER(firstname) || ' ' || LOWER(lastname) AS full_name
, username
, city
, state
, country
, sex
, premium::BOOLEAN AS has_premium_subscription
, summit::BOOLEAN AS summit_subscription
, TO_TIMESTAMP(created_at) AS created_at
, TO_TIMESTAMP(updated_at) AS updated_at
, badge_type_id
, weight::INTEGER AS weight_kg
, TO_TIMESTAMP(_airbyte_extracted_at) AS extracted_at

FROM {{ source('strava', 'athletes') }}
