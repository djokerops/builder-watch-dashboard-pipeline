"""Minimal Dune API client: run SQL, and upload CSV tables (create/replace)."""
import os, time, json, requests

API = "https://api.dune.com/api/v1"

_TRANSIENT = (429, 500, 502, 503, 504)


def _post(url, headers, json_body, tries=5):
    """POST with retry on transient 429/5xx errors (Dune occasionally 500s on create)."""
    last = None
    for i in range(tries):
        r = requests.post(url, headers=headers, json=json_body)
        if r.status_code < 400:
            return r
        last = r
        if r.status_code in _TRANSIENT:
            time.sleep(3 * (i + 1)); continue
        r.raise_for_status()
    last.raise_for_status()


def _get(url, headers, params=None, tries=5):
    """GET with retry on transient 429/5xx errors."""
    last = None
    for i in range(tries):
        r = requests.get(url, headers=headers, params=params)
        if r.status_code < 400:
            return r
        last = r
        if r.status_code in _TRANSIENT:
            time.sleep(3 * (i + 1)); continue
        r.raise_for_status()
    last.raise_for_status()


def _key():
    k = os.environ.get("DUNE_API_KEY")
    if k:
        return k
    # local fallback: the Dune CLI's saved config (~/.config/dune/config.yaml)
    cfg = os.path.expanduser("~/.config/dune/config.yaml")
    if os.path.exists(cfg):
        import re
        txt = open(cfg).read()
        m = re.search(r"(?:api[_-]?key|key)\s*:\s*['\"]?([A-Za-z0-9_\-]+)", txt)
        if m:
            return m.group(1)
    raise SystemExit("DUNE_API_KEY is not set (add it as a GitHub Actions secret / env var).")


def run_sql(sql, performance="large", poll=5, timeout=2400):
    """Run raw DuneSQL: create a private temp query, execute it, return result rows, archive it."""
    h = {"X-Dune-Api-Key": _key(), "Content-Type": "application/json"}
    c = _post(f"{API}/query", h,
              {"name": "watchtower-pipeline (temp)", "query_sql": sql, "is_private": True})
    qid = c.json()["query_id"]
    try:
        e = _post(f"{API}/query/{qid}/execute", h, {"performance": performance})
        execution_id = e.json()["execution_id"]
        deadline = time.time() + timeout
        while time.time() < deadline:
            s = _get(f"{API}/execution/{execution_id}/status", h)
            state = s.json()["state"]
            if state == "QUERY_STATE_COMPLETED":
                res = _get(f"{API}/execution/{execution_id}/results", h, params={"limit": 100000})
                return res.json()["result"]["rows"]
            if state in ("QUERY_STATE_FAILED", "QUERY_STATE_CANCELLED", "QUERY_STATE_EXPIRED"):
                raise RuntimeError(f"Dune execution {execution_id} ended in {state}")
            time.sleep(poll)
        raise TimeoutError(f"Dune execution {execution_id} did not finish within {timeout}s")
    finally:
        try:
            requests.post(f"{API}/query/{qid}/archive", headers=h)
        except Exception:
            pass


def upload_csv(table_name, csv_text, description="", is_private=False):
    """Create or REPLACE a table from CSV text. Table lands at dune.<namespace>.<table_name>."""
    h = {"X-Dune-Api-Key": _key(), "Content-Type": "application/json"}
    r = _post(f"{API}/table/upload/csv", h,
              {"table_name": table_name, "data": csv_text,
               "description": description, "is_private": is_private})
    return r.json()
