-- ============================================================================
-- RETENTION — which projects are STILL on-chain active, by name.
-- "Active" = at least one agent-wallet/builder-code tx in the last 30 days.
-- Shows the hackathon path so you can see who carried across hackathons.
-- Source: dune.celo.dataset_team_metrics (refreshed daily by the pipeline).
-- ============================================================================
SELECT
    team                         AS project,
    value_tier,
    n_hackathons,
    (n_hackathons > 1)           AS returned_across_hackathons,
    path                         AS hackathon_path,
    first_hackathon,
    last_hackathon,
    onchain_last_tx,
    onchain_txs_30d,
    tx                           AS total_tx,
    volume_usd,
    users
FROM dune.celo.dataset_team_metrics
WHERE still_onchain_active = true
ORDER BY onchain_txs_30d DESC, volume_usd DESC
