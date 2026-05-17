// Utility: infer attributes from a shirt section
function normalizeSize(raw) {
  const cleaned = (raw || '').toUpperCase().replace(/\s+/g, '');
  const digitMatch = cleaned.match(/^(\d+)XL$/); // e.g. 2XL, 3XL ...
  if (digitMatch) {
    const count = parseInt(digitMatch[1], 10);
    if (Number.isFinite(count) && count > 0) {
      return {
        normalized: `${'X'.repeat(count)}L`, // 2XL -> XXL, 3XL -> XXXL, etc.
        label: `${count}XL`,
      };
    }
  }
  return { normalized: cleaned, label: cleaned };
}

function normalizeCollectibleValue(value) {
  const normalized = (value || '').trim().toLowerCase();
  return ['matchworn', 'signed', 'framed'].includes(normalized) ? normalized : 'regular';
}

function inferAttributes(section) {
  const title = section.querySelector('h3')?.textContent || '';
  const playerText = section.querySelector('.player-info')?.textContent || '';
  const seasonMatch = title.match(/(\d{4}-\d{4})/);
  const typeMatch = title.match(/Home|Away|Third|Fourth|GK ?\d?|Goalkeeper/i);
  // Capture size tokens like XS, S, M, L, XL, 2XL, 3XL, 4XL...
  const sizeMatch = title.match(/Size:\s*([0-9]+XL|[A-Z]{1,6})/i);
  const playerMatch = playerText.match(/Player:\s*([^\-]+)/i);
  const collectibleFromAttr = (section.dataset.collectible || '').trim().toLowerCase();
  const extraText = section.querySelector('.collectible-info')?.textContent || '';
  const collectibleFromText = /match[\s-]*worn/i.test(extraText) ? 'matchworn'
    : (/signed/i.test(extraText) ? 'signed'
      : (/framed/i.test(extraText) ? 'framed' : ''));
  const collectible = collectibleFromAttr || collectibleFromText;

  if (seasonMatch) {
    const label = seasonMatch[1];
    const expanded = expandSeasonLabel(label);
    section.dataset.seasonLabel = label;
    if (expanded.length) {
      section.dataset.seasons = expanded.join('|');
      section.dataset.season = expanded[0];
    } else {
      section.dataset.season = label;
    }
  }
  if (typeMatch) {
    const raw = (typeMatch[0] || '').toLowerCase();
    // Normalize GK/Goalkeeper variants to a single "gk" bucket; others keep as-is
    const base = /(gk|goalkeeper)/.test(raw) ? 'gk' : raw;
    section.dataset.type = raw;
    section.dataset.typeBase = base;
  }
  if (sizeMatch) {
    const { normalized, label } = normalizeSize(sizeMatch[1]);
    section.dataset.size = normalized;
    section.dataset.sizeLabel = label;
  }
  if (playerMatch) {
    const label = playerMatch[1].trim();
    section.dataset.player = label.toLowerCase();
    section.dataset.playerLabel = label; // preserve original casing for UI
  }
  section.dataset.collectible = normalizeCollectibleValue(collectible);
}

function byAlpha(a, b) { return a.localeCompare(b, undefined, { sensitivity: 'base' }); }

function expandSeasonLabel(label) {
  if (!label) return [];
  const parts = label.split('-');
  if (parts.length !== 2) return [label];
  const start = parseInt(parts[0], 10);
  const end = parseInt(parts[1], 10);
  if (!Number.isFinite(start) || !Number.isFinite(end) || end <= start) {
    return [label];
  }
  const seasons = [];
  for (let year = start; year < end; year += 1) {
    const next = String(year + 1).padStart(4, '0');
    seasons.push(`${year}-${next}`);
  }
  return seasons.length ? seasons : [label];
}

function sortSizes(arr) {
  function rankSize(s) {
    const z = normalizeSize(s).normalized;
    if (z === 'XS') return 0;
    if (z === 'S') return 1;
    if (z === 'M') return 2;
    if (z === 'L') return 3;
    const m = z.match(/^X+L$/);
    if (m) return 3 + (z.length - 1); // 'XL' -> 4, 'XXL' -> 5, etc.
    return Number.POSITIVE_INFINITY; // unknown formats sort after known
  }
  return Array.from(arr).sort((a,b) => {
    const ra = rankSize(a);
    const rb = rankSize(b);
    if (Number.isFinite(ra) && Number.isFinite(rb)) return ra - rb;
    if (Number.isFinite(ra)) return -1;
    if (Number.isFinite(rb)) return 1;
    return byAlpha(a,b);
  });
}

function labelForType(value) {
  const labels = { home: 'Home', away: 'Away', third: 'Third', fourth: 'Fourth', gk: 'GK' };
  return labels[value] || (value ? value.charAt(0).toUpperCase() + value.slice(1) : 'Unknown');
}

function labelForCollectible(value) {
  const labels = { matchworn: 'Matchworn', signed: 'Signed', framed: 'Framed', regular: 'Regular' };
  return labels[normalizeCollectibleValue(value)];
}

function incrementMap(map, key, amount = 1) {
  if (!key) return;
  map.set(key, (map.get(key) || 0) + amount);
}

function getTopEntries(map, limit = 8) {
  return Array.from(map.entries())
    .sort((a, b) => (b[1] - a[1]) || byAlpha(a[0], b[0]))
    .slice(0, limit);
}

function setupFiltering() {
  const seasonSel = document.getElementById('filter-season');
  const typeSel = document.getElementById('filter-type');
  const sizeSel = document.getElementById('filter-size');
  const playerSel = document.getElementById('filter-player');
  const collectibleSel = document.getElementById('filter-collectible');
  const clearBtn = document.getElementById('filter-clear');
  const resultsEl = document.getElementById('filter-results');
  const emptyEl = document.getElementById('filter-empty');
  const statsEl = document.getElementById('collection-stats');
  const typeChartEl = document.getElementById('chart-type');
  const collectibleChartEl = document.getElementById('chart-collectible');
  const seasonChartEl = document.getElementById('chart-season');
  const listViewBtn = document.getElementById('view-list');
  const galleryViewBtn = document.getElementById('view-gallery');
  const sections = Array.from(document.querySelectorAll('.shirt-section'));

  // Initialize data attributes
  sections.forEach(inferAttributes);

  // Build unique option sets from DOM
  const seasons = new Set();
  const typesBase = new Set();
  const sizesMap = new Map(); // key: normalized, val: label for UI
  const playersMap = new Map(); // key: lower, val: label

  sections.forEach(sec => {
    if (sec.dataset.seasons) {
      sec.dataset.seasons.split('|').forEach(season => seasons.add(season));
    } else if (sec.dataset.season) {
      seasons.add(sec.dataset.season);
    }
    if (sec.dataset.typeBase) typesBase.add(sec.dataset.typeBase);
    if (sec.dataset.size) sizesMap.set(sec.dataset.size, sec.dataset.sizeLabel || sec.dataset.size);
    if (sec.dataset.player) playersMap.set(sec.dataset.player, sec.dataset.playerLabel || sec.dataset.player);
    sec.dataset.collectible = normalizeCollectibleValue(sec.dataset.collectible);
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
    const TYPE_ORDER = ['home','away','third','fourth','gk'];
    TYPE_ORDER.forEach(t => {
      if (!typesBase.has(t)) return;
      const opt = document.createElement('option');
      opt.value = t; // normalized base value
      opt.textContent = labelForType(t);
      typeSel.appendChild(opt);
    });
  }

  if (sizeSel) {
    sortSizes(sizesMap.keys()).forEach(z => {
      const opt = document.createElement('option');
      opt.value = z; // normalized for matching
      opt.textContent = sizesMap.get(z) || z; // display original label when available (e.g., 2XL)
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

  if (collectibleSel) {
    [
      { value: 'matchworn', label: 'Matchworn' },
      { value: 'signed', label: 'Signed' },
      { value: 'framed', label: 'Framed' },
      { value: 'regular', label: 'Regular' },
    ].forEach(({ value, label }) => {
      const opt = document.createElement('option');
      opt.value = value;
      opt.textContent = label;
      collectibleSel.appendChild(opt);
    });
  }

  function getMultiSelectedValues(selectEl) {
    return Array.from(selectEl?.selectedOptions || []).map(o => o.value).filter(Boolean);
  }

  function updateCounts() {
    const map = new Map([
      [seasonSel, document.querySelector('label[for="filter-season"]')],
      [typeSel, document.querySelector('label[for="filter-type"]')],
      [sizeSel, document.querySelector('label[for="filter-size"]')],
      [playerSel, document.querySelector('label[for="filter-player"]')],
      [collectibleSel, document.querySelector('label[for="filter-collectible"]')],
    ]);
    map.forEach((labelEl, sel) => {
      if (!labelEl || !sel) return;
      const base = labelEl.textContent.split(' (')[0];
      const count = getMultiSelectedValues(sel).length;
      labelEl.textContent = count ? `${base} (${count} selected)` : base;
    });
  }

  function enableMultiSelectWithoutCtrl(selectEl) {
    if (!selectEl) return;

    // On touch devices the native picker already handles multi-select
    // interactions. Intercepting the touch events prevents the menu
    // from opening, so skip the custom logic on such devices.
    const isTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    if (isTouch) return;

    const toggle = (e) => {
      e.preventDefault();
      const option = e.target;
      option.selected = !option.selected;
      selectEl.dispatchEvent(new Event('change'));
    };

    selectEl.addEventListener('mousedown', toggle);
  }

  function setViewMode(mode) {
    const isGallery = mode === 'gallery';
    document.body.classList.toggle('gallery-view', isGallery);
    listViewBtn?.classList.toggle('active', !isGallery);
    galleryViewBtn?.classList.toggle('active', isGallery);
    listViewBtn?.setAttribute('aria-pressed', String(!isGallery));
    galleryViewBtn?.setAttribute('aria-pressed', String(isGallery));
  }

  function renderStat(label, value, helper) {
    return `
      <article class="stat-card">
        <span>${label}</span>
        <strong>${value}</strong>
        <small>${helper}</small>
      </article>
    `;
  }

  function renderStats(visibleSections) {
    if (!statsEl) return;
    const matchwornCount = visibleSections.filter(sec => sec.dataset.collectible === 'matchworn').length;
    const signedCount = visibleSections.filter(sec => sec.dataset.collectible === 'signed').length;
    const playerCount = new Set(visibleSections.map(sec => sec.dataset.player).filter(Boolean)).size;
    const seasonCount = new Set(visibleSections.flatMap(sec => (sec.dataset.seasons || sec.dataset.season || '').split('|').filter(Boolean))).size;

    statsEl.innerHTML = [
      renderStat('Visible shirts', visibleSections.length, `${sections.length} total in the archive`),
      renderStat('Matchworn', matchwornCount, 'Filtered by current view'),
      renderStat('Signed', signedCount, 'Autographs and squad-signed shirts'),
      renderStat('Players', playerCount, 'Unique named players shown'),
      renderStat('Seasons', seasonCount, 'Unique seasons represented'),
    ].join('');
  }

  function renderChart(target, entries, formatter = value => value) {
    if (!target) return;
    const max = Math.max(...entries.map(([, count]) => count), 1);
    if (!entries.length) {
      target.innerHTML = '<p class="chart-empty">No data for this selection.</p>';
      return;
    }

    target.innerHTML = entries.map(([key, count]) => {
      const width = Math.max((count / max) * 100, 8);
      return `
        <div class="chart-row">
          <div class="chart-label">
            <span>${formatter(key)}</span>
            <strong>${count}</strong>
          </div>
          <div class="chart-track" aria-hidden="true">
            <span style="width: ${width}%"></span>
          </div>
        </div>
      `;
    }).join('');
  }

  function renderCharts(visibleSections) {
    const typeMap = new Map();
    const collectibleMap = new Map();
    const seasonMap = new Map();

    visibleSections.forEach(sec => {
      incrementMap(typeMap, sec.dataset.typeBase || 'unknown');
      incrementMap(collectibleMap, normalizeCollectibleValue(sec.dataset.collectible));
      const seasonValues = (sec.dataset.seasons || sec.dataset.season || '').split('|').filter(Boolean);
      seasonValues.forEach(season => incrementMap(seasonMap, season));
    });

    const typeOrder = ['home', 'away', 'third', 'fourth', 'gk', 'unknown'];
    const typeEntries = Array.from(typeMap.entries()).sort((a, b) => typeOrder.indexOf(a[0]) - typeOrder.indexOf(b[0]));
    const collectibleEntries = getTopEntries(collectibleMap, 6);
    const seasonEntries = getTopEntries(seasonMap, 8);

    renderChart(typeChartEl, typeEntries, labelForType);
    renderChart(collectibleChartEl, collectibleEntries, labelForCollectible);
    renderChart(seasonChartEl, seasonEntries);
  }

  function applyFilter() {
    const seasonsSelected = seasonSel ? getMultiSelectedValues(seasonSel) : [];
    const typesSelected = typeSel ? getMultiSelectedValues(typeSel).map(v => v.toLowerCase()) : [];
    const sizesSelected = sizeSel ? getMultiSelectedValues(sizeSel).map(v => v.toUpperCase()) : [];
    const playersSelected = playerSel ? getMultiSelectedValues(playerSel) : [];
    const collectibleSelected = collectibleSel ? getMultiSelectedValues(collectibleSel).map(v => v.toLowerCase()) : [];
    const visibleSections = [];

    sections.forEach(sec => {
      const seasonValues = sec.dataset.seasons
        ? sec.dataset.seasons.split('|').filter(Boolean)
        : (sec.dataset.season ? [sec.dataset.season] : []);
      const okSeason = seasonsSelected.length === 0 || seasonValues.some(v => seasonsSelected.includes(v));
      const okType = typesSelected.length === 0 || typesSelected.includes(sec.dataset.typeBase || '');
      const okSize = sizesSelected.length === 0 || sizesSelected.includes(sec.dataset.size || '');
      const okPlayer = playersSelected.length === 0 || playersSelected.includes(sec.dataset.player || '');
      const collectibleValue = (sec.dataset.collectible || '').toLowerCase();
      const okCollectible = collectibleSelected.length === 0 || collectibleSelected.includes(collectibleValue);
      const isVisible = okSeason && okType && okSize && okPlayer && okCollectible;
      sec.style.display = isVisible ? '' : 'none';
      if (isVisible) visibleSections.push(sec);
    });

    if (resultsEl) {
      resultsEl.textContent = `Showing ${visibleSections.length} of ${sections.length} shirts.`;
    }
    if (emptyEl) emptyEl.hidden = visibleSections.length !== 0;
    renderStats(visibleSections);
    renderCharts(visibleSections);
  }

  [seasonSel, typeSel, sizeSel, collectibleSel, playerSel].forEach(sel => {
    enableMultiSelectWithoutCtrl(sel);
    sel?.addEventListener('change', () => { applyFilter(); updateCounts(); });
  });

  listViewBtn?.addEventListener('click', () => setViewMode('list'));
  galleryViewBtn?.addEventListener('click', () => setViewMode('gallery'));

  clearBtn?.addEventListener('click', () => {
    [seasonSel, typeSel, sizeSel, collectibleSel, playerSel].forEach(sel => {
      if (sel) Array.from(sel.options).forEach(o => (o.selected = false));
    });
    applyFilter();
    updateCounts();
  });

  // Initial apply to respect any default selections
  setViewMode('list');
  applyFilter();
  updateCounts();
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
