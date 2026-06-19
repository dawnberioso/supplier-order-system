import json
import os
import base64
import pandas as pd
from datetime import datetime

try:
    import requests
except ImportError:
    requests = None

try:
    import streamlit as st
except ImportError:
    st = None


def _get_secret(key, default=""):
    """Read a config value from Streamlit secrets first, then env vars."""
    if st is not None:
        try:
            if key in st.secrets:
                return st.secrets[key]
        except Exception:
            pass
    return os.getenv(key, default)


class DataHandler:
    """
    Handles all data operations, reading and writing supplier JSON files
    directly to a GitHub repository via the GitHub API.

    Requires three secrets (set in Streamlit -> Settings -> Secrets):
      GITHUB_TOKEN  = your personal access token
      GITHUB_REPO   = "username/repository"   e.g. "dawnberioso/supplier-order-system"
      GITHUB_BRANCH = "main"                  (optional, defaults to main)
    """

    def __init__(self, data_dir="supplier_data"):
        self.data_dir = data_dir
        self.token = _get_secret("GITHUB_TOKEN", "")
        self.repo = _get_secret("GITHUB_REPO", "")
        self.branch = _get_secret("GITHUB_BRANCH", "main")
        self.api_base = "https://api.github.com"

    # ---------- internal helpers ----------

    def is_connected(self):
        """True if we have everything needed to write to GitHub."""
        return bool(self.token and self.repo and requests is not None)

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
        }

    def _path(self, filename):
        return f"{self.data_dir}/{filename}"

    def _get_file(self, filename):
        """Return (content_dict, sha) for a JSON file, or (None, None)."""
        url = f"{self.api_base}/repos/{self.repo}/contents/{self._path(filename)}"
        try:
            r = requests.get(url, headers=self._headers(),
                             params={"ref": self.branch}, timeout=20)
            if r.status_code == 200:
                payload = r.json()
                raw = base64.b64decode(payload["content"]).decode("utf-8")
                return json.loads(raw), payload["sha"]
            return None, None
        except Exception as e:
            print(f"_get_file error for {filename}: {e}")
            return None, None

    def _put_file(self, filename, content_dict, message):
        """Create or update a JSON file on GitHub. Returns True on success."""
        if not self.is_connected():
            return False
        url = f"{self.api_base}/repos/{self.repo}/contents/{self._path(filename)}"
        _, sha = self._get_file(filename)
        raw = json.dumps(content_dict, indent=2, ensure_ascii=False)
        body = {
            "message": message,
            "content": base64.b64encode(raw.encode("utf-8")).decode("utf-8"),
            "branch": self.branch,
        }
        if sha:
            body["sha"] = sha
        try:
            r = requests.put(url, headers=self._headers(), json=body, timeout=30)
            return r.status_code in (200, 201)
        except Exception as e:
            print(f"_put_file error for {filename}: {e}")
            return False

    def _modify(self, filename, mutate, message, default=None):
        """Safe read-modify-write with optimistic locking.

        Reads the file's content AND sha together, applies `mutate(data)`
        (which returns the new dict), and writes with that exact sha. If
        GitHub rejects the write because someone else changed the file in the
        meantime (409 conflict), it re-reads the freshest content and re-applies
        `mutate`, retrying a few times. This prevents one save from silently
        overwriting another section's data.
        """
        if not self.is_connected():
            return False
        url = f"{self.api_base}/repos/{self.repo}/contents/{self._path(filename)}"
        for _ in range(5):
            current, sha = self._get_file(filename)
            if current is None:
                if default is None:
                    return False  # refuse to write over an unreadable file
                current = json.loads(json.dumps(default))  # fresh deep copy
            new_content = mutate(current)
            if new_content is None:
                return False
            raw = json.dumps(new_content, indent=2, ensure_ascii=False)
            body = {
                "message": message,
                "content": base64.b64encode(raw.encode("utf-8")).decode("utf-8"),
                "branch": self.branch,
            }
            if sha:
                body["sha"] = sha
            try:
                r = requests.put(url, headers=self._headers(), json=body, timeout=30)
            except Exception as e:
                print(f"_modify error for {filename}: {e}")
                return False
            if r.status_code in (200, 201):
                return True
            if r.status_code == 409:
                continue  # sha stale — another write landed; re-read and retry
            print(f"_modify PUT {filename} -> {r.status_code}: {r.text[:200]}")
            return False
        return False

    def _delete_file(self, filename, message):
        if not self.is_connected():
            return False
        _, sha = self._get_file(filename)
        if not sha:
            return False
        url = f"{self.api_base}/repos/{self.repo}/contents/{self._path(filename)}"
        body = {"message": message, "sha": sha, "branch": self.branch}
        try:
            r = requests.delete(url, headers=self._headers(), json=body, timeout=30)
            return r.status_code == 200
        except Exception as e:
            print(f"_delete_file error for {filename}: {e}")
            return False

    def _list_supplier_files(self):
        """List all .json files in the data dir except config.json."""
        url = f"{self.api_base}/repos/{self.repo}/contents/{self.data_dir}"
        try:
            r = requests.get(url, headers=self._headers(),
                             params={"ref": self.branch}, timeout=20)
            if r.status_code != 200:
                return []
            # Internal data files that are NOT suppliers (so they never show in
            # the supplier dropdown and can't be deleted as one).
            reserved = {"config.json", "shift_coverage.json", "time_off.json"}
            files = []
            for item in r.json():
                name = item.get("name", "")
                if name.endswith(".json") and name not in reserved:
                    files.append(name[:-5])  # strip .json
            return sorted(files)
        except Exception as e:
            print(f"_list_supplier_files error: {e}")
            return []

    def _now(self):
        return datetime.now().isoformat()

    # ---------- suppliers ----------

    def get_all_suppliers(self):
        return self._list_supplier_files()

    def create_supplier(self, supplier_name, description=""):
        existing, _ = self._get_file(f"{supplier_name}.json")
        if existing is not None:
            return False  # already exists
        data = {
            "supplier_name": supplier_name,
            "description": description,
            "created_at": self._now(),
            "last_updated": self._now(),
            "rules": [],
        }
        ok = self._put_file(f"{supplier_name}.json", data,
                            f"Create supplier {supplier_name}")
        if ok:
            self._add_to_config(supplier_name)
        return ok

    def delete_supplier(self, supplier_name):
        ok = self._delete_file(f"{supplier_name}.json",
                               f"Delete supplier {supplier_name}")
        if ok:
            self._remove_from_config(supplier_name)
        return ok

    def rename_supplier(self, old_name, new_name):
        data, _ = self._get_file(f"{old_name}.json")
        if data is None:
            return False
        exists, _ = self._get_file(f"{new_name}.json")
        if exists is not None:
            return False
        data["supplier_name"] = new_name
        data["last_updated"] = self._now()
        if not self._put_file(f"{new_name}.json", data,
                              f"Rename supplier to {new_name}"):
            return False
        self._delete_file(f"{old_name}.json", f"Remove old name {old_name}")
        self._remove_from_config(old_name)
        self._add_to_config(new_name)
        return True

    def get_supplier_info(self, supplier_name):
        data, _ = self._get_file(f"{supplier_name}.json")
        if data is None:
            return {}
        return {
            "supplier_name": data.get("supplier_name", supplier_name),
            "description": data.get("description", ""),
            "created_at": data.get("created_at", "N/A"),
            "last_updated": data.get("last_updated", "N/A"),
        }

    # ---------- rules ----------

    def get_supplier_rules(self, supplier_name):
        data, _ = self._get_file(f"{supplier_name}.json")
        if data is None:
            return []
        return data.get("rules", [])

    def add_rule(self, supplier_name, rule):
        def _m(data):
            data.setdefault("rules", []).append(rule)
            data["last_updated"] = self._now()
            return data
        return self._modify(f"{supplier_name}.json", _m,
                            f"Add rule to {supplier_name}")

    def update_supplier_rules(self, supplier_name, rules):
        def _m(data):
            data["rules"] = rules
            data["last_updated"] = self._now()
            return data
        return self._modify(f"{supplier_name}.json", _m,
                            f"Update rules for {supplier_name}",
                            default={"supplier_name": supplier_name, "rules": []})

    def delete_supplier_rules(self, supplier_name):
        return self.update_supplier_rules(supplier_name, [])

    # ---------- favorites ----------

    def get_supplier_favorites(self, supplier_name):
        data, _ = self._get_file(f"{supplier_name}.json")
        if data is None:
            return []
        return data.get("favorites", [])

    def update_supplier_favorites(self, supplier_name, favorites):
        # default=None => refuse to write if the file can't be read, so we
        # never risk overwriting the supplier's rules with a blank file.
        def _m(data):
            data["favorites"] = favorites
            data["last_updated"] = self._now()
            return data
        return self._modify(f"{supplier_name}.json", _m,
                            f"Update favorites for {supplier_name}")

    # ---------- rules meta (custom column titles & extra columns) ----------

    def get_rules_meta(self, supplier_name):
        data, _ = self._get_file(f"{supplier_name}.json")
        meta = (data or {}).get("rules_meta", {})
        return {"labels": dict(meta.get("labels", {})),
                "extra_columns": list(meta.get("extra_columns", []))}

    def update_rules_meta(self, supplier_name, meta):
        def _m(data):
            data["rules_meta"] = {"labels": dict(meta.get("labels", {})),
                                  "extra_columns": list(meta.get("extra_columns", []))}
            data["last_updated"] = self._now()
            return data
        return self._modify(f"{supplier_name}.json", _m,
                            f"Update rules columns for {supplier_name}")

    # ---------- product rules (product-level defaults, no customer) ----------

    def get_product_rules(self, supplier_name):
        data, _ = self._get_file(f"{supplier_name}.json")
        if data is None:
            return []
        return data.get("product_rules", [])

    def update_product_rules(self, supplier_name, rules):
        def _m(data):
            data["product_rules"] = rules
            data["last_updated"] = self._now()
            return data
        return self._modify(f"{supplier_name}.json", _m,
                            f"Update product rules for {supplier_name}")

    def get_product_rules_meta(self, supplier_name):
        data, _ = self._get_file(f"{supplier_name}.json")
        meta = (data or {}).get("product_rules_meta", {})
        return {"labels": dict(meta.get("labels", {})),
                "extra_columns": list(meta.get("extra_columns", []))}

    def update_product_rules_meta(self, supplier_name, meta):
        def _m(data):
            data["product_rules_meta"] = {"labels": dict(meta.get("labels", {})),
                                          "extra_columns": list(meta.get("extra_columns", []))}
            data["last_updated"] = self._now()
            return data
        return self._modify(f"{supplier_name}.json", _m,
                            f"Update product rules columns for {supplier_name}")

    # ---------- supplier details (Time Shift, POC, etc.) ----------

    DETAIL_KEYS = ["time_shift_aut", "time_shift_ukt", "information", "poc", "team_ph"]

    def get_supplier_details(self, supplier_name):
        data, _ = self._get_file(f"{supplier_name}.json")
        details = (data or {}).get("details", {})
        # Always return every expected key so the form renders consistently.
        return {k: details.get(k, "") for k in self.DETAIL_KEYS}

    def update_supplier_details(self, supplier_name, details):
        def _m(data):
            data["details"] = {k: details.get(k, "") for k in self.DETAIL_KEYS}
            data["last_updated"] = self._now()
            return data
        return self._modify(f"{supplier_name}.json", _m,
                            f"Update details for {supplier_name}")

    # ---------- required days per customer ----------

    def get_required_days(self, supplier_name):
        data, _ = self._get_file(f"{supplier_name}.json")
        if data is None:
            return []
        return data.get("required_days", [])

    def update_required_days(self, supplier_name, rows):
        def _m(data):
            data["required_days"] = rows
            data["last_updated"] = self._now()
            return data
        return self._modify(f"{supplier_name}.json", _m,
                            f"Update required days for {supplier_name}")

    # ---------- shift coverage (employees & schedules) ----------

    def get_shift_coverage(self):
        data, _ = self._get_file("shift_coverage.json")
        if data is None:
            return []
        return data.get("rows", [])

    def update_shift_coverage(self, rows):
        def _m(data):
            data["rows"] = rows
            data["last_updated"] = self._now()
            return data
        return self._modify("shift_coverage.json", _m, "Update shift coverage",
                            default={"rows": []})

    # Coverage Overview is a separate weekly roster (Member, Role, Mon-Sun),
    # kept apart from the per-supplier schedules stored in "rows".
    def get_coverage_overview(self):
        data, _ = self._get_file("shift_coverage.json")
        if data is None:
            return []
        return data.get("overview", [])

    def update_coverage_overview(self, rows):
        def _m(data):
            data["overview"] = rows
            data["last_updated"] = self._now()
            return data
        return self._modify("shift_coverage.json", _m, "Update coverage overview",
                            default={"rows": []})

    def get_coverage_meta(self):
        data, _ = self._get_file("shift_coverage.json")
        meta = (data or {}).get("overview_meta", {})
        return {"labels": dict(meta.get("labels", {})),
                "extra_columns": list(meta.get("extra_columns", []))}

    def update_coverage_meta(self, meta):
        def _m(data):
            data["overview_meta"] = {"labels": dict(meta.get("labels", {})),
                                     "extra_columns": list(meta.get("extra_columns", []))}
            data["last_updated"] = self._now()
            return data
        return self._modify("shift_coverage.json", _m, "Update coverage overview columns",
                            default={"rows": []})

    # ---------- general time off (leave entries & public holidays) ----------

    # Australian national public holidays for 2026 (seed values shown until the
    # user edits & saves their own list). State-specific days can be added in-app.
    DEFAULT_AU_HOLIDAYS = [
        {"date": "2026-01-01", "name": "New Year's Day"},
        {"date": "2026-01-26", "name": "Australia Day"},
        {"date": "2026-04-03", "name": "Good Friday"},
        {"date": "2026-04-04", "name": "Easter Saturday"},
        {"date": "2026-04-05", "name": "Easter Sunday"},
        {"date": "2026-04-06", "name": "Easter Monday"},
        {"date": "2026-04-25", "name": "Anzac Day"},
        {"date": "2026-06-08", "name": "King's Birthday"},
        {"date": "2026-12-25", "name": "Christmas Day"},
        {"date": "2026-12-26", "name": "Boxing Day"},
    ]

    def get_time_off(self):
        data, _ = self._get_file("time_off.json")
        if data is None:
            return []
        return data.get("entries", [])

    def update_time_off(self, rows):
        def _m(data):
            data["entries"] = rows
            data["last_updated"] = self._now()
            return data
        return self._modify("time_off.json", _m, "Update time off entries",
                            default={"entries": [], "holidays": []})

    def get_holidays(self):
        # If no list has been saved yet, fall back to the AU national defaults so
        # holidays appear on the dashboard without requiring a first save.
        data, _ = self._get_file("time_off.json")
        if data is None or "holidays" not in data:
            return [dict(h) for h in self.DEFAULT_AU_HOLIDAYS]
        return data.get("holidays", [])

    def update_holidays(self, rows):
        def _m(data):
            data["holidays"] = rows
            data["last_updated"] = self._now()
            return data
        return self._modify("time_off.json", _m, "Update public holidays",
                            default={"entries": [], "holidays": []})

    def get_breaks(self):
        data, _ = self._get_file("time_off.json")
        if data is None:
            return []
        return data.get("breaks", [])

    def update_breaks(self, rows):
        def _m(data):
            data["breaks"] = rows
            data["last_updated"] = self._now()
            return data
        return self._modify("time_off.json", _m, "Update staff on break",
                            default={"entries": [], "holidays": [], "breaks": []})

    # ---------- config.json ----------

    def _add_to_config(self, supplier_name):
        cfg, _ = self._get_file("config.json")
        if cfg is None:
            cfg = {"version": "1.0", "created_at": self._now(), "suppliers": []}
        if supplier_name not in cfg.get("suppliers", []):
            cfg.setdefault("suppliers", []).append(supplier_name)
        cfg["last_updated"] = self._now()
        self._put_file("config.json", cfg, f"Register supplier {supplier_name}")

    def _remove_from_config(self, supplier_name):
        cfg, _ = self._get_file("config.json")
        if cfg is None:
            return
        if supplier_name in cfg.get("suppliers", []):
            cfg["suppliers"].remove(supplier_name)
        cfg["last_updated"] = self._now()
        self._put_file("config.json", cfg, f"Unregister supplier {supplier_name}")

    # ---------- misc ----------

    def get_statistics(self):
        stats = {"total_suppliers": 0, "total_rules": 0,
                 "total_customers": set(), "total_products": set()}
        for supplier in self.get_all_suppliers():
            stats["total_suppliers"] += 1
            for rule in self.get_supplier_rules(supplier):
                stats["total_rules"] += 1
                stats["total_customers"].add(rule.get("customer", ""))
                stats["total_products"].add(rule.get("ordered_product", ""))
        stats["total_customers"] = len(stats["total_customers"])
        stats["total_products"] = len(stats["total_products"])
        return stats
