WITH locations AS (
SELECT
  DISTINCT location_city
, location_state
, location_country
FROM {{ ref('activities') }} 
WHERE location_city IS NOT NULL OR location_state IS NOT NULL OR location_country IS NOT NULL

UNION

SELECT
  DISTINCT city
, state
, country
FROM {{ ref('athletes') }} 
WHERE city IS NOT NULL OR state IS NOT NULL OR country IS NOT NULL
)

SELECT
  {{ dbt_utils.generate_surrogate_key(['location_city','location_state','location_country']) }} AS location_key
, location_city AS city
, location_state AS state
, location_country AS country
FROM locations
