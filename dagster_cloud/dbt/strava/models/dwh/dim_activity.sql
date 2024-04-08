WITH activities AS (
SELECT
  DISTINCT activity_type
FROM {{ ref('activities') }} 
WHERE activity_type IS NOT NULL
)

SELECT
  {{ dbt_utils.generate_surrogate_key(['activity_type']) }} AS activity_key
, activity_type AS type

FROM activities
