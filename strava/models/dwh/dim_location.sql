{{ config(materialized='table') }}
WITH locations AS (
SELECT
  DISTINCT location_city
, location_state
, location_country
FROM {{ ref('activities') }} 
WHERE location_city IS NOT NULL AND location_state IS NOT NULL AND location_country IS NOT NULL

UNION

SELECT
  DISTINCT city
, state
, country
FROM {{ ref('athletes') }} 
WHERE city IS NOT NULL AND state IS NOT NULL AND country IS NOT NULL
)

SELECT
  {{ dbt_utils.generate_surrogate_key(['location_city','location_state','location_country']) }} AS location_key
, location_city AS city
, location_state AS state
, location_country AS country
FROM locations

-- Define primary key constraint
-- ALTER TABLE dim_location
-- ADD PRIMARY KEY (location_id);