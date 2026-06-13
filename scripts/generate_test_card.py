#!/usr/bin/env python3
"""Generate a standalone test card HTML with the new fade design. Brazil 2-0 Morocco."""

import base64, os

ROOT      = os.path.join(os.path.dirname(__file__), "..")
FLAGS_DIR = os.path.join(ROOT, "docs", "assets", "flags")
LOGOS_DIR = os.path.join(ROOT, "docs", "assets", "logos")
OUTPUT    = os.path.join(ROOT, "docs", "test_card.html")


def b64(path: str) -> str:
    ext  = path.rsplit(".", 1)[-1].lower()
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp"}.get(ext, "image/png")
    with open(path, "rb") as fh:
        data = base64.b64encode(fh.read()).decode()
    return f"data:{mime};base64,{data}"


wc_logo  = b64(os.path.join(LOGOS_DIR, "wc2026.png"))
fpl_logo = b64(os.path.join(LOGOS_DIR, "fpl_addicted.png"))
br_flag  = b64(os.path.join(FLAGS_DIR, "BR.png"))
ma_flag  = b64(os.path.join(FLAGS_DIR, "MA.png"))

HTML = f"""<!DOCTYPE html>
<html lang="cs">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<meta name="apple-mobile-web-app-capable" content="yes">
<title>Test karta — MS 2026</title>
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Barlow+Condensed:wght@900&family=Barlow:wght@400;700&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/dom-to-image/2.6.0/dom-to-image.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<style>
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

body {{
  background: #0a0a0a;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 0 60px;
  font-family: 'Barlow', sans-serif;
}}

/* ── Card wrapper ───────────────────────────────── */
.card-wrapper {{
  position: relative;
  overflow: hidden;
}}

/* ── THE CARD — 1080×1350 CSS px ────────────────── */
.card {{
  width: 1080px;
  height: 1350px;
  position: relative;
  overflow: hidden;
  background: #0d1b3e;
  transform-origin: top left;
}}

/* ── Photo zone — full bleed background ─────────── */
.photo-zone {{
  position: absolute;
  inset: 0;
  overflow: hidden;
  cursor: grab;
}}
.photo-zone:active {{ cursor: grabbing; }}

.photo-placeholder {{
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20px;
  color: rgba(255,255,255,0.2);
  pointer-events: none;
  font-size: 32px;
  letter-spacing: 0.05em;
}}
.photo-placeholder-icon {{ font-size: 100px; }}

.player-photo {{
  position: absolute;
  top: 50%;
  left: 50%;
  transform-origin: center center;
  pointer-events: none;
  user-select: none;
  -webkit-user-drag: none;
  max-width: none;
  max-height: none;
  display: none;
}}

/* ── Subtle black gradient — bottom only ─────────── */
.gradient-overlay {{
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to bottom,
    rgba(0,0,0,0)    0%,
    rgba(0,0,0,0)   42%,
    rgba(0,0,0,0.22) 54%,
    rgba(0,0,0,0.55) 66%,
    rgba(0,0,0,0.78) 78%,
    rgba(0,0,0,0.82) 88%,
    rgba(0,0,0,0.74) 100%
  );
  pointer-events: none;
}}

/* ── Top logos ───────────────────────────────────── */
.top-logos {{
  position: absolute;
  top: 40px;
  left: 0; right: 0;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 0 44px;
  pointer-events: none;
  z-index: 10;
}}
.logo-wc {{
  height: 160px;
  width: auto;
  filter: drop-shadow(0 2px 16px rgba(0,0,0,0.55));
}}
.logo-fpl {{
  height: 150px;
  width: auto;
  filter: drop-shadow(0 2px 16px rgba(0,0,0,0.65));
}}

/* ── Score section — blíž ke spodku ─────────────── */
.score-section {{
  position: absolute;
  bottom: 150px;
  left: 0; right: 0;
  display: flex;
  align-items: flex-start;
  padding: 0 56px;
  z-index: 10;
  pointer-events: none;
}}
.team-block {{
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  gap: 12px;
}}
.team-flag {{
  display: block;
  width: 173px;
  height: 115px;
  object-fit: cover;
  border-radius: 9px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.55);
  margin: 0 auto;
}}
.team-name {{
  font-family: 'Barlow Condensed', sans-serif;
  font-weight: 900;
  font-size: 43px;
  color: #fff;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  text-align: center;
  text-shadow: 0 2px 10px rgba(0,0,0,0.8);
  -webkit-text-stroke: 5px #5B2D8E;
  paint-order: stroke fill;
  width: 100%;
}}
.score-center {{
  display: flex;
  align-items: center;
  gap: 20px;
  flex-shrink: 0;
  padding-top: 8px;
}}
.score-num {{
  font-family: 'Anton', sans-serif;
  font-size: 210px;
  color: #fff;
  line-height: 0.88;
  min-width: 120px;
  text-align: center;
  text-shadow:
     1.5px  0    0 #fff,
    -1.5px  0    0 #fff,
     0      1.5px 0 #fff,
     0     -1.5px 0 #fff,
     1.5px  1.5px 0 #fff,
    -1.5px  1.5px 0 #fff,
     1.5px -1.5px 0 #fff,
    -1.5px -1.5px 0 #fff,
     10px  0    0 #5B2D8E,
    -10px  0    0 #5B2D8E,
     0     10px 0 #5B2D8E,
     0    -10px 0 #5B2D8E,
     10px  10px 0 #5B2D8E,
    -10px  10px 0 #5B2D8E,
     10px -10px 0 #5B2D8E,
    -10px -10px 0 #5B2D8E,
     0 4px 28px rgba(0,0,0,0.5);
  -webkit-text-stroke: 9px #fff;
  paint-order: stroke fill;
}}
.score-vline {{
  width: 3px;
  height: 145px;
  background: rgba(255,255,255,0.28);
  border-radius: 2px;
  flex-shrink: 0;
}}


/* ── Scorers — inside .team-block ────────────────── */
.scorer-list {{
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  margin-top: 4px;
}}
.scorer-item {{
  font-family: 'Barlow Condensed', sans-serif;
  font-weight: 700;
  font-size: inherit;
  color: rgba(255,255,255,0.88);
  text-shadow: 0 1px 8px rgba(0,0,0,0.9);
  line-height: 1.25;
  letter-spacing: 0.02em;
  white-space: nowrap;
  text-align: center;
}}

/* ── Controls (outside card, not exported) ───────── */
.controls {{
  display: flex;
  gap: 12px;
  margin-top: 16px;
  flex-wrap: wrap;
  justify-content: center;
  padding: 0 16px;
  width: 100%;
  max-width: 560px;
}}
.btn {{
  padding: 14px 28px;
  border: none;
  border-radius: 12px;
  font-family: 'Barlow', sans-serif;
  font-weight: 700;
  font-size: 16px;
  cursor: pointer;
  flex: 1;
  min-width: 140px;
  letter-spacing: 0.04em;
  transition: opacity 0.15s;
}}
.btn:active {{ opacity: 0.8; }}
.btn:disabled {{ opacity: 0.4; cursor: not-allowed; }}
.btn-upload {{ background: #1e293b; color: #fff; }}
.btn-export {{ background: #C8001A; color: #fff; }}
</style>
</head>
<body>

<div class="card-wrapper" id="wrapper">
  <div class="card" id="card">

    <!-- Full-bleed photo background -->
    <div class="photo-zone" id="pz">
      <div class="photo-placeholder" id="pp">
        <div class="photo-placeholder-icon">📷</div>
        <div>Klepni pro nahrání fotky</div>
      </div>
      <img class="player-photo" id="pi" draggable="false" alt="">
    </div>

    <!-- Dark gradient overlay -->
    <div class="gradient-overlay"></div>

    <!-- Top logos -->
    <div class="top-logos">
      <img class="logo-wc"  src="{wc_logo}"  alt="FIFA WC 2026">
      <img class="logo-fpl" src="{fpl_logo}" alt="FPL Addicted">
    </div>

    <!-- Score section -->
    <div class="score-section">
      <div class="team-block">
        <img class="team-flag" src="{br_flag}" alt="Brazil">
        <div class="team-name">Brazil</div>
        <div class="scorer-list" style="font-size:26px">
          <div class="scorer-item">Vinicius Jr. 34', 67'</div>
        </div>
      </div>
      <div class="score-center">
        <span class="score-num">2</span>
        <div class="score-vline"></div>
        <span class="score-num">0</span>
      </div>
      <div class="team-block">
        <img class="team-flag" src="{ma_flag}" alt="Morocco">
        <div class="team-name">Morocco</div>
      </div>
    </div>

  </div><!-- /card -->
</div><!-- /card-wrapper -->

<input type="file" accept="image/*" id="file-input" style="display:none">

<div class="controls">
  <button class="btn btn-upload" onclick="document.getElementById('file-input').click()">📷 Nahrát fotku</button>
  <button class="btn btn-export" id="export-btn" onclick="exportCard()">⬇️ Stáhnout PNG</button>
</div>

<script>
'use strict';

// ── Scale card to fit screen ──────────────────────────────
function scaleCard() {{
  const maxW  = Math.min(window.innerWidth - 32, 1080);
  const scale = maxW / 1080;
  const card    = document.getElementById('card');
  const wrapper = document.getElementById('wrapper');
  card.style.transform  = `scale(${{scale}})`;
  wrapper.style.width   = `${{1080 * scale}}px`;
  wrapper.style.height  = `${{1350 * scale}}px`;
  wrapper._scale = scale;
}}
window.addEventListener('load',   scaleCard);
window.addEventListener('resize', scaleCard);

// ── Photo upload & drag/zoom ──────────────────────────────
const input = document.getElementById('file-input');
const zone  = document.getElementById('pz');
const ph    = document.getElementById('pp');
const img   = document.getElementById('pi');
const state = {{ x: 0, y: 0, scale: 1 }};

function getDisplayScale() {{
  return document.getElementById('wrapper')._scale || 1;
}}
function applyTransform() {{
  img.style.transform =
    `translate(calc(-50% + ${{state.x}}px), calc(-50% + ${{state.y}}px)) scale(${{state.scale}})`;
}}

input.addEventListener('change', e => {{
  const file = e.target.files[0];
  if (!file) return;
  img.src = URL.createObjectURL(file);
  img.onload = () => {{
    const zW = zone.clientWidth, zH = zone.clientHeight;
    const fillScale = Math.max(zW / img.naturalWidth, zH / img.naturalHeight);
    img.style.width  = `${{img.naturalWidth  * fillScale}}px`;
    img.style.height = `${{img.naturalHeight * fillScale}}px`;
    state.x = 0; state.y = 0; state.scale = 1;
    applyTransform();
    img.style.display = 'block';
    ph.style.display  = 'none';
  }};
}});

zone.addEventListener('click', e => {{
  if (img.style.display === 'none' || !img.src) input.click();
}});

// Touch
let drag  = {{ active: false, startX: 0, startY: 0, startTX: 0, startTY: 0 }};
let pinch = {{ active: false, startDist: 0, startScale: 1 }};

function dist(t) {{
  return Math.hypot(t[0].clientX - t[1].clientX, t[0].clientY - t[1].clientY);
}}
zone.addEventListener('touchstart', e => {{
  if (!img.src) return;
  e.preventDefault();
  const ds = getDisplayScale();
  if (e.touches.length === 1) {{
    drag = {{ active: true, startX: e.touches[0].clientX, startY: e.touches[0].clientY,
              startTX: state.x, startTY: state.y }};
    pinch.active = false;
  }} else if (e.touches.length === 2) {{
    pinch = {{ active: true, startDist: dist(e.touches), startScale: state.scale }};
    drag.active = false;
  }}
}}, {{ passive: false }});

zone.addEventListener('touchmove', e => {{
  if (!img.src) return;
  e.preventDefault();
  const ds = getDisplayScale();
  if (drag.active && e.touches.length === 1) {{
    state.x = drag.startTX + (e.touches[0].clientX - drag.startX) / ds;
    state.y = drag.startTY + (e.touches[0].clientY - drag.startY) / ds;
    applyTransform();
  }} else if (pinch.active && e.touches.length === 2) {{
    state.scale = Math.max(0.3, Math.min(6, pinch.startScale * (dist(e.touches) / pinch.startDist)));
    applyTransform();
  }}
}}, {{ passive: false }});

zone.addEventListener('touchend',    () => {{ drag.active = false; pinch.active = false; }});
zone.addEventListener('touchcancel', () => {{ drag.active = false; pinch.active = false; }});

// Mouse
let md = {{ down: false, startX: 0, startY: 0, startTX: 0, startTY: 0 }};
zone.addEventListener('mousedown', e => {{
  if (!img.src || e.button !== 0) return;
  md = {{ down: true, startX: e.clientX, startY: e.clientY, startTX: state.x, startTY: state.y }};
  e.preventDefault();
}});
document.addEventListener('mousemove', e => {{
  if (!md.down) return;
  const ds = getDisplayScale();
  state.x = md.startTX + (e.clientX - md.startX) / ds;
  state.y = md.startTY + (e.clientY - md.startY) / ds;
  applyTransform();
}});
document.addEventListener('mouseup', () => {{ md.down = false; }});
zone.addEventListener('wheel', e => {{
  if (!img.src) return;
  e.preventDefault();
  state.scale = Math.max(0.3, Math.min(6, state.scale * (e.deltaY > 0 ? 0.9 : 1.1)));
  applyTransform();
}}, {{ passive: false }});

// ── PNG Export ────────────────────────────────────────────
async function exportCard() {{
  const card = document.getElementById('card');
  const btn  = document.getElementById('export-btn');
  const savedTransform = card.style.transform;
  card.style.transform = 'none';
  btn.disabled = true;
  btn.textContent = '⏳ Exportuji…';
  try {{
    const url = await domtoimage.toPng(card, {{ width: 1080, height: 1350 }});
    const a = document.createElement('a');
    a.href = url; a.download = 'ms2026_karta.png'; a.click();
  }} catch(err) {{
    console.warn('dom-to-image failed, trying html2canvas:', err);
    try {{
      const canvas = await html2canvas(card, {{ width:1080, height:1350, scale:1, useCORS:true, logging:false }});
      canvas.toBlob(blob => {{
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob); a.download = 'ms2026_karta.png'; a.click();
      }}, 'image/png');
    }} catch(err2) {{
      alert('Export selhal. Zkus screenshot.');
    }}
  }} finally {{
    card.style.transform = savedTransform;
    btn.disabled = false;
    btn.textContent = '⬇️ Stáhnout PNG';
  }}
}}
</script>
</body>
</html>"""

with open(OUTPUT, "w", encoding="utf-8") as fh:
    fh.write(HTML)
print(f"Test card -> {OUTPUT}")
