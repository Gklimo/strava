WITH date_dimension AS (
    SELECT
        date_day,
        month_start_date,
        month_end_date
    FROM {{ ref('dim_date') }}
),

monthly_activities AS (
    SELECT
        a.athlete_id,
        dd.month_start_date AS month,
        COUNT(a.activity_id) AS total_activities,
        SUM(a.distance_m) AS total_distance,
        SUM(a.total_elevation_gain) AS total_elevation_gain
    FROM {{ ref('activities') }} a
    JOIN date_dimension dd ON DATE_TRUNC('month', a.start_date) = dd.date_day
    GROUP BY a.athlete_id, dd.month_start_date
),

ranked_activities AS (
    SELECT
        *,
        SUM(total_distance) OVER (
            PARTITION BY athlete_id ORDER BY month
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS running_total_distance,
        RANK() OVER (
            PARTITION BY athlete_id ORDER BY total_distance DESC
        ) AS distance_rank,
        AVG(total_distance) OVER (
            PARTITION BY athlete_id ORDER BY month
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS moving_avg_3m_distance
    FROM monthly_activities
),

scd_athlete_details AS (
    SELECT
        athlete_id,
        first_name,
        last_name,
        city,
        country,
        valid_from_date,
        valid_to_date
    FROM {{ ref('dim_athlete') }}  -- reference to SCD-enabled athlete dimension table
)

SELECT
    ra.athlete_id,
    ad.first_name,
    ad.last_name,
    ad.city,
    ad.country,
    ra.month,
    ra.total_activities,
    ra.total_distance,
    ra.total_elevation_gain,
    ra.running_total_distance,
    ra.distance_rank,
    ra.moving_avg_3m_distance
FROM ranked_activities ra
JOIN scd_athlete_details ad 
    ON ra.athlete_id = ad.athlete_id
JOIN date_dimension dd
    ON ra.month = dd.month_start_date
    AND dd.month_start_date >= ad.valid_from_date
    AND (dd.month_end_date <= ad.valid_to_date OR ad.valid_to_date IS NULL)
