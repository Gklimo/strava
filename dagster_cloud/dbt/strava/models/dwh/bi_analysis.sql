SELECT 
  fact_activity.*
, dim_location.city AS activity_city
, dim_location.state AS activity_state
, dim_location.country AS activity_country
, full_name AS athlete_full_name
, dim_athlete.city AS athlete_city
, dim_athlete.country AS athlete_country
, sex
, has_premium_subscription
, created_at
, weight_kg
, dim_activity.type AS activity_type

from {{ ref('fact_activity') }} fact_activity 
left join {{ ref('dim_athlete') }} dim_athlete on fact_activity.athlete_id = dim_athlete.athlete_id
left join {{ ref('dim_location') }} dim_location on fact_activity.location_id = dim_location.location_key
left join {{ ref('dim_activity') }} dim_activity on fact_activity.activity_type_id = dim_activity.activity_key