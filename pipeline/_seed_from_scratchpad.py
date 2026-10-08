"""ONE-TIME: build the committed seed (data/projects.json, data/team_registry.json)
from the current resolved state in the analysis scratchpad. After this, the seed is the
source of truth for team identity; the daily pipeline only refreshes on-chain metrics."""
import json, csv, os
SCRATCH = "/private/tmp/claude-503/-Users-arua/6bf04b4d-61f3-41cd-92e6-709ef0336326/scratchpad"
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(HERE, "data")

HKID = {'Real World v1': 'rw_v1', 'Real World v2': 'rw_v2', 'PoS AI': 'pos',
        'Onchain': 'onchain', 'Synthesis': 'synthesis',
        'Agentic DeFAI': 'defai', 'Agents at Work': 'aaw'}

def rows(f):
    d = json.load(open(os.path.join(SCRATCH, f)))
    return d.get('result', {}).get('rows') or d.get('rows')

srcmap = json.load(open(os.path.join(SCRATCH, 'srcmap2.json')))
tp = rows('tp_anchor.json')
meta = {(r['team_id'], r['hackathon'], r['project_name']): r for r in tp}

CURATED = ['team', 'total_hackathons', 'use_case', 'tracks', 'status', 'score', 'tx_count',
           'dev_commits_mar', 'dev_prs_mar', 'milestones_done', 'milestones_total', 'url',
           'description', 'uc_source']

projects = []
for o in srcmap:
    m = meta.get((o['team_id'], o['hackathon'], o['project_name']), {})
    projects.append({
        "team_id": o['team_id'],
        "hackathon_id": HKID[o['hackathon']],
        "project_name": o['project_name'],
        "team_name": m.get('team', o['project_name']),
        "use_case": m.get('use_case', ''),
        "github": m.get('url', ''),
        "code": o.get('code') or '',
        "wallets": o.get('wallets', []),          # agent wallets (dev payout already excluded upstream)
        "src_tx": o.get('src_tx'),
        "meta": {k: m.get(k, '') for k in CURATED},   # curated columns passed through verbatim
    })

# team registry: stable id -> name + all handles ever seen (for matching future submissions)
from collections import defaultdict
reg = {}
names = {}
hand = defaultdict(lambda: {"codes": set(), "wallets": set()})
for p in projects:
    names.setdefault(p['team_id'], p['team_name'])
    hand[p['team_id']]  # ensure every team is present, even with no handles
    if p['code']:
        hand[p['team_id']]['codes'].add(p['code'])
    for w in p['wallets']:
        hand[p['team_id']]['wallets'].add(w)
for tid in sorted(hand):
    reg[tid] = {"name": names[tid],
                "codes": sorted(hand[tid]['codes']),
                "wallets": sorted(hand[tid]['wallets'])}

os.makedirs(DATA, exist_ok=True)
json.dump(projects, open(os.path.join(DATA, 'projects.json'), 'w'), indent=1)
json.dump(reg, open(os.path.join(DATA, 'team_registry.json'), 'w'), indent=1)
print(f"seeded {len(projects)} projects across {len(reg)} teams")
