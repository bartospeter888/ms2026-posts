#!/usr/bin/env python3
"""Poll WC 2026 match results during evening windows and append newly-finished
matches to matches.json as soon as they appear.

Run every 10 min during 11:00-08:59 UTC (afternoon/evening kickoffs +
late finishes), plus a daily cleanup pass at 13:00 UTC that resets
matches.json / processed_ids.json for the next game day.

Goal scorers are enriched via TheSportsDB v1 (free key '123').
"""

import json
import os
import sys
from datetime import date, datetime, timedelta, timezone

import requests

sys.path.insert(0, os.path.dirname(__file__))
from scorer_lookup import scorers_by_teams

API_KEY = os.environ.get("FOOTBALL_DATA_API_KEY", "")
BASE_URL = "https://api.football-data.org/v4"
COMPETITION = "WC"
MATCHES_PATH   = os.path.join(os.path.dirname(__file__), "..", "matches.json")
PROCESSED_PATH = os.path.join(os.path.dirname(__file__), "..", "processed_ids.json")

TOURNAMENT_START = date(2026, 6, 11)
TOURNAMENT_END   = date(2026, 7, 19)


def game_day_for(now: datetime) -> date:
    """Afternoon/evening matches (11:00-23:59 UTC) and their late finishes
    (00:00-10:59 UTC the next day) both belong to the calendar date the
    afternoon/evening started on."""
    if now.hour >= 11:
        return now.date()
    return now.date() - timedelta(days=1)


def load_json(path: str, default):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save_json(path: str, data) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


def fetch_finished_matches(target: date) -> list:
    url = f"{BASE_URL}/competitions/{COMPETITION}/matches"
    headers = {"X-Auth-Token": API_KEY}
    # +1 day window catches late Pacific-time kickoffs whose utcDate rolls to next UTC day
    params  = {"dateFrom": target.isoformat(), "dateTo": (target + timedelta(days=1)).isoformat()}

    resp = requests.get(url, headers=headers, params=params, timeout=20)
    resp.raise_for_status()
    raw_matches = resp.json().get("matches", [])

    return [m for m in raw_matches if m.get("status") in ("FINISHED", "AWARDED")]


def build_match_entry(m: dict, target: date) -> dict:
    home  = m.get("homeTeam", {})
    away  = m.get("awayTeam", {})
    score = m.get("score", {}).get("fullTime", {})

    scorers_home, scorers_away = scorers_by_teams(
        home.get("name", ""), away.get("name", ""), target.isoformat()
    )
    print(f"    Scorers: {scorers_home} | {scorers_away}")

    return {
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
    }


def cleanup() -> None:
    save_json(MATCHES_PATH, {"date": "", "matches": []})
    save_json(PROCESSED_PATH, {"ids": []})
    print("Cleanup: matches.json and processed_ids.json reset for the next game day.")


def main():
    if not API_KEY:
        print("ERROR: FOOTBALL_DATA_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    now = datetime.now(timezone.utc)
    override = os.environ.get("DATE_OVERRIDE", "").strip()

    if not override and now.hour == 13:
        cleanup()
        return

    if override:
        try:
            target = date.fromisoformat(override)
            print(f"DATE_OVERRIDE: using {target}")
        except ValueError:
            print(f"ERROR: invalid DATE_OVERRIDE '{override}'", file=sys.stderr)
            sys.exit(1)
    else:
        target = game_day_for(now)

    if COMPETITION == "WC" and not (TOURNAMENT_START <= target <= TOURNAMENT_END):
        print(f"Game day {target} outside tournament window — nothing to do.")
        return

    print(f"Polling {COMPETITION} matches for game day {target}…")
    finished = fetch_finished_matches(target)

    processed = load_json(PROCESSED_PATH, {"ids": []})
    processed_ids = set(processed.get("ids", []))

    new_matches = [m for m in finished if m.get("id") not in processed_ids]
    if not new_matches:
        print("No new finished matches.")
        return

    data = load_json(MATCHES_PATH, {"date": "", "matches": []})
    if data.get("date") != target.isoformat():
        data = {"date": target.isoformat(), "matches": []}

    for m in new_matches:
        entry = build_match_entry(m, target)
        data["matches"].append(entry)
        processed_ids.add(m.get("id"))
        print(f"  New card: {entry['home']['name']} {entry['score']['home']}:{entry['score']['away']} {entry['away']['name']}")

    save_json(MATCHES_PATH, data)
    save_json(PROCESSED_PATH, {"ids": sorted(processed_ids)})
    print(f"Saved {len(new_matches)} new match(es) → {MATCHES_PATH}")


if __name__ == "__main__":
    main()
