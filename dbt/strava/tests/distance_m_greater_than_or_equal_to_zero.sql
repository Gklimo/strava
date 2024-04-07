/*
  Test: Ensure Non-negative Distances in Activities
  Description: This test is designed to verify that all entries in the 'activities' model
  have non-negative values in the 'distance_m' column. Negative distances are not expected
  and might indicate data entry errors or issues in data processing pipelines. Records found
  to violate this condition should be reviewed for accuracy and corrected as needed.
*/

SELECT
    activity_id,
    distance_m
FROM {{ ref('activities') }}
WHERE distance_m < 0
