"""Fetch fresh on-chain metrics from Dune and write the 3 Watchtower CSVs.

Curated project metadata (use_case, milestones, descriptions, team identity) is passed through
from the committed seed; only tx / volume / users / recency / tiers are recomputed each run.
Outputs to out/ : team_metrics.csv, team_projects_final.csv, lena_worklist.csv
"""
import os, csv, math, json, argparse
from datetime import date
from collections import defaultdict

from . import handles as H
from . import queries as Q
from .dune_client import run_sql

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "out")


# ---- scoring -----------------------------------------------------------------
def tier(u, v, tx):
    if u >= 25 and v >= 1000: return "Production"
    if u >= 5 and v >= 50:    return "Traction"
    if tx > 0 or v > 0:       return "Demo"
    return "None"


def recency(ls, active, today):
    ls = (ls or "").strip()
    if ls:
        y, m, dd = map(int, ls[:10].split("-"))
        days = (today - date(y, m, dd)).days
        return 1.0 if days <= 30 else (0.0 if days >= 180 else 1 - (days - 30) / 150)
    return 1.0 if active else 0.3


def score(u, v, ls, active, today):
    return round(45 * min(1, math.log10(u + 1) / math.log10(1000))
                 + 40 * min(1, math.log10(v + 1) / math.log10(500000))
                 + 15 * recency(ls, active, today), 1)


def _rows(result):
    return result   # run_sql already returns list[dict]


def main(dry_run=False):
    today = date.today()
    cfg = H.load_config()
    projects = H.load_projects()
    h = H.build(cfg, projects)
    START = cfg.get("metrics_start", "2026-01-01")

    SEQ = {hk["id"]: hk["seq"] for hk in cfg["hackathons"]}
    NAME = {hk["id"]: hk["name"] for hk in cfg["hackathons"]}
    END = {hk["id"]: date.fromisoformat(hk["window"]["end"]) for hk in cfg["hackathons"]}
    TYPE = {hk["id"]: hk["type"] for hk in cfg["hackathons"]}
    LATEST = max(SEQ.values())

    # ---- run queries ----
    def step(label, sql):
        print(f"  running {label} ...", flush=True)
        return run_sql(sql)
    tx_rows = step("tx", Q.tx_sql(h, START))
    user_rows = step("users", Q.users_sql(h, START))
    vol_rows = step("volume", Q.volume_sql(h, START))
    status_rows = step("status", Q.status_sql(h, START))
    code_status = step("code_status", Q.code_status_sql(h)) if Q.code_status_sql(h) else []
    fee_rows = step("fees", Q.fees_sql(h)) if Q.fees_sql(h) else []

    pid_map = {int(p): v for p, v in h["pid_map"].items()}

    team_tx, proj_tx = {}, {}
    for r in tx_rows:
        if r["pid"] is None and r["team"] != "ALL":
            team_tx[r["team"]] = r["tx"] or 0
        elif r["pid"] is not None:
            proj_tx[pid_map[int(r["pid"])]] = r["tx"] or 0
    team_users, proj_users = {}, {}
    for r in user_rows:
        if r["pid"] is None and r["team"] != "ALL":
            team_users[r["team"]] = r["users"] or 0
        elif r["pid"] is not None:
            proj_users[pid_map[int(r["pid"])]] = r["users"] or 0
    team_vol = {r["team"]: (r["vol"] or 0) for r in vol_rows if r["team"] != "ALL"}
    wstat = {r["team"]: r for r in status_rows}
    crec = {r["code"]: r for r in code_status}
    cfee = {r["code"]: (r["fees"] or 0) for r in fee_rows}

    # ---- per-project rows ----
    tp_rows = []
    by_team = defaultdict(list)
    for p in projects:
        key = (p["team_id"], p["hackathon_id"], p["project_name"])
        m = p["meta"]
        t = TYPE[p["hackathon_id"]]
        ms = {"builder_code": "wallet+code", "erc8004": "agent-wallet",
              "project_submission": "source-tx"}[t]
        row = {
            "team_id": p["team_id"], "team": p["team_name"],
            "total_hackathons": m.get("total_hackathons", ""),
            "hackathon": NAME[p["hackathon_id"]], "seq": SEQ[p["hackathon_id"]],
            "project_name": p["project_name"], "use_case": p["use_case"],
            "tracks": m.get("tracks", ""), "status": m.get("status", ""),
            "score": m.get("score", ""), "tx_count": m.get("tx_count", ""),
            "dev_commits_mar": m.get("dev_commits_mar", ""), "dev_prs_mar": m.get("dev_prs_mar", ""),
            "milestones_done": m.get("milestones_done", ""), "milestones_total": m.get("milestones_total", ""),
            "url": p.get("github", ""), "description": m.get("description", ""),
            "uc_source": m.get("uc_source", ""),
            "tx": proj_tx.get(key, 0), "volume_usd": "", "users": proj_users.get(key, 0),
            "metric_source": ms if (key in proj_tx or key in proj_users) else "none",
        }
        tp_rows.append(row)
        by_team[p["team_id"]].append(p)

    # ---- team-level aggregation ----
    teams = []
    for tid, ps in by_team.items():
        hks = sorted({p["hackathon_id"] for p in ps}, key=lambda x: SEQ[x])
        last = hks[-1]
        nhk = len(hks)
        projnames = list(dict.fromkeys(p["project_name"] for p in ps))
        distinct_projects = len(set(projnames))
        use_cases = sorted({p["use_case"] for p in ps if p["use_case"] not in ("", "Unknown")})
        name = ps[0]["team_name"]
        last_seq = SEQ[last]
        status = ("Active-continued" if last_seq >= LATEST - 1 and nhk >= 2
                  else "Active-new" if last_seq >= LATEST - 1
                  else "Re-engage" if nhk >= 2 else "Dropped-once")
        gap = round((today - END[last]).days / 7, 1)
        serial = nhk >= 3 and distinct_projects >= nhk

        tx = team_tx.get(tid, 0)
        vol = team_vol.get(tid, 0.0)
        users = team_users.get(tid, 0)
        wallets = h["team_wallets"].get(tid, [])
        # recency: wallets (celo.transactions) + codes (daily code metric)
        lasts, txs30 = [], 0
        s = wstat.get(tid)
        if s:
            if s.get("last_tx"): lasts.append(s["last_tx"][:10])
            txs30 += s.get("txs_30d") or 0
        for c in h["team_codes"].get(tid, []):
            cr = crec.get(c)
            if cr:
                if cr.get("last_day"): lasts.append(cr["last_day"][:10])
                txs30 += int(cr.get("tx_30d") or 0)
        last_tx = max(lasts, default="")
        active = txs30 > 0
        teams.append({
            "team_id": tid, "team": name, "status": status,
            "value_tier": tier(users, vol, tx), "value_score": score(users, vol, last_tx, active, today),
            "serial_hopper": serial, "n_hackathons": nhk, "distinct_projects": distinct_projects,
            "use_cases": "; ".join(use_cases), "path": " -> ".join(NAME[x] for x in hks),
            "first_hackathon": NAME[hks[0]], "last_hackathon": NAME[last], "gap_weeks": gap,
            "still_onchain_active": active, "tx": tx, "volume_usd": round(vol, 2), "users": users,
            "onchain_txs_30d": txs30, "onchain_last_tx": last_tx, "n_wallets": len(wallets),
        })

    os.makedirs(OUT, exist_ok=True)
    tpcols = ["team_id", "team", "total_hackathons", "hackathon", "seq", "project_name", "use_case",
              "tracks", "status", "score", "tx_count", "dev_commits_mar", "dev_prs_mar",
              "milestones_done", "milestones_total", "url", "description", "uc_source",
              "tx", "volume_usd", "users", "metric_source"]
    tp_rows.sort(key=lambda r: (r["team_id"], r["seq"]))
    _write(os.path.join(OUT, "team_projects_final.csv"), tpcols, tp_rows)

    mcols = ["team_id", "team", "status", "value_tier", "value_score", "serial_hopper",
             "n_hackathons", "distinct_projects", "use_cases", "path", "first_hackathon",
             "last_hackathon", "gap_weeks", "still_onchain_active", "tx", "volume_usd", "users",
             "onchain_txs_30d", "onchain_last_tx", "n_wallets"]
    _write(os.path.join(OUT, "team_metrics.csv"), mcols, sorted(teams, key=lambda z: -z["volume_usd"]))

    wcols = ["team_id", "team", "status", "serial_hopper", "n_hackathons", "distinct_projects",
             "path", "first_hackathon", "last_hackathon", "gap_weeks", "onchain_last_tx",
             "onchain_txs_30d", "still_onchain_active", "n_wallets"]
    _write(os.path.join(OUT, "lena_worklist.csv"), wcols, sorted(teams, key=lambda z: z["team_id"]))

    grand_u = next((r["users"] for r in user_rows if r["team"] == "ALL" and r["pid"] is None), None)
    grand_v = next((r["vol"] for r in vol_rows if r["team"] == "ALL"), None)
    print(f"built {len(teams)} teams, {len(tp_rows)} project rows")
    print(f"headline distinct users={grand_u}  volume=${grand_v:,.0f}" if grand_u else "")
    return teams


def _write(path, cols, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in cols})


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    main(**vars(ap.parse_args()))
