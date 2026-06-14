/* MS 2026 — FPL Addicted: photo upload, drag/zoom, PNG export */
'use strict';

// ── Scale cards to fit screen on load and resize ─────────────────────────────
function scaleCards() {
  document.querySelectorAll('.card-wrapper').forEach(wrapper => {
    const maxW = Math.min(window.innerWidth - 32, 1080);
    const scale = maxW / 1080;
    const card = wrapper.querySelector('.card');
    if (!card) return;
    card.style.transform = `scale(${scale})`;
    wrapper.style.width  = `${1080 * scale}px`;
    wrapper.style.height = `${1350 * scale}px`;
    wrapper.dataset.scale = scale;
  });
}
window.addEventListener('load', scaleCards);
window.addEventListener('resize', scaleCards);


// ── Per-card photo interaction ────────────────────────────────────────────────
function initCard(matchId) {
  const input       = document.getElementById(`file-${matchId}`);
  const zone        = document.getElementById(`pz-${matchId}`);
  const placeholder = document.getElementById(`pp-${matchId}`);
  const img         = document.getElementById(`pi-${matchId}`);
  const wrapper     = zone.closest('.card-wrapper');

  if (!input || !zone || !img) return;

  // State for the photo transform (in card-CSS-pixels)
  const state = { x: 0, y: 0, scale: 1 };

  function applyTransform() {
    img.style.transform =
      `translate(calc(-50% + ${state.x}px), calc(-50% + ${state.y}px)) scale(${state.scale})`;
  }

  function getDisplayScale() {
    return parseFloat(wrapper?.dataset.scale || '1') || 1;
  }

  // ── Load photo ──────────────────────────────────────────────────────────────
  input.addEventListener('change', e => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      img.src = reader.result;
      img.onload = () => {
        // Center the image and fill the photo zone (cover fit)
        const zoneW = zone.clientWidth;   // in CSS card-px (1080px scale)
        const zoneH = zone.clientHeight;
        const natW  = img.naturalWidth;
        const natH  = img.naturalHeight;
        const fillScale = Math.max(zoneW / natW, zoneH / natH);
        img.style.width  = `${natW * fillScale}px`;
        img.style.height = `${natH * fillScale}px`;
        img.style.left   = '50%';
        img.style.top    = '50%';
        state.x = 0; state.y = 0; state.scale = 1;
        applyTransform();
        img.style.display         = 'block';
        placeholder.style.display = 'none';
      };
    };
    reader.readAsDataURL(file);
  });

  // Tap on zone / placeholder → open file picker
  zone.addEventListener('click', e => {
    if (e.target === placeholder || placeholder.contains(e.target) || e.target === zone) {
      input.click();
    }
  });

  // ── Touch drag & pinch-zoom ─────────────────────────────────────────────────
  let drag  = { active: false, startX: 0, startY: 0, startTX: 0, startTY: 0 };
  let pinch = { active: false, startDist: 0, startScale: 1 };

  function touchDist(t) {
    const dx = t[0].clientX - t[1].clientX;
    const dy = t[0].clientY - t[1].clientY;
    return Math.hypot(dx, dy);
  }

  zone.addEventListener('touchstart', e => {
    if (!img.src) return;
    e.preventDefault();
    const ds = getDisplayScale();
    if (e.touches.length === 1) {
      drag.active = true;
      drag.startX  = e.touches[0].clientX;
      drag.startY  = e.touches[0].clientY;
      drag.startTX = state.x;
      drag.startTY = state.y;
      pinch.active = false;
    } else if (e.touches.length === 2) {
      pinch.active     = true;
      pinch.startDist  = touchDist(e.touches);
      pinch.startScale = state.scale;
      drag.active      = false;
    }
  }, { passive: false });

  zone.addEventListener('touchmove', e => {
    if (!img.src) return;
    e.preventDefault();
    const ds = getDisplayScale();
    if (drag.active && e.touches.length === 1) {
      state.x = drag.startTX + (e.touches[0].clientX - drag.startX) / ds;
      state.y = drag.startTY + (e.touches[0].clientY - drag.startY) / ds;
      applyTransform();
    } else if (pinch.active && e.touches.length === 2) {
      const dist    = touchDist(e.touches);
      state.scale   = Math.max(0.3, Math.min(6, pinch.startScale * (dist / pinch.startDist)));
      applyTransform();
    }
  }, { passive: false });

  zone.addEventListener('touchend',   () => { drag.active = false; pinch.active = false; });
  zone.addEventListener('touchcancel',() => { drag.active = false; pinch.active = false; });

  // ── Mouse drag (desktop) ────────────────────────────────────────────────────
  let md = { down: false, startX: 0, startY: 0, startTX: 0, startTY: 0 };
  zone.addEventListener('mousedown', e => {
    if (!img.src || e.button !== 0) return;
    md.down = true; md.startX = e.clientX; md.startY = e.clientY;
    md.startTX = state.x; md.startTY = state.y;
    e.preventDefault();
  });
  document.addEventListener('mousemove', e => {
    if (!md.down) return;
    const ds = getDisplayScale();
    state.x = md.startTX + (e.clientX - md.startX) / ds;
    state.y = md.startTY + (e.clientY - md.startY) / ds;
    applyTransform();
  });
  document.addEventListener('mouseup', () => { md.down = false; });

  // Mouse wheel zoom
  zone.addEventListener('wheel', e => {
    if (!img.src) return;
    e.preventDefault();
    const factor = e.deltaY > 0 ? 0.9 : 1.1;
    state.scale = Math.max(0.3, Math.min(6, state.scale * factor));
    applyTransform();
  }, { passive: false });
}

// Init all cards after DOM ready
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.card[data-match-id]').forEach(card => {
    initCard(card.dataset.matchId);
  });
});


// ── Inline all <img> as base64 before export (fixes CORS issues) ─────────────
async function inlineImages(root) {
  const imgs  = Array.from(root.querySelectorAll('img[src]'));
  const saved = imgs.map(img => img.src);
  await Promise.all(imgs.map(async img => {
    const src = img.src;
    if (!src || src.startsWith('data:') || src.startsWith('blob:')) return;
    try {
      const res  = await fetch(src);
      const blob = await res.blob();
      img.src    = await new Promise((ok, fail) => {
        const r = new FileReader();
        r.onload  = () => ok(r.result);
        r.onerror = fail;
        r.readAsDataURL(blob);
      });
    } catch { /* leave src as-is if fetch fails */ }
  }));
  return () => imgs.forEach((img, i) => { img.src = saved[i]; });
}

// ── Flatten the photo (with its drag/zoom transform) into a plain, untransformed
// <img> covering the photo zone. html2canvas/dom-to-image render a CSS
// transform with calc() on an oversized <img> inconsistently across mobile
// browsers (works in Safari, blank in Chrome) — drawing it onto a canvas
// first with getBoundingClientRect()-derived geometry sidesteps that entirely.
function flattenPhoto(zone, img) {
  if (!img.src || img.style.display === 'none') return null;
  const zoneRect = zone.getBoundingClientRect();
  const imgRect  = img.getBoundingClientRect();
  const canvas = document.createElement('canvas');
  canvas.width  = Math.round(zoneRect.width);
  canvas.height = Math.round(zoneRect.height);
  const ctx = canvas.getContext('2d');
  ctx.drawImage(
    img,
    imgRect.left - zoneRect.left,
    imgRect.top  - zoneRect.top,
    imgRect.width,
    imgRect.height
  );
  return canvas.toDataURL('image/png');
}

// ── PNG export ────────────────────────────────────────────────────────────────
async function exportCard(matchId) {
  const card = document.getElementById(`card-${matchId}`);
  const btn  = document.getElementById(`export-btn-${matchId}`);
  const zone = document.getElementById(`pz-${matchId}`);
  const img  = document.getElementById(`pi-${matchId}`);
  if (!card || !btn) return;

  btn.disabled    = true;
  btn.textContent = '⏳ Exportuji…';

  // Remove display transform + inline external images before capture
  const savedTransform = card.style.transform;
  card.style.transform = 'none';
  const restore = await inlineImages(card);

  // Flatten the photo into a plain full-cover <img> with no transform
  const savedImgStyle = img ? img.getAttribute('style') : null;
  const savedImgSrc   = img ? img.src : null;
  const flat = (zone && img) ? flattenPhoto(zone, img) : null;
  if (flat) {
    img.src = flat;
    img.style.cssText = 'position:absolute; inset:0; width:100%; height:100%; transform:none;';
  }

  try {
    // html2canvas draws each element via canvas APIs directly, which handles
    // <img> photo elements with data: URLs far more reliably on mobile
    // browsers than dom-to-image's SVG-foreignObject approach (which can
    // silently drop the photo on mobile Safari).
    const canvas = await html2canvas(card, {
      width: 1080, height: 1350,
      scale: 1, useCORS: true, allowTaint: false,
      backgroundColor: '#0d1b3e',
      logging: false,
    });
    await new Promise((resolve, reject) => {
      canvas.toBlob(blob => {
        if (!blob) { reject(new Error('toBlob returned null')); return; }
        const url = URL.createObjectURL(blob);
        const a   = document.createElement('a');
        a.href = url; a.download = `ms2026_${matchId}.png`;
        a.click();
        URL.revokeObjectURL(url);
        resolve();
      }, 'image/png');
    });
  } catch (err) {
    console.warn('html2canvas failed, trying dom-to-image:', err);
    try {
      // imagePlaceholder: transparent 1px — prevents reject on any remaining CORS failures
      const dataUrl = await domtoimage.toPng(card, {
        width: 1080, height: 1350,
        imagePlaceholder: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAC0lEQVQI12NgAAIABQAABjE+ibYAAAAASUVORK5CYII=',
      });
      const a = document.createElement('a');
      a.href     = dataUrl;
      a.download = `ms2026_${matchId}.png`;
      a.click();
    } catch (err2) {
      alert('Export se nezdařil. Zkus screenshot telefonu.');
      console.error(err2);
    }
  } finally {
    restore();
    if (flat) {
      img.src = savedImgSrc;
      img.setAttribute('style', savedImgStyle);
    }
    card.style.transform = savedTransform;
    btn.disabled    = false;
    btn.textContent = '⬇️ Stáhnout PNG';
  }
}


// ── Copy caption ──────────────────────────────────────────────────────────────
function copyCaption(matchId) {
  const textarea = document.getElementById(`caption-${matchId}`);
  const btn      = document.getElementById(`copy-btn-${matchId}`);
  if (!textarea || !btn) return;

  navigator.clipboard.writeText(textarea.value).then(() => {
    btn.textContent = '✅ Zkopírováno!';
    btn.classList.add('copied');
    setTimeout(() => {
      btn.textContent = '📋 Kopírovat caption';
      btn.classList.remove('copied');
    }, 2000);
  }).catch(() => {
    // Fallback for browsers that block clipboard API
    textarea.select();
    document.execCommand('copy');
    btn.textContent = '✅ Zkopírováno!';
    setTimeout(() => { btn.textContent = '📋 Kopírovat caption'; }, 2000);
  });
}
