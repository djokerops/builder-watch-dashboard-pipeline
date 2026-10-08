"""Load a new hackathon's submissions into the committed seed, keeping team_ids stable.

Usage:  python -m pipeline.add_hackathon <hackathon_id>     (id must already exist in config/hackathons.yml)

It pulls the hackathon's rows from its Dune source table, turns each into a project, matches
it to an existing team (shared wallet/code, else normalised name), and only mints a NEW
team_id for genuinely new teams. Appends to data/projects.json and updates data/team_registry.json.
Review the diff before committing.
"""
import os, re, json, sys
from . import handles as H
from .dune_client import run_sql

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(HERE, "data")
EX_SUFFIX = {"0000000000000000000000000000000000000000", "8004a169fb4a3325136eb29fa0ceb6d2e539a432"}


def norm(s):
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())


def wnorm(w):
    m = re.search(r"([0-9a-f]{40})", (w or "").lower())
    w = m.group(1) if m else ""
    return "" if w in EX_SUFFIX else w


def _fetch_rows(hk):
    t = hk["type"]
    if t == "project_submission":
        c = hk["columns"]
        rows = run_sql(f"SELECT {c['project']} AS project, {c['github']} AS github FROM {hk['table']}")
        return [{"project": r["project"], "team_name": r["project"], "github": r.get("github") or "",
                 "code": "", "wallets": []} for r in rows if r.get("project")]
    if t == "erc8004":
        ids = ",".join(str(i) for i in hk["agent_ids"])
        rows = run_sql(f"SELECT agentname, agentwallet FROM {hk['registry_table']} "
                       f"WHERE CAST(agentid AS bigint) IN ({ids})")
        out = []
        for r in rows:
            w = wnorm(str(r.get("agentwallet") or ""))
            out.append({"project": r.get("agentname") or "", "team_name": r.get("agentname") or "",
                        "github": "", "code": "", "wallets": [w] if w else []})
        return out
    if t == "builder_code":
        c = hk["columns"]
        cols = [f"{c['code']} AS code", f"{c['wallet']} AS wallet", f"{c['team']} AS team",
                f"{c.get('github', 'NULL')} AS github"]
        if "other_wallets" in c:
            cols.append(f"{c['other_wallets']} AS other_wallets")
        if "project" in c:
            cols.append(f"{c['project']} AS project")
        rows = run_sql(f"SELECT {', '.join(cols)} FROM {hk['table']}")
        out = []
        for r in rows:
            ws = [wnorm(str(r.get("wallet") or ""))]
            for x in re.split(r"[,\s]+", str(r.get("other_wallets") or "")):
                ws.append(wnorm(x))
            out.append({"project": r.get("project") or r.get("team") or "",
                        "team_name": r.get("team") or "", "github": r.get("github") or "",
                        "code": (r.get("code") or "").strip(), "wallets": [w for w in ws if w]})
        return out
    raise SystemExit(f"unknown hackathon type: {t}")


def main(hid):
    cfg = H.load_config()
    hk = next((x for x in cfg["hackathons"] if x["id"] == hid), None)
    if not hk:
        raise SystemExit(f"'{hid}' not found in config/hackathons.yml -- add the block first.")

    projects = H.load_projects()
    reg = json.load(open(os.path.join(DATA, "team_registry.json")))
    if any(p["hackathon_id"] == hid for p in projects):
        print(f"warning: projects for '{hid}' already present; this will append duplicates. Aborting.")
        return

    # lookup: handle -> existing team_id, name -> existing team_id
    by_code, by_wallet, by_name = {}, {}, {}
    for tid, info in reg.items():
        for c in info.get("codes", []):
            by_code[c] = tid
        for w in info.get("wallets", []):
            by_wallet[w] = tid
        by_name.setdefault(norm(info["name"]), tid)

    def next_id():
        n = max((int(t[1:]) for t in reg), default=0) + 1
        return f"T{n:03d}"

    added_rows, new_teams = [], 0
    for r in _fetch_rows(hk):
        tid = None
        if r["code"] and r["code"] in by_code:
            tid = by_code[r["code"]]
        if not tid:
            for w in r["wallets"]:
                if w in by_wallet:
                    tid = by_wallet[w]; break
        if not tid and norm(r["team_name"]) in by_name:
            tid = by_name[norm(r["team_name"])]
        if not tid:
            tid = next_id(); new_teams += 1
            reg[tid] = {"name": r["team_name"], "codes": [], "wallets": []}
            by_name[norm(r["team_name"])] = tid
        # update registry handles
        if r["code"] and r["code"] not in reg[tid]["codes"]:
            reg[tid]["codes"].append(r["code"]); by_code[r["code"]] = tid
        for w in r["wallets"]:
            if w not in reg[tid]["wallets"]:
                reg[tid]["wallets"].append(w); by_wallet[w] = tid
        added_rows.append({
            "team_id": tid, "hackathon_id": hid, "project_name": r["project"],
            "team_name": reg[tid]["name"], "use_case": "", "github": r["github"],
            "code": r["code"], "wallets": r["wallets"], "src_tx": None,
            "meta": {"team": reg[tid]["name"], "total_hackathons": "", "use_case": "", "tracks": "",
                     "status": "", "score": "", "tx_count": "", "dev_commits_mar": "", "dev_prs_mar": "",
                     "milestones_done": "", "milestones_total": "", "url": r["github"],
                     "description": "", "uc_source": ""},
        })

    projects.extend(added_rows)
    json.dump(projects, open(os.path.join(DATA, "projects.json"), "w"), indent=1)
    json.dump(reg, open(os.path.join(DATA, "team_registry.json"), "w"), indent=1)
    print(f"added {len(added_rows)} projects for '{hid}' ({new_teams} new teams). "
          f"Review use_case fields (left blank) and commit data/.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python -m pipeline.add_hackathon <hackathon_id>")
    main(sys.argv[1])
