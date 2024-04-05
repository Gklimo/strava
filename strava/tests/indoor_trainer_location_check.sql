/*
  Custom dbt test: Indoor Trainer Elevation Gain Check
  This test checks for records in the 'activities' table where the activity is marked as indoor training (is_indoor_trainer = true).
  The test ensures that all such indoor training activities have a total elevation gain of 0.
  The expectation is that indoor activities should not record any elevation gain.
  If any indoor training activities have a non-zero elevation gain, this test will fail, indicating data inconsistency.
*/

SELECT *
FROM {{ ref('activities') }}
WHERE is_indoor_trainer
  AND total_elevation_gain != 0
