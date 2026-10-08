# Celo Agent-Hackathon Watchtower — data pipeline

Rebuilds the Builder Watchtower tables from fresh on-chain data every day and uploads them to
Dune, replacing the existing `dataset_*` tables.

| Output CSV | Upload name | Live Dune table | Grain |
|---|---|---|---|
| `team_metrics.csv` | `team_metrics` | `dune.celo.dataset_team_metrics` | one row per team (tx, volume, users, tier, score, recency) |
| `team_projects_final.csv` | `hackathon_team_projects` | `dune.celo.dataset_hackathon_team_projects` | one row per project (metadata + per-project tx/users) |
| `lena_worklist.csv` | `team_worklist` | `dune.celo.dataset_team_worklist` | one row per team (re-engagement worklist) |
| `headline_totals.csv` | `headline_totals` | `dune.celo.dataset_headline_totals` | **one row**: program-wide distinct users / tx / volume / fees + team & tier counts |

> Dune prepends `dataset_` to the upload name automatically (verified via the API), so the
> config holds upload names **without** that prefix.

## Metric definitions (all wallet ∪ code, deduped)

- **tx** — distinct tx hashes where an agent wallet is sender or recipient, UNION builder-code-tagged txs.
- **volume** — `sum(amount_usd)` over distinct transfers (`unique_key`), agent wallet ∪ code.
- **users** — distinct external payers: inbound to an agent wallet (excluding other agent wallets), UNION code-tagged senders.
- **fees** — `chain_fees_usd` from the daily code metric (builder-code hackathons only).
- Developer payout wallets (Real World `recipient`/`payout`) are **not** agent wallets and are excluded everywhere.
- A handle shared across teams is **owned once** (count-once), so nothing double-counts across teams.
- All cumulative metrics use one lower bound, `metrics_start` in the config (default `2026-01-01`).

### The headline KPIs come from `headline_totals`, NOT from `SUM(team_metrics)`
Per-team counts can't be summed — a user/tx touching two teams is in both rows. Point the
distinct users / tx / volume KPI cards at the one-row `dataset_headline_totals` table, which the
pipeline refreshes daily.

## What refreshes vs. what's fixed

- **Daily (automated):** on-chain metrics — tx, volume, users, fees, recency, tiers, scores, headline.
- **Committed seed (`data/`):** resolved project list + curated metadata (use_case, descriptions)
  + `team_registry.json` (stable `team_id`s). A rebuild never renumbers teams.

## Layout

```
config/hackathons.yml     # the hackathon registry + metrics_start + upload table names
data/projects.json        # committed seed: one entry per project + curated meta + handles
data/team_registry.json   # stable team_id -> name + handles, for matching future submissions
pipeline/handles.py       # count-once agent-handle resolution from config + seed
pipeline/queries.py       # generates the on-chain metric SQL from the handle maps
pipeline/dune_client.py   # Dune API: run SQL (create→execute→results), upload CSV
pipeline/build.py         # fetch metrics -> write the 4 CSVs to out/
pipeline/upload.py        # upload out/*.csv to Dune (replace tables)
pipeline/run.py           # daily entrypoint (build + upload)
pipeline/add_hackathon.py # load a new hackathon's submissions into the seed
.github/workflows/daily.yml
```

## Run locally

```bash
pip install -r requirements.txt
export DUNE_API_KEY=...            # or rely on ~/.config/dune/config.yaml
python -m pipeline.run --no-upload # build CSVs into out/ without uploading
python -m pipeline.run             # build + upload to Dune
```

## Add a new hackathon

1. Add a block to `config/hackathons.yml` (set `id`, `seq`, `name`, `window`, `type`, source table/columns).
   - `project_submission` — self-reported table (project + github + tx column).
   - `erc8004` — curated `agent_ids` list; wallet from `dataset_agents.agentwallet`.
   - `builder_code` — allowlist table with `code`, `wallet`, `team` (+ optional `other_wallets`).
2. `python -m pipeline.add_hackathon <id>` — pulls its submissions, matches to existing teams by
   shared wallet/code (else name), mints new `team_id`s only for genuinely new teams.
3. Fill in `use_case` for the new rows in `data/projects.json` (left blank by the loader), then commit `data/`.

## CI setup

Add repo secret **`DUNE_API_KEY`**. The workflow (`.github/workflows/daily.yml`) runs daily at
06:17 UTC and on manual dispatch; it also attaches the generated CSVs as run artifacts.
