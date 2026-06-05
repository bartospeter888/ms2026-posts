#!/usr/bin/env python3
"""
generate_page.py — Čte matches.json a generuje docs/index.html se všemi match kartami.
Vlajky hledá nejdřív v docs/assets/flags/{ISO_UPPER}.png, fallback na flagcdn.com CDN.
"""

import json
import os
import sys
from datetime import datetime, timezone

ROOT      = os.path.join(os.path.dirname(__file__), "..")
MATCHES   = os.path.join(ROOT, "matches.json")
FLAGS_DIR = os.path.join(ROOT, "docs", "assets", "flags")
OUTPUT    = os.path.join(ROOT, "docs", "index.html")

# Relative paths from docs/ for assets served by GitHub Pages
ASSET_BASE = "assets"

sys.path.insert(0, os.path.dirname(__file__))
from flag_map import tla_to_iso

# ── Stage labels ─────────────────────────────────────────────────────────────
STAGE_LABELS = {
    "GROUP_STAGE":          "Skupinová fáze",
    "LAST_32":              "Osmifinále",
    "LAST_16":              "Osmifinále",
    "QUARTER_FINALS":       "Čtvrtfinále",
    "SEMI_FINALS":          "Semifinále",
    "THIRD_PLACE":          "O 3. místo",
    "FINAL":                "Finále",
}


def flag_path(tla: str) -> str:
    """Return relative path from docs/ for the flag image."""
    iso = tla_to_iso(tla)
    if not iso:
        return ""
    local = os.path.join(FLAGS_DIR, f"{iso.upper()}.png")
    if os.path.exists(local):
        return f"{ASSET_BASE}/flags/{iso.upper()}.png"
    # CDN fallback
    return f"https://flagcdn.com/w320/{iso}.png"


def format_date(utc_str: str) -> str:
    """Convert UTC ISO date to Czech-style date."""
    try:
        dt = datetime.fromisoformat(utc_str.replace("Z", "+00:00"))
        months = ["", "ledna", "února", "března", "dubna", "května", "června",
                  "července", "srpna", "září", "října", "listopadu", "prosince"]
        return f"{dt.day}. {months[dt.month]} {dt.year}"
    except Exception:
        return utc_str[:10]


def stage_label(stage: str, group: str | None, matchday: int | None) -> str:
    label = STAGE_LABELS.get(stage, stage.replace("_", " ").title())
    if group:
        group_clean = group.replace("GROUP_", "Skupina ")
        label = f"{group_clean} · {label}"
    if matchday:
        label += f" · Hrací den {matchday}"
    return label.upper()


def build_scorers_html(scorers_home: list, scorers_away: list) -> str:
    has_data = bool(scorers_home or scorers_away)
    empty_cls = "" if has_data else " empty"

    def scorer_item(s):
        # Try to highlight the minute in red (e.g. "Mbappé 45'")
        parts = s.rsplit("'", 1)
        if len(parts) == 2 and parts[1] == "" and "'" in s:
            name_part, min_part = s.rsplit(" ", 1)
            return f'<div class="scorer-item">{esc(name_part)} <span class="min">{esc(min_part)}</span></div>'
        return f'<div class="scorer-item">{esc(s)}</div>'

    home_html = "\n".join(scorer_item(s) for s in scorers_home)
    away_html = "\n".join(scorer_item(s) for s in scorers_away)

    return f'''<div class="scorers-section{empty_cls}">
  <div class="scorers-col">{home_html}</div>
  <div class="scorers-icon">⚽</div>
  <div class="scorers-col scorers-right">{away_html}</div>
</div>'''


def build_caption(match: dict) -> str:
    home      = match["home"]["shortName"] or match["home"]["name"]
    away      = match["away"]["shortName"] or match["away"]["name"]
    sc_h      = match["score"]["home"]
    sc_a      = match["score"]["away"]
    date_str  = format_date(match.get("utcDate", ""))
    stage     = STAGE_LABELS.get(match.get("stage", ""), "MS 2026")
    group     = (match.get("group") or "").replace("GROUP_", "Skupina ")

    scorers_h = match.get("scorers_home", [])
    scorers_a = match.get("scorers_away", [])

    scorers_lines = ""
    if scorers_h or scorers_a:
        scorers_lines = "\n\n⚽ Střelci:\n"
        for s in scorers_h:
            scorers_lines += f"  {home}: {s}\n"
        for s in scorers_a:
            scorers_lines += f"  {away}: {s}\n"

    group_line = f"{group} | " if group else ""
    tags = f"#MS2026 #WorldCup2026 #{home.replace(' ','')} #{away.replace(' ','')} #FPL #FPLAddicted"

    return (
        f"⚽ VÝSLEDEK | {home.upper()} {sc_h}:{sc_a} {away.upper()}\n"
        f"📅 {date_str} | {group_line}{stage}"
        f"{scorers_lines}\n\n"
        f"💎 Top fantasy hráč: ___\n\n"
        f"🔮 Sleduj FPL Addicted pro tipy na WC fantasy ligu!\n\n"
        f"—\n"
        f"{tags}"
    )


def esc(s) -> str:
    """HTML-escape a string."""
    return (str(s)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def build_card_html(match: dict) -> str:
    mid       = str(match["id"])
    home      = match["home"]
    away      = match["away"]
    sc_h      = match["score"]["home"]
    sc_a      = match["score"]["away"]
    score_h   = str(sc_h) if sc_h is not None else "?"
    score_a   = str(sc_a) if sc_a is not None else "?"

    home_name  = esc(home["shortName"] or home["name"])
    away_name  = esc(away["shortName"] or away["name"])
    home_flag  = flag_path(home["tla"])
    away_flag  = flag_path(away["tla"])
    caption    = esc(build_caption(match))

    return f'''<div class="match-section">

  <div class="card-wrapper" id="wrapper-{mid}">
    <div class="card" id="card-{mid}" data-match-id="{mid}">

      <!-- Full-bleed photo background -->
      <div class="photo-zone" id="pz-{mid}">
        <div class="photo-placeholder" id="pp-{mid}">
          <div class="photo-placeholder-icon">📷</div>
          <div>Klepni pro nahrání fotky</div>
        </div>
        <img class="player-photo" id="pi-{mid}" draggable="false" alt="">
      </div>

      <!-- Dark gradient overlay -->
      <div class="gradient-overlay"></div>

      <!-- Top logos -->
      <div class="top-logos">
        <img class="logo-wc"  src="assets/logos/wc2026.png"       alt="FIFA WC 2026">
        <img class="logo-fpl" src="assets/logos/fpl_addicted.png"  alt="FPL Addicted">
      </div>

      <!-- Score section -->
      <div class="score-section">
        <div class="team-block">
          <img class="team-flag" src="{home_flag}" alt="{home_name}">
          <div class="team-name">{home_name}</div>
        </div>
        <div class="score-center">
          <span class="score-num">{score_h}</span>
          <div class="score-vline"></div>
          <span class="score-num">{score_a}</span>
        </div>
        <div class="team-block">
          <img class="team-flag" src="{away_flag}" alt="{away_name}">
          <div class="team-name">{away_name}</div>
        </div>
      </div>

    </div><!-- /card -->
  </div><!-- /card-wrapper -->

  <input type="file" accept="image/*" id="file-{mid}" style="display:none">

  <div class="controls">
    <button class="btn btn-upload" onclick="document.getElementById('file-{mid}').click()">
      📷 Nahrát fotku
    </button>
    <button class="btn btn-export" id="export-btn-{mid}" onclick="exportCard('{mid}')">
      ⬇️ Stáhnout PNG
    </button>
  </div>

  <div class="caption-box">
    <div class="caption-label">Caption ke zkopírování:</div>
    <textarea class="caption-textarea" id="caption-{mid}">{caption}</textarea>
    <button class="btn-copy" id="copy-btn-{mid}" onclick="copyCaption('{mid}')">
      📋 Kopírovat caption
    </button>
  </div>

</div><!-- /match-section -->
<div class="match-divider"></div>
'''


HTML_HEAD = '''\
<!DOCTYPE html>
<html lang="cs">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<title>MS 2026 – FPL Addicted Výsledky</title>
<link rel="stylesheet" href="assets/style.css">
<!-- dom-to-image (primary PNG export) -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/dom-to-image/2.6.0/dom-to-image.min.js"></script>
<!-- html2canvas (fallback) -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
</head>
<body>
'''

HTML_FOOT = '''\
<script src="assets/app.js"></script>
</body>
</html>
'''


def main():
    if not os.path.exists(MATCHES):
        print(f"ERROR: {MATCHES} not found — run fetch_matches.py first", file=sys.stderr)
        sys.exit(1)

    with open(MATCHES, encoding="utf-8") as fh:
        data = json.load(fh)

    matches   = data.get("matches", [])
    date_str  = data.get("date", "")

    # Format date for display
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        months = ["", "ledna", "února", "března", "dubna", "května", "června",
                  "července", "srpna", "září", "října", "listopadu", "prosince"]
        display_date = f"{dt.day}. {months[dt.month]} {dt.year}"
    except Exception:
        display_date = date_str

    # Build page
    html = HTML_HEAD
    html += f'''<div class="page-header">
  <h1>⚽ MS 2026 · Výsledky</h1>
  <div class="date-label">{esc(display_date)}</div>
</div>\n'''

    if not matches:
        html += '<div class="no-matches">Dnes žádné odehrané zápasy ⚽</div>\n'
    else:
        for m in matches:
            html += build_card_html(m)

    html += HTML_FOOT

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as fh:
        fh.write(html)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M UTC")
    print(f"Generated {len(matches)} card(s) -> {OUTPUT}  [{generated_at}]")


if __name__ == "__main__":
    main()
