-- ============================================================================
-- Celo agent-hackathon WINNERS (static reference; append rows for new hackathons).
-- Ordered chronologically by seq (hackathon label is prefixed with its number too).
-- team_id joins to dune.celo.dataset_team_metrics / dataset_hackathon_team_projects.
-- NULL team_id = winner not resolvable in our project data (see note column).
-- ============================================================================
WITH winners (seq, hackathon, rank, project, team_id, award, placement, prize_usd, score, tx_30d_reported, note) AS (
  VALUES
  (1, '1. Agents for Real World v1', CAST(NULL AS integer), 'AutoClaw', 'T201', 'Main Track', '1st', 4000, CAST(NULL AS double), CAST(NULL AS integer), CAST(NULL AS varchar)),
  (1, '1. Agents for Real World v1', NULL, 'AgentHouse', NULL, 'Main Track', '2nd', 1000, NULL, NULL, 'unmatched in data'),
  (1, '1. Agents for Real World v1', NULL, 'Celo TrustAgent', 'T151', 'Infra', 'Winner', 1000, NULL, NULL, NULL),
  (1, '1. Agents for Real World v1', NULL, 'DenLabs', NULL, 'Infra', 'Winner', 1000, NULL, NULL, 'unmatched in data'),
  (3, '3. Proof of Ship AI Track', NULL, 'Esusu AI', 'T001', NULL, 'Winner', NULL, NULL, NULL, NULL),
  (3, '3. Proof of Ship AI Track', NULL, 'Tycoon', 'T007', NULL, 'Winner', NULL, NULL, NULL, NULL),
  (3, '3. Proof of Ship AI Track', NULL, 'GameArena / MARKOV-1', 'T034', NULL, 'Winner', NULL, NULL, NULL, NULL),
  (3, '3. Proof of Ship AI Track', NULL, 'Monipay', 'T035', NULL, 'Winner', NULL, NULL, NULL, NULL),
  (4, '4. AI Hackathon (Onchain)', 1, 'RemitRoute', 'T011', NULL, 'Rank 1', NULL, 8.4, 13, NULL),
  (4, '4. AI Hackathon (Onchain)', 2, 'AjoAI', 'T027', NULL, 'Rank 2', NULL, 8.1, 16, NULL),
  (4, '4. AI Hackathon (Onchain)', 3, 'Monipay', 'T035', NULL, 'Rank 3', NULL, 8.0, 703, NULL),
  (4, '4. AI Hackathon (Onchain)', 4, 'Pay For API', 'T193', NULL, 'Rank 4', NULL, 8.0, 3553, NULL),
  (4, '4. AI Hackathon (Onchain)', 5, 'Warrant', 'T055', NULL, 'Rank 5', NULL, 8.0, 10, NULL),
  (4, '4. AI Hackathon (Onchain)', 6, 'Celina', 'T046', NULL, 'Rank 6', NULL, 7.9, 125, NULL),
  (4, '4. AI Hackathon (Onchain)', 7, 'UtilityPay', NULL, NULL, 'Rank 7', NULL, 7.7, 148, 'team_id unverified'),
  (4, '4. AI Hackathon (Onchain)', 8, 'Sendease', NULL, NULL, 'Rank 8', NULL, 7.7, 90, 'unmatched in data'),
  (4, '4. AI Hackathon (Onchain)', 9, 'Cowry', NULL, NULL, 'Rank 9', NULL, 7.7, 73, 'team_id unverified'),
  (4, '4. AI Hackathon (Onchain)', 10, 'ChamaAgent', 'T184', NULL, 'Rank 10', NULL, 7.7, 25, NULL),
  (6, '6. Agentic Payments & DeFAI', NULL, 'Binary', 'T002', 'Track 1 - Most Revenue', '1st', 2000, NULL, NULL, NULL),
  (6, '6. Agentic Payments & DeFAI', NULL, 'UniAgent / AutoRange', 'T003', 'Track 1 - Most Revenue', '2nd', 1000, NULL, NULL, NULL),
  (6, '6. Agentic Payments & DeFAI', NULL, 'AbaPay', 'T005', 'Track 2 - Most x402', '1st', 700, NULL, NULL, NULL),
  (6, '6. Agentic Payments & DeFAI', NULL, 'RemitRoute', 'T011', 'Track 2 - Most x402', '2nd', 300, NULL, NULL, NULL),
  (6, '6. Agentic Payments & DeFAI', NULL, '(top reviewers pool)', NULL, 'Track 3 - Askbots', 'Pool', 500, NULL, NULL, 'split across top reviewers'),
  (6, '6. Agentic Payments & DeFAI', NULL, '(top 10 feedback authors)', NULL, 'Track 4 - Aigora', 'Pool', 500, NULL, NULL, '10 x $50'),
  (7, '7. Agents at Work', NULL, 'AbaPay', 'T005', 'Value Moved', '1st', 1500, NULL, NULL, NULL),
  (7, '7. Agents at Work', NULL, 'AbaPay', 'T005', 'Real World Adoption', 'Winner', 1000, NULL, NULL, NULL),
  (7, '7. Agents at Work', NULL, 'Binary', 'T002', 'Value Moved', 'Runner-up', 500, NULL, NULL, 'faucet-funded test play; recognised, not counted'),
  (7, '7. Agents at Work', NULL, 'Earmark', 'T078', 'Best Stablecoin Adoption', 'Winner', 150, NULL, NULL, NULL),
  (7, '7. Agents at Work', NULL, 'Tenda', 'T069', 'Best Stablecoin Adoption', 'Winner', 150, NULL, NULL, NULL),
  (7, '7. Agents at Work', NULL, 'CeloDesk', 'T059', 'Best Stablecoin Adoption', 'Winner', 150, NULL, NULL, NULL),
  (7, '7. Agents at Work', NULL, 'Compute Router', 'T102', 'Best Stablecoin Adoption', 'Winner', 150, NULL, NULL, NULL),
  (7, '7. Agents at Work', NULL, 'ThothPay', 'T107', 'Best Stablecoin Adoption', 'Winner', 150, NULL, NULL, NULL),
  (7, '7. Agents at Work', NULL, 'Sentry', 'T008', 'AskBots Growth 1', 'Winner', 300, NULL, NULL, NULL),
  (7, '7. Agents at Work', NULL, 'Providus', 'T080', 'AskBots Growth 2', 'Winner', 150, NULL, NULL, NULL),
  (7, '7. Agents at Work', NULL, 'Restwise', 'T054', 'AskBots Growth 3', 'Winner', 50, NULL, NULL, NULL),
  (7, '7. Agents at Work', NULL, 'Kobo', 'T010', 'Judges'' Favorite', 'Winner', 500, NULL, NULL, NULL),
  (7, '7. Agents at Work', NULL, 'Compute Router', 'T102', 'Judges'' Favorite', 'Honourable mention', NULL, NULL, NULL, NULL),
  (7, '7. Agents at Work', NULL, 'LexIQ', 'T079', 'Judges'' Favorite', 'Honourable mention', NULL, NULL, NULL, NULL),
  (7, '7. Agents at Work', NULL, 'Leash', 'T015', 'Judges'' Favorite', 'Honourable mention', NULL, NULL, NULL, NULL),
  (7, '7. Agents at Work', NULL, 'Restwise', 'T054', 'Buy Feedback', 'Winner', 50, NULL, NULL, NULL),
  (7, '7. Agents at Work', NULL, 'SUBI', 'T088', 'Buy Feedback', 'Winner', 50, NULL, NULL, NULL),
  (7, '7. Agents at Work', NULL, 'Cowrie', 'T072', 'Buy Feedback', 'Winner', 50, NULL, NULL, NULL),
  (7, '7. Agents at Work', NULL, 'Sharetopus', 'T126', 'Buy Feedback', 'Winner', 50, NULL, NULL, NULL),
  (7, '7. Agents at Work', NULL, 'Kobo', 'T010', 'Buy Feedback', 'Winner', 50, NULL, NULL, NULL)
)
SELECT seq, hackathon, rank, project, team_id, award, placement, prize_usd, score, tx_30d_reported, note
FROM winners
ORDER BY seq, COALESCE(rank, 999), prize_usd DESC NULLS LAST, project
