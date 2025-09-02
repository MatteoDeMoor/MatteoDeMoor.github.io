// Utility: infer attributes from a shirt section
function inferAttributes(section) {
  const title = section.querySelector('h3')?.textContent || '';
  const playerText = section.querySelector('.player-info')?.textContent || '';
  const seasonMatch = title.match(/(\d{4}-\d{4})/);
  const typeMatch = title.match(/Home|Away|Third|Fourth|GK ?\d?/i);
  const sizeMatch = title.match(/Size:\s*([A-Z]{1,3})/i);
  const playerMatch = playerText.match(/Player:\s*([^\-]+)/i);

  if (seasonMatch) section.dataset.season = seasonMatch[1];
  if (typeMatch) {
    const raw = (typeMatch[0] || '').toLowerCase();
    // Normalize GK 1/2/3 -> gk; others keep as-is
    const base = /gk/.test(raw) ? 'gk' : raw;
    section.dataset.type = raw;
    section.dataset.typeBase = base;
  }
  if (sizeMatch) section.dataset.size = sizeMatch[1].toUpperCase();
  if (playerMatch) {
    const label = playerMatch[1].trim();
    section.dataset.player = label.toLowerCase();
    section.dataset.playerLabel = label; // preserve original casing for UI
  }
}

function byAlpha(a, b) { return a.localeCompare(b, undefined, { sensitivity: 'base' }); }

function sortSizes(arr) {
  const order = ['XS','S','M','L','XL','XXL','XXXL'];
  return Array.from(arr).sort((a,b) => {
    const ia = order.indexOf(a);
    const ib = order.indexOf(b);
    if (ia === -1 && ib === -1) return byAlpha(a,b);
    if (ia === -1) return 1;
    if (ib === -1) return -1;
    return ia - ib;
  });
}

function setupFiltering() {
  const seasonSel = document.getElementById('filter-season');
  const typeSel = document.getElementById('filter-type');
  const sizeSel = document.getElementById('filter-size');
  const playerSel = document.getElementById('filter-player');
  const clearBtn = document.getElementById('filter-clear');
  const sections = Array.from(document.querySelectorAll('.shirt-section'));

  // Initialize data attributes
  sections.forEach(inferAttributes);

  // Build unique option sets from DOM
  const seasons = new Set();
  const typesBase = new Set();
  const sizes = new Set();
  const playersMap = new Map(); // key: lower, val: label

  sections.forEach(sec => {
    if (sec.dataset.season) seasons.add(sec.dataset.season);
    if (sec.dataset.typeBase) typesBase.add(sec.dataset.typeBase);
    if (sec.dataset.size) sizes.add(sec.dataset.size);
    if (sec.dataset.player) playersMap.set(sec.dataset.player, sec.dataset.playerLabel || sec.dataset.player);
  });

  // Populate selects
  if (seasonSel) {
    // Multi-select: no default selection -> show all
    [...Array.from(seasons).sort((a,b)=>byAlpha(b,a))] // reverse alpha (newer first like 2024-2025)
      .forEach(season => {
        const opt = document.createElement('option');
        opt.value = season;
        opt.textContent = season;
        seasonSel.appendChild(opt);
      });
  }

  if (typeSel) {
    const addAll = document.createElement('option');
    addAll.value = '';
    addAll.textContent = 'All types';
    typeSel.appendChild(addAll);
    Array.from(typesBase).sort(byAlpha).forEach(t => {
      const opt = document.createElement('option');
      opt.value = t; // already normalized (home/away/third/fourth/gk)
      opt.textContent = t.charAt(0).toUpperCase() + t.slice(1);
      typeSel.appendChild(opt);
    });
  }

  if (sizeSel) {
    const addAll = document.createElement('option');
    addAll.value = '';
    addAll.textContent = 'All sizes';
    sizeSel.appendChild(addAll);
    sortSizes(sizes).forEach(z => {
      const opt = document.createElement('option');
      opt.value = z;
      opt.textContent = z;
      sizeSel.appendChild(opt);
    });
  }

  if (playerSel) {
    Array.from(playersMap.entries())
      .sort((a,b)=>byAlpha(a[1], b[1]))
      .forEach(([key,label]) => {
        const opt = document.createElement('option');
        opt.value = key; // lower-case key
        opt.textContent = label; // display label
        playerSel.appendChild(opt);
      });
  }

  function getMultiSelectedValues(selectEl) {
    return Array.from(selectEl?.selectedOptions || []).map(o => o.value).filter(Boolean);
  }

  function applyFilter() {
    const seasonsSelected = seasonSel ? getMultiSelectedValues(seasonSel) : [];
    const typeValue = (typeSel?.value || '').toLowerCase();
    const sizeValue = (sizeSel?.value || '').toUpperCase();
    const playersSelected = playerSel ? getMultiSelectedValues(playerSel) : [];

    sections.forEach(sec => {
      const okSeason = seasonsSelected.length === 0 || seasonsSelected.includes(sec.dataset.season || '');
      const okType = !typeValue || (sec.dataset.typeBase || '') === typeValue;
      const okSize = !sizeValue || (sec.dataset.size || '') === sizeValue;
      const okPlayer = playersSelected.length === 0 || playersSelected.includes(sec.dataset.player || '');
      sec.style.display = (okSeason && okType && okSize && okPlayer) ? '' : 'none';
    });
  }

  [seasonSel, typeSel, sizeSel, playerSel].forEach(sel => {
    if (!sel) return;
    sel.addEventListener('change', applyFilter);
  });

  clearBtn?.addEventListener('click', () => {
    if (seasonSel) Array.from(seasonSel.options).forEach(o => (o.selected = false));
    if (typeSel) typeSel.value = '';
    if (sizeSel) sizeSel.value = '';
    if (playerSel) Array.from(playerSel.options).forEach(o => (o.selected = false));
    applyFilter();
  });

  // Initial apply to respect any default selections
  applyFilter();
}

function setupLightbox() {
  const overlay = document.createElement('div');
  overlay.className = 'lightbox-overlay';
  overlay.innerHTML = `
    <div class="lightbox-content">
      <button class="lightbox-close" aria-label="Close">✕</button>
      <button class="lightbox-prev" aria-label="Previous">‹</button>
      <img class="lightbox-img" alt="Shirt image"/>
      <button class="lightbox-next" aria-label="Next">›</button>
    </div>
  `;
  document.body.appendChild(overlay);

  const imgEl = overlay.querySelector('.lightbox-img');
  const btnClose = overlay.querySelector('.lightbox-close');
  const btnPrev = overlay.querySelector('.lightbox-prev');
  const btnNext = overlay.querySelector('.lightbox-next');

  let currentList = [];
  let currentIndex = 0;

  function open(list, index) {
    currentList = list;
    currentIndex = index;
    imgEl.src = currentList[currentIndex].src;
    overlay.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
  function close() {
    overlay.classList.remove('open');
    document.body.style.overflow = '';
  }
  function show(delta) {
    if (!currentList.length) return;
    currentIndex = (currentIndex + delta + currentList.length) % currentList.length;
    imgEl.src = currentList[currentIndex].src;
  }

  btnClose.addEventListener('click', close);
  btnPrev.addEventListener('click', () => show(-1));
  btnNext.addEventListener('click', () => show(1));
  overlay.addEventListener('click', (e) => { if (e.target === overlay) close(); });
  window.addEventListener('keydown', (e) => {
    if (!overlay.classList.contains('open')) return;
    if (e.key === 'Escape') close();
    if (e.key === 'ArrowLeft') show(-1);
    if (e.key === 'ArrowRight') show(1);
  });

  // Wire images
  document.querySelectorAll('.shirt-section').forEach(section => {
    const imgs = Array.from(section.querySelectorAll('.photo img'));
    imgs.forEach((img, idx) => {
      img.style.cursor = 'zoom-in';
      img.addEventListener('click', () => open(imgs, idx));
    });
  });
}

document.addEventListener('DOMContentLoaded', () => {
  setupFiltering();
  setupLightbox();
});
