-- ============================================================================
-- TRANSACTIONS per HACKATHON and per TRACK — which models & tracks performed.
-- Tracks exist only for DeFAI, Agents at Work and Synthesis; the others show
-- only their hackathon-total line.
-- NOTE: tracks are multi-valued. A project entered in several tracks counts
-- toward EACH, so track rows OVERLAP and exceed the hackathon total. Use them
-- for relative comparison, not as a partition. (These per-project tx are a
-- comparison metric; the deduped headline tx lives in the overview query.)
-- Source: dune.celo.dataset_hackathon_team_projects.
-- ============================================================================
WITH proj AS (
    SELECT hackathon, min(seq) OVER (PARTITION BY hackathon) AS seq, tracks, tx, users
    FROM dune.celo.dataset_hackathon_team_projects
),
hk AS (   -- one hackathon-total line per hackathon (all projects)
    SELECT seq, hackathon, '— hackathon total —' AS track,
           count(*) AS projects, sum(tx) AS tx, sum(users) AS users
    FROM proj GROUP BY seq, hackathon
),
exploded AS (
    SELECT seq, hackathon, trim(t) AS track, tx, users
    FROM proj CROSS JOIN UNNEST(split(tracks, ',')) AS x(t)
    WHERE tracks <> '' AND trim(t) <> ''
),
tr AS (   -- per-track breakdown (where tracks exist)
    SELECT seq, hackathon, track,
           count(*) AS projects, sum(tx) AS tx, sum(users) AS users
    FROM exploded GROUP BY seq, hackathon, track
)
SELECT seq, hackathon, track, projects, tx, users,
       CAST(round(1.0 * tx / nullif(projects, 0)) AS integer) AS tx_per_project
FROM (SELECT * FROM hk UNION ALL SELECT * FROM tr)
ORDER BY seq, (track = '— hackathon total —') DESC, tx DESC
