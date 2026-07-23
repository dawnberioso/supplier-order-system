
# ---------- general time off (leave entries & public holidays) ----------

    # Australian national public holidays for 2026 (seed values shown until the
    # user edits & saves their own list). State-specific days can be added in-app.
    # Australian public holidays for 2026 — national days plus the main
    # state/territory days (labelled with their state). Shown as the seed until
    # the user saves their own list. NOTE: a few state days (e.g. WA King's
    # Birthday, VIC AFL Grand Final Friday) are proclaimed each year and should
    # be verified; the user can edit/add any in-app.
DEFAULT_AU_HOLIDAYS = [
{"date": "2026-01-01", "name": "New Year's Day"},
{"date": "2026-01-26", "name": "Australia Day"},
        {"date": "2026-03-02", "name": "Labour Day (WA)"},
        {"date": "2026-03-09", "name": "Labour Day (VIC)"},
        {"date": "2026-03-09", "name": "Eight Hours Day (TAS)"},
        {"date": "2026-03-09", "name": "Canberra Day (ACT)"},
        {"date": "2026-03-09", "name": "Adelaide Cup (SA)"},
{"date": "2026-04-03", "name": "Good Friday"},
{"date": "2026-04-04", "name": "Easter Saturday"},
{"date": "2026-04-05", "name": "Easter Sunday"},
{"date": "2026-04-06", "name": "Easter Monday"},
{"date": "2026-04-25", "name": "Anzac Day"},
        {"date": "2026-06-08", "name": "King's Birthday"},
        {"date": "2026-04-27", "name": "Anzac Day holiday (WA)"},
        {"date": "2026-05-04", "name": "Labour Day (QLD)"},
        {"date": "2026-05-04", "name": "May Day (NT)"},
        {"date": "2026-06-01", "name": "Western Australia Day (WA)"},
        {"date": "2026-06-01", "name": "Reconciliation Day (ACT)"},
        {"date": "2026-06-08", "name": "King's Birthday (NSW, VIC, ACT, SA, TAS, NT)"},
        {"date": "2026-08-03", "name": "Picnic Day (NT)"},
        {"date": "2026-08-03", "name": "Bank Holiday (NSW, ACT)"},
        {"date": "2026-09-28", "name": "King's Birthday (WA)"},
        {"date": "2026-10-05", "name": "Labour Day (NSW, ACT, SA)"},
        {"date": "2026-10-05", "name": "King's Birthday (QLD)"},
        {"date": "2026-11-03", "name": "Melbourne Cup (VIC)"},
{"date": "2026-12-25", "name": "Christmas Day"},
{"date": "2026-12-26", "name": "Boxing Day"},
        {"date": "2026-12-28", "name": "Boxing Day holiday (additional)"},
        {"date": "2026-12-28", "name": "Proclamation Day (SA)"},
]

def get_time_off(self):
@@ -441,12 +462,16 @@ def _m(data):
default={"entries": [], "holidays": []})

def get_holidays(self):
        # If no list has been saved yet, fall back to the AU national defaults so
        # holidays appear on the dashboard without requiring a first save.
        # Fall back to the AU defaults whenever no holidays have been saved yet
        # (file missing, key absent, OR the stored list is empty — which happens
        # once time_off.json was first created by a break/leave save).
data, _ = self._get_file("time_off.json")
        if data is None or "holidays" not in data:
        if data is None:
            return [dict(h) for h in self.DEFAULT_AU_HOLIDAYS]
        hols = data.get("holidays", [])
        if not hols:
return [dict(h) for h in self.DEFAULT_AU_HOLIDAYS]
        return data.get("holidays", [])
        return hols

def update_holidays(self, rows):
def _m(data):
