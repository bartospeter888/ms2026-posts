#!/usr/bin/env python3
"""Goal scorer lookup via TheSportsDB v1 (free key '123').

lookuptimeline.php returns ALL match events (goals, cards, substitutions),
distinguished by strTimeline ("Goal", "Card", "subst", ...). We must filter
for strTimeline == "Goal" to get scorers. eventresults.php and
lookuplineup.php do not carry goal/scorer info on the free tier
(eventresults always returns {"results": null}; lineup has no goal markers),
so lookuptimeline.php is the only usable source.

Some goals never show up in the timeline at all (TSDB data gap). For those,
manual_scorers.json holds hand-checked additions keyed by TSDB event id,
merged in and sorted by minute.
"""

import json
import os
import re

import requests

_BASE = "https://www.thesportsdb.com/api/v1/json/123"
_MANUAL_SCORERS_PATH = os.path.join(os.path.dirname(__file__), "manual_scorers.json")


def _load_manual_scorers() -> dict:
    try:
        with open(_MANUAL_SCORERS_PATH, encoding="utf-8") as fh:
            return json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _sort_by_minute(scorers: list[str]) -> list[str]:
    def minute(label: str) -> int:
        m = re.match(r"(\d+)", label)
        return int(m.group(1)) if m else 0
    return sorted(scorers, key=minute)


def _norm(name: str) -> str:
    s = name.lower()
    for tok in ("fc", "afc", "sc", "cf", "ac", "fk",
                "national football team", "national team"):
        s = s.replace(tok, "")
    return " ".join(s.split())


def _match(a: str, b: str) -> bool:
    na, nb = _norm(a), _norm(b)
    return na == nb or na in nb or nb in na


def scorers_by_id(event_id: str) -> tuple[list[str], list[str]]:
    """Fetch scorers directly by TSDB event id. Returns ([], []) on any error."""
    sh, sa = [], []
    try:
        r = requests.get(f"{_BASE}/lookuptimeline.php",
                         params={"id": str(event_id)}, timeout=10)
        r.raise_for_status()
        timeline = r.json().get("timeline") or []

        # strHome: "Yes" = home team scored, "No" = away team scored
        for item in timeline:
            if (item.get("strTimeline") or "").strip().lower() != "goal":
                continue
            player = (item.get("strPlayer") or "").strip()
            if not player:
                continue
            minute  = (item.get("intTime") or "").strip()
            is_home = (item.get("strHome") or "").strip().lower() == "yes"
            label   = f"{minute}' {player}" if minute else player

            if is_home:
                sh.append(label)
            else:
                sa.append(label)
    except Exception:
        pass

    manual = _load_manual_scorers().get(str(event_id))
    if manual:
        sh.extend(manual.get("home", []))
        sa.extend(manual.get("away", []))

    return _sort_by_minute(sh), _sort_by_minute(sa)


def _find_event_id(home: str, away: str, date_str: str) -> str | None:
    """Search TSDB for a soccer event by team names on a given UTC date."""
    try:
        r = requests.get(f"{_BASE}/eventsday.php",
                         params={"d": date_str, "s": "Soccer"}, timeout=10)
        r.raise_for_status()
        for ev in (r.json().get("events") or []):
            if (_match(home, ev.get("strHomeTeam", "")) and
                    _match(away, ev.get("strAwayTeam", ""))):
                return ev.get("idEvent")
    except Exception:
        pass
    return None


def scorers_by_teams(home: str, away: str, date_str: str) -> tuple[list[str], list[str]]:
    """Find event by team names + date, return scorers. Graceful fallback to ([], [])."""
    eid = _find_event_id(home, away, date_str)
    if not eid:
        return [], []
    return scorers_by_id(eid)
