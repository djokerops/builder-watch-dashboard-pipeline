"""Compare freshly-built out/ CSVs against the known-good reference CSVs."""
import csv, sys, os
REF = "/private/tmp/claude-503/-Users-arua/6bf04b4d-61f3-41cd-92e6-709ef0336326/scratchpad"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")


def load(path, key):
    return {r[key]: r for r in csv.DictReader(open(path))}


def cmp_metric(name, a, b, cols):
    print(f"\n== {name} ==")
    ids = set(a) & set(b)
    print(f"rows: out={len(a)} ref={len(b)} common={len(ids)}")
    for c in cols:
        diffs = []
        for i in ids:
            try:
                av = float(a[i].get(c, 0) or 0); bv = float(b[i].get(c, 0) or 0)
            except ValueError:
                continue
            if abs(av - bv) > max(1.0, 0.01 * abs(bv)):
                diffs.append((i, bv, av))
        print(f"  {c}: {len(diffs)} teams differ >1% ", end="")
        if diffs[:3]:
            print("e.g.", [(i, b, a) for i, b, a in diffs[:3]])
        else:
            print("(match)")


tm_o = load(os.path.join(OUT, "team_metrics.csv"), "team_id")
tm_r = load(os.path.join(REF, "team_metrics.csv"), "team_id")
cmp_metric("team_metrics", tm_o, tm_r, ["tx", "volume_usd", "users"])
# tier distribution
from collections import Counter
print("\ntiers out:", dict(Counter(r["value_tier"] for r in tm_o.values())))
print("tiers ref:", dict(Counter(r["value_tier"] for r in tm_r.values())))
