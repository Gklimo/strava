WITH athlete_data AS (
    SELECT
      a.athlete_id
    , a.first_name
    , a.last_name
    , a.full_name
    , a.username
    , a.city
    , a.state
    , a.country
    , a.sex
    , a.has_premium_subscription
    , a.summit_subscription
    , a.created_at
    , a.updated_at
    , a.badge_type_id
    , a.weight_kg
    , a.extracted_at
    FROM {{ ref('athletes') }} AS a
),

ranked_athletes AS (
    SELECT
      *
    , ROW_NUMBER() OVER (
        PARTITION BY athlete_id
        ORDER BY extracted_at DESC
      ) AS rank
    FROM athlete_data
)

SELECT
  athlete_id
, first_name
, last_name
, full_name
, username
, city
, state
, country
, sex
, has_premium_subscription
, summit_subscription
, created_at
, updated_at
, badge_type_id
, weight_kg
, extracted_at
    -- slowly changing dimention setup
, CASE WHEN rank = 1 THEN true ELSE false END AS is_current
, CASE WHEN rank = 1 THEN extracted_at ELSE LAG(extracted_at) OVER (PARTITION BY athlete_id ORDER BY extracted_at DESC) END AS valid_from_date
, CASE WHEN rank = 1 THEN NULL ELSE LEAD(extracted_at) OVER (PARTITION BY athlete_id ORDER BY extracted_at DESC) END AS valid_to_date
FROM ranked_athletes
