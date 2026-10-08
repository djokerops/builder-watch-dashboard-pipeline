"""Upload the 3 generated CSVs to Dune, replacing the existing dataset_* tables."""
import os
from . import handles as H
from .dune_client import upload_csv

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "out")


def main():
    cfg = H.load_config()
    tables = cfg["dune_upload"]["tables"]
    files = {
        "team_metrics": "team_metrics.csv",
        "team_projects": "team_projects_final.csv",
        "lena_worklist": "lena_worklist.csv",
    }
    for key, fname in files.items():
        path = os.path.join(OUT, fname)
        with open(path) as f:
            text = f.read()
        table = tables[key]   # upload name; Dune prepends "dataset_"
        resp = upload_csv(table, text, description=f"Builder Watchtower {key} (auto-refreshed daily)")
        print(f"uploaded {fname} -> dune.{cfg['dune_upload']['namespace']}.dataset_{table}  {resp}")


if __name__ == "__main__":
    main()
