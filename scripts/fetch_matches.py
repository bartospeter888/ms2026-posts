#!/usr/bin/env python3
"""Fetch WC 2026 match results for yesterday from football-data.org and save to matches.json.
Goal scorers are enriched via TheSportsDB v1 (free key '123').
"""

import json
import os
import sys
from datetime import date, timedelta

import requests

sys.path.insert(0, os.path.dirname(__file__))
from scorer_lookup import scorers_by_teams

API_KEY = os.environ.get("FOOTBALL_DATA_API_KEY", "")
BASE_URL = "https://api.football-data.org/v4"
COMPETITION = "WC"
OUTPUT = os.path.join(os.path.dirname(__file__), "..", "matches.json")

TOURNAMENT_START = date(2026, 6, 11)
TOURNAMENT_END   = date(2026, 7, 19)


def fetch_matches(target: date) -> list:
    url = f"{BASE_URL}/competitions/{COMPETITION}/matches"
    headers = {"X-Auth-Token": API_KEY}
    # +1 day window catches late Pacific-time kickoffs whose utcDate rolls to next UTC day
    params  = {"dateFrom": target.isoformat(), "dateTo": (target + timedelta(days=1)).isoformat()}

    resp = requests.get(url, headers=headers, params=params, timeout=20)
    resp.raise_for_status()
    raw_matches = resp.json().get("matches", [])

    matches = []
    for m in raw_matches:
        if m.get("status") not in ("FINISHED", "AWARDED"):
            continue

        home  = m.get("homeTeam", {})
        away  = m.get("awayTeam", {})
        score = m.get("score", {}).get("fullTime", {})

        # Scorers from TheSportsDB (football-data.org free tier has no goals)
        home_name_str = home.get("name", "")
        away_name_str = away.get("name", "")
        scorers_home, scorers_away = scorers_by_teams(
            home_name_str, away_name_str, target.isoformat()
        )
        print(f"    Scorers: {scorers_home} | {scorers_away}")

        matches.append({
            "id":           m.get("id"),
            "utcDate":      m.get("utcDate", target.isoformat()),
            "matchday":     m.get("matchday"),
            "stage":        m.get("stage", "GROUP_STAGE"),
            "group":        m.get("group"),
            "home": {
                "name":      home.get("name", ""),
                "shortName": home.get("shortName") or home.get("name", ""),
                "tla":       home.get("tla", ""),
                "crest":     home.get("crest", ""),
            },
            "away": {
                "name":      away.get("name", ""),
                "shortName": away.get("shortName") or away.get("name", ""),
                "tla":       away.get("tla", ""),
                "crest":     away.get("crest", ""),
            },
            "score": {
                "home": score.get("home"),
                "away": score.get("away"),
            },
            "scorers_home": scorers_home,
            "scorers_away": scorers_away,
        })

    return matches


def main():
    if not API_KEY:
        print("ERROR: FOOTBALL_DATA_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    override = os.environ.get("DATE_OVERRIDE", "").strip()
    if override:
        try:
            target = date.fromisoformat(override)
            print(f"DATE_OVERRIDE: using {target}")
        except ValueError:
            print(f"ERROR: invalid DATE_OVERRIDE '{override}'", file=sys.stderr)
            sys.exit(1)
    else:
        target = date.today() - timedelta(days=1)

    if COMPETITION == "WC" and not (TOURNAMENT_START <= target <= TOURNAMENT_END):
        print(f"Date {target} outside tournament window — writing empty matches.json")
        result = {"date": target.isoformat(), "matches": []}
    else:
        print(f"Fetching {COMPETITION} matches for {target}…")
        matches = fetch_matches(target)
        print(f"  Found {len(matches)} finished match(es).")
        result = {"date": target.isoformat(), "matches": matches}

    with open(OUTPUT, "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=2)
    print(f"Saved → {OUTPUT}")


if __name__ == "__main__":
    main()
