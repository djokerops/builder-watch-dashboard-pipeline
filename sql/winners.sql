-- ============================================================================
-- Celo agent-hackathon WINNERS (static reference; append rows for new hackathons).
-- team_id joins to dune.celo.dataset_team_metrics / dataset_hackathon_team_projects.
-- NULL team_id = winner not resolvable in our project data (see note column).
-- ============================================================================
WITH winners (hackathon, seq, rank, project, team_id, award, placement, prize_usd, score, tx_30d_reported, note) AS (
  VALUES
  ('Agents for Real World v1', 1, CAST(NULL AS integer), 'AutoClaw', 'T201', 'Main Track', '1st', 4000, CAST(NULL AS double), CAST(NULL AS integer), CAST(NULL AS varchar)),
  ('Agents for Real World v1', 1, NULL, 'AgentHouse', NULL, 'Main Track', '2nd', 1000, NULL, NULL, 'unmatched in data'),
  ('Agents for Real World v1', 1, NULL, 'Celo TrustAgent', 'T151', 'Infra', 'Winner', 1000, NULL, NULL, NULL),
  ('Agents for Real World v1', 1, NULL, 'DenLabs', NULL, 'Infra', 'Winner', 1000, NULL, NULL, 'unmatched in data'),
  ('Proof of Ship AI Track', 3, NULL, 'Esusu AI', 'T001', NULL, 'Winner', NULL, NULL, NULL, NULL),
  ('Proof of Ship AI Track', 3, NULL, 'Tycoon', 'T007', NULL, 'Winner', NULL, NULL, NULL, NULL),
  ('Proof of Ship AI Track', 3, NULL, 'GameArena / MARKOV-1', 'T034', NULL, 'Winner', NULL, NULL, NULL, NULL),
  ('Proof of Ship AI Track', 3, NULL, 'Monipay', 'T035', NULL, 'Winner', NULL, NULL, NULL, NULL),
  ('AI Hackathon (Onchain)', 4, 1, 'RemitRoute', 'T011', NULL, 'Rank 1', NULL, 8.4, 13, NULL),
  ('AI Hackathon (Onchain)', 4, 2, 'AjoAI', 'T027', NULL, 'Rank 2', NULL, 8.1, 16, NULL),
  ('AI Hackathon (Onchain)', 4, 3, 'Monipay', 'T035', NULL, 'Rank 3', NULL, 8.0, 703, NULL),
  ('AI Hackathon (Onchain)', 4, 4, 'Pay For API', 'T193', NULL, 'Rank 4', NULL, 8.0, 3553, NULL),
  ('AI Hackathon (Onchain)', 4, 5, 'Warrant', 'T055', NULL, 'Rank 5', NULL, 8.0, 10, NULL),
  ('AI Hackathon (Onchain)', 4, 6, 'Celina', 'T046', NULL, 'Rank 6', NULL, 7.9, 125, NULL),
  ('AI Hackathon (Onchain)', 4, 7, 'UtilityPay', NULL, NULL, 'Rank 7', NULL, 7.7, 148, 'team_id unverified'),
  ('AI Hackathon (Onchain)', 4, 8, 'Sendease', NULL, NULL, 'Rank 8', NULL, 7.7, 90, 'unmatched in data'),
  ('AI Hackathon (Onchain)', 4, 9, 'Cowry', NULL, NULL, 'Rank 9', NULL, 7.7, 73, 'team_id unverified'),
  ('AI Hackathon (Onchain)', 4, 10, 'ChamaAgent', 'T184', NULL, 'Rank 10', NULL, 7.7, 25, NULL),
  ('Agentic Payments & DeFAI', 6, NULL, 'Binary', 'T002', 'Track 1 - Most Revenue', '1st', 2000, NULL, NULL, NULL),
  ('Agentic Payments & DeFAI', 6, NULL, 'UniAgent / AutoRange', 'T003', 'Track 1 - Most Revenue', '2nd', 1000, NULL, NULL, NULL),
  ('Agentic Payments & DeFAI', 6, NULL, 'AbaPay', 'T005', 'Track 2 - Most x402', '1st', 700, NULL, NULL, NULL),
  ('Agentic Payments & DeFAI', 6, NULL, 'RemitRoute', 'T011', 'Track 2 - Most x402', '2nd', 300, NULL, NULL, NULL),
  ('Agentic Payments & DeFAI', 6, NULL, '(top reviewers pool)', NULL, 'Track 3 - Askbots', 'Pool', 500, NULL, NULL, 'split across top reviewers'),
  ('Agentic Payments & DeFAI', 6, NULL, '(top 10 feedback authors)', NULL, 'Track 4 - Aigora', 'Pool', 500, NULL, NULL, '10 x $50'),
  ('Agents at Work', 7, NULL, 'AbaPay', 'T005', 'Value Moved', '1st', 1500, NULL, NULL, NULL),
  ('Agents at Work', 7, NULL, 'AbaPay', 'T005', 'Real World Adoption', 'Winner', 1000, NULL, NULL, NULL),
  ('Agents at Work', 7, NULL, 'Binary', 'T002', 'Value Moved', 'Runner-up', 500, NULL, NULL, 'faucet-funded test play; recognised, not counted'),
  ('Agents at Work', 7, NULL, 'Earmark', 'T078', 'Best Stablecoin Adoption', 'Winner', 150, NULL, NULL, NULL),
  ('Agents at Work', 7, NULL, 'Tenda', 'T069', 'Best Stablecoin Adoption', 'Winner', 150, NULL, NULL, NULL),
  ('Agents at Work', 7, NULL, 'CeloDesk', 'T059', 'Best Stablecoin Adoption', 'Winner', 150, NULL, NULL, NULL),
  ('Agents at Work', 7, NULL, 'Compute Router', 'T102', 'Best Stablecoin Adoption', 'Winner', 150, NULL, NULL, NULL),
  ('Agents at Work', 7, NULL, 'ThothPay', 'T107', 'Best Stablecoin Adoption', 'Winner', 150, NULL, NULL, NULL),
  ('Agents at Work', 7, NULL, 'Sentry', 'T008', 'AskBots Growth 1', 'Winner', 300, NULL, NULL, NULL),
  ('Agents at Work', 7, NULL, 'Providus', 'T080', 'AskBots Growth 2', 'Winner', 150, NULL, NULL, NULL),
  ('Agents at Work', 7, NULL, 'Restwise', 'T054', 'AskBots Growth 3', 'Winner', 50, NULL, NULL, NULL),
  ('Agents at Work', 7, NULL, 'Kobo', 'T010', 'Judges'' Favorite', 'Winner', 500, NULL, NULL, NULL),
  ('Agents at Work', 7, NULL, 'Compute Router', 'T102', 'Judges'' Favorite', 'Honourable mention', NULL, NULL, NULL, NULL),
  ('Agents at Work', 7, NULL, 'LexIQ', 'T079', 'Judges'' Favorite', 'Honourable mention', NULL, NULL, NULL, NULL),
  ('Agents at Work', 7, NULL, 'Leash', 'T015', 'Judges'' Favorite', 'Honourable mention', NULL, NULL, NULL, NULL),
  ('Agents at Work', 7, NULL, 'Restwise', 'T054', 'Buy Feedback', 'Winner', 50, NULL, NULL, NULL),
  ('Agents at Work', 7, NULL, 'SUBI', 'T088', 'Buy Feedback', 'Winner', 50, NULL, NULL, NULL),
  ('Agents at Work', 7, NULL, 'Cowrie', 'T072', 'Buy Feedback', 'Winner', 50, NULL, NULL, NULL),
  ('Agents at Work', 7, NULL, 'Sharetopus', 'T126', 'Buy Feedback', 'Winner', 50, NULL, NULL, NULL),
  ('Agents at Work', 7, NULL, 'Kobo', 'T010', 'Buy Feedback', 'Winner', 50, NULL, NULL, NULL)
)
SELECT hackathon, rank, project, team_id, award, placement, prize_usd, score, tx_30d_reported, note
FROM winners
ORDER BY seq, COALESCE(rank, 999), prize_usd DESC NULLS LAST, project
