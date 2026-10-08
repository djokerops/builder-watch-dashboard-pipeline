"""Load config + seed, and derive the count-once agent-handle maps used for all on-chain metrics.

Rules (identical to the Builder Watchtower methodology):
  * wallets are agent wallets ONLY for erc8004 + builder_code hackathons.
    project_submission hackathons (Real World, Synthesis) contribute NO wallet -- their
    recipient/payout addresses are developer payout wallets, never counted.
  * codes come only from builder_code hackathons.
  * a handle shared across teams is owned once, by the team with the most project rows
    (ties -> lowest team_id), so nothing is double-counted across teams.
"""
import os, json, yaml
from collections import defaultdict, Counter

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_config():
    with open(os.path.join(HERE, "config", "hackathons.yml")) as f:
        return yaml.safe_load(f)


def load_projects():
    return json.load(open(os.path.join(HERE, "data", "projects.json")))


def _types(cfg):
    return {h["id"]: h["type"] for h in cfg["hackathons"]}


def build(cfg=None, projects=None):
    cfg = cfg or load_config()
    projects = projects or load_projects()
    htype = _types(cfg)
    ex = {cfg["zero_address"].lower()[2:], cfg["registry_address"].lower()[2:]}

    def project_handles(p):
        t = htype[p["hackathon_id"]]
        codes = [p["code"]] if (p["code"] and t == "builder_code") else []
        wallets = []
        if t in ("erc8004", "builder_code"):
            wallets = [w for w in p["wallets"] if w and w.lower() not in ex]
        return codes, wallets

    # count-once ownership across teams
    h2t = defaultdict(Counter)
    for p in projects:
        c, w = project_handles(p)
        for x in c:
            h2t["c:" + x][p["team_id"]] += 1
        for x in w:
            h2t["w:" + x][p["team_id"]] += 1
    owner = {h: sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[0][0] for h, c in h2t.items()}

    team_codes = defaultdict(set)
    team_wallets = defaultdict(set)
    pid_map = {}                 # pid -> (team_id, hackathon_id, project_name)
    proj_wallet_pairs = []       # (pid, team_id, wallet)
    proj_code_pairs = []         # (pid, team_id, code)
    pid = 0
    for p in projects:
        c, w = project_handles(p)
        oc = [x for x in c if owner["c:" + x] == p["team_id"]]
        ow = [x for x in w if owner["w:" + x] == p["team_id"]]
        team_codes[p["team_id"]].update(oc)
        team_wallets[p["team_id"]].update(ow)
        if not oc and not ow:
            continue
        pid += 1
        pid_map[pid] = (p["team_id"], p["hackathon_id"], p["project_name"])
        for x in ow:
            proj_wallet_pairs.append((pid, p["team_id"], x))
        for x in oc:
            proj_code_pairs.append((pid, p["team_id"], x))

    all_wallets = sorted({w for s in team_wallets.values() for w in s})
    all_codes = sorted({c for s in team_codes.values() for c in s})
    return {
        "team_codes": {t: sorted(s) for t, s in team_codes.items()},
        "team_wallets": {t: sorted(s) for t, s in team_wallets.items()},
        "pid_map": pid_map,
        "proj_wallet_pairs": proj_wallet_pairs,
        "proj_code_pairs": proj_code_pairs,
        "all_wallets": all_wallets,
        "all_codes": all_codes,
    }
