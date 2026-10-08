"""Generate the on-chain metric SQL from the handle maps.

All metrics use the Builder Watchtower basis: agent wallet (sender OR recipient) UNION
builder-code, deduplicated -- tx by hash, volume by transfer unique_key, users by payer.
tx and users return project + team + grand ('ALL') rows via GROUPING SETS; volume is team
+ grand. Grand rows are program-wide DISTINCT totals, not a sum of the team rows.
"""
ZERO = "0x0000000000000000000000000000000000000000"


def _pwv(triples):   # (pid, team, wallet) -> VALUES
    return ",".join(f"({p},'{t}',0x{w})" for p, t, w in triples)


def _pcv(triples):   # (pid, team, code) -> VALUES
    return ",".join(f"({p},'{t}','{c}')" for p, t, c in triples)


def _team_wv(team_wallets):
    return ",".join(f"('{t}',0x{w})" for t, ws in team_wallets.items() for w in ws)


def _team_cv(team_codes):
    return ",".join(f"('{t}','{c}')" for t, cs in team_codes.items() for c in cs)


def tx_sql(h, start="2026-01-01"):
    return f"""WITH wmap(pid,team,wallet) AS (VALUES {_pwv(h['proj_wallet_pairs'])}),
cmap(pid,team,code) AS (VALUES {_pcv(h['proj_code_pairs'])}),
txu AS (
  SELECT m.pid, m.team, t.hash AS h FROM celo.transactions t JOIN wmap m ON t."from"=m.wallet WHERE t.block_date>=DATE '{start}'
  UNION ALL
  SELECT m.pid, m.team, t.hash FROM celo.transactions t JOIN wmap m ON t.to=m.wallet WHERE t.block_date>=DATE '{start}'
  UNION ALL
  SELECT m.pid, m.team, t.hash FROM dune.celo.transactions_attributed t JOIN cmap m ON contains(split(t.multi_code,','),m.code) WHERE t.block_date>=DATE '{start}'
)
SELECT CAST(pid AS varchar) AS pid, COALESCE(team,'ALL') AS team, count(DISTINCT h) AS tx
FROM txu GROUP BY GROUPING SETS ((pid,team),(team),())"""


def users_sql(h, start="2026-01-01"):
    allw = ",".join("0x" + w for w in h["all_wallets"])
    return f"""WITH wmap(pid,team,wallet) AS (VALUES {_pwv(h['proj_wallet_pairs'])}),
cmap(pid,team,code) AS (VALUES {_pcv(h['proj_code_pairs'])}),
allw(wallet) AS (VALUES {allw}),
payers AS (
  SELECT m.pid, m.team, t."from" AS u FROM tokens_celo.transfers t JOIN wmap m ON t.to=m.wallet
    WHERE t.block_date>=DATE '{start}' AND t."from" NOT IN (SELECT wallet FROM allw) AND t."from" != {ZERO}
  UNION ALL
  SELECT m.pid, m.team, t."from" FROM dune.celo.transactions_attributed t JOIN cmap m ON contains(split(t.multi_code,','),m.code)
    WHERE t.block_date>=DATE '{start}'
)
SELECT CAST(pid AS varchar) AS pid, COALESCE(team,'ALL') AS team, count(DISTINCT u) AS users
FROM payers GROUP BY GROUPING SETS ((pid,team),(team),())"""


def volume_sql(h, start="2026-01-01"):
    """Team + grand volume (distinct transfers by unique_key). Split joins avoid a slow OR."""
    return f"""WITH wmap(team,wallet) AS (VALUES {_team_wv(h['team_wallets'])}),
cmap(team,code) AS (VALUES {_team_cv(h['team_codes'])}),
tagged AS (
  SELECT m.team, t.unique_key AS uk, t.amount_usd AS amt FROM tokens_celo.transfers t JOIN wmap m ON t."from"=m.wallet WHERE t.block_date>=DATE '{start}'
  UNION ALL
  SELECT m.team, t.unique_key, t.amount_usd FROM tokens_celo.transfers t JOIN wmap m ON t.to=m.wallet WHERE t.block_date>=DATE '{start}'
  UNION ALL
  SELECT m.team, t.unique_key, t.amount_usd FROM dune.celo.transfers_attributed t JOIN cmap m ON contains(split(t.multi_code,','),m.code) WHERE t.block_date>=DATE '{start}'
),
teamv AS (SELECT team, uk, max(amt) AS amt FROM tagged GROUP BY team, uk),
grand AS (SELECT uk, max(amt) AS amt FROM tagged GROUP BY uk)
SELECT team, round(sum(amt),2) AS vol FROM teamv GROUP BY team
UNION ALL SELECT 'ALL', round(sum(amt),2) FROM grand"""


def status_sql(h, start="2026-01-01"):
    """Per-team wallet recency: last tx date and tx count in the last 30 days."""
    return f"""WITH wmap(team,wallet) AS (VALUES {_team_wv(h['team_wallets'])}),
tx AS (
  SELECT m.team, t.block_date AS d FROM celo.transactions t JOIN wmap m ON t."from"=m.wallet WHERE t.block_date>=DATE '{start}'
  UNION ALL
  SELECT m.team, t.block_date FROM celo.transactions t JOIN wmap m ON t.to=m.wallet WHERE t.block_date>=DATE '{start}'
)
SELECT team, CAST(max(d) AS varchar) AS last_tx,
       count_if(d >= date_add('day', -30, current_date)) AS txs_30d
FROM tx GROUP BY team"""


def code_status_sql(h):
    codes = ",".join("'" + c + "'" for c in h["all_codes"])
    if not codes:
        return None
    return f"""SELECT builder_code AS code, CAST(max(day) AS varchar) AS last_day,
       coalesce(sum(CASE WHEN day >= date_add('day', -30, current_timestamp) THEN tx_count END),0) AS tx_30d
FROM dune.celo.agent_daily_code_metric WHERE on_allowlist AND builder_code IN ({codes}) GROUP BY 1"""


def fees_sql(h):
    codes = ",".join("'" + c + "'" for c in h["all_codes"])
    if not codes:
        return None
    return f"""SELECT builder_code AS code, round(sum(chain_fees_usd),2) AS fees
FROM dune.celo.agent_daily_code_metric WHERE on_allowlist AND builder_code IN ({codes}) GROUP BY 1"""
