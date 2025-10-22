// Utility: infer attributes from a shirt section
function inferAttributes(section) {
  const title = section.querySelector('h3')?.textContent || '';
  const playerText = section.querySelector('.player-info')?.textContent || '';
  const seasonMatch = title.match(/(\d{4}-\d{4})/);
  const typeMatch = title.match(/Home|Away|Third|Fourth|GK ?\d?|Goalkeeper/i);
  // Capture full size tokens like XS, S, M, L, XL, XXL, XXXL, XXXXL, ...
  const sizeMatch = title.match(/Size:\s*([A-Z]{1,5})/i);
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
  if (sizeMatch) section.dataset.size = sizeMatch[1].toUpperCase();
  if (playerMatch) {
    const label = playerMatch[1].trim();
    section.dataset.player = label.toLowerCase();
    section.dataset.playerLabel = label; // preserve original casing for UI
  }
  if (collectible) {
    section.dataset.collectible = collectible;
  }
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
    const z = (s || '').toUpperCase();
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

function setupFiltering() {
  const seasonGroup = document.getElementById('filter-season');
  const typeGroup = document.getElementById('filter-type');
  const sizeGroup = document.getElementById('filter-size');
  const playerGroup = document.getElementById('filter-player');
  const collectibleGroup = document.getElementById('filter-collectible');
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
    if (sec.dataset.seasons) {
      sec.dataset.seasons.split('|').forEach(season => seasons.add(season));
    } else if (sec.dataset.season) {
      seasons.add(sec.dataset.season);
    }
    if (sec.dataset.typeBase) typesBase.add(sec.dataset.typeBase);
    if (sec.dataset.size) sizes.add(sec.dataset.size);
    if (sec.dataset.player) playersMap.set(sec.dataset.player, sec.dataset.playerLabel || sec.dataset.player);
    if (sec.dataset.collectible) {
      sec.dataset.collectible = sec.dataset.collectible.toLowerCase();
    }
  });

  function buildChipGroup(container, items, onChange) {
    if (!container) return null;
    container.innerHTML = '';
    const selected = new Set();

    items.forEach(({ value, label }) => {
      const chip = document.createElement('button');
      chip.type = 'button';
      chip.className = 'filter-chip';
      chip.textContent = label;
      chip.dataset.value = value;
      chip.setAttribute('aria-pressed', 'false');
      chip.addEventListener('click', () => {
        const isActive = chip.classList.toggle('is-active');
        chip.setAttribute('aria-pressed', isActive ? 'true' : 'false');
        if (isActive) {
          selected.add(value);
        } else {
          selected.delete(value);
        }
        onChange?.();
      });
      container.appendChild(chip);
    });

    return {
      getSelected: () => Array.from(selected),
      clear: (silent = false) => {
        if (!selected.size) return false;
        selected.clear();
        container.querySelectorAll('.filter-chip.is-active').forEach(chip => {
          chip.classList.remove('is-active');
          chip.setAttribute('aria-pressed', 'false');
        });
        if (!silent) onChange?.();
        return true;
      },
    };
  }

  const labelMap = {
    season: document.getElementById('filter-season-label'),
    type: document.getElementById('filter-type-label'),
    size: document.getElementById('filter-size-label'),
    collectible: document.getElementById('filter-collectible-label'),
    player: document.getElementById('filter-player-label'),
  };

  Object.values(labelMap).forEach(labelEl => {
    if (labelEl && !labelEl.dataset.baseLabel) {
      labelEl.dataset.baseLabel = labelEl.textContent.trim();
    }
  });

  const filters = {};

  function applyFilter() {
    const seasonsSelected = filters.season ? filters.season.getSelected() : [];
    const typesSelected = filters.type ? filters.type.getSelected().map(v => v.toLowerCase()) : [];
    const sizesSelected = filters.size ? filters.size.getSelected().map(v => v.toUpperCase()) : [];
    const playersSelected = filters.player ? filters.player.getSelected() : [];
    const collectibleSelected = filters.collectible ? filters.collectible.getSelected().map(v => v.toLowerCase()) : [];

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
      sec.style.display = (okSeason && okType && okSize && okPlayer && okCollectible) ? '' : 'none';
    });
  }

  function updateCounts() {
    Object.entries(labelMap).forEach(([key, labelEl]) => {
      if (!labelEl) return;
      const base = labelEl.dataset.baseLabel || labelEl.textContent.split(' (')[0];
      const count = filters[key]?.getSelected().length || 0;
      labelEl.textContent = count ? `${base} (${count} selected)` : base;
    });
  }

  const handleChange = () => {
    applyFilter();
    updateCounts();
  };

  filters.season = buildChipGroup(
    seasonGroup,
    Array.from(seasons).sort((a, b) => byAlpha(b, a)).map(value => ({ value, label: value })),
    handleChange,
  );

  const TYPE_ORDER = ['home', 'away', 'third', 'fourth', 'gk'];
  const TYPE_LABELS = { home: 'Home', away: 'Away', third: 'Third', fourth: 'Fourth', gk: 'GK' };
  filters.type = buildChipGroup(
    typeGroup,
    TYPE_ORDER.filter(t => typesBase.has(t)).map(value => ({ value, label: TYPE_LABELS[value] || value })),
    handleChange,
  );

  filters.size = buildChipGroup(
    sizeGroup,
    sortSizes(sizes).map(value => ({ value, label: value })),
    handleChange,
  );

  filters.collectible = buildChipGroup(
    collectibleGroup,
    [
      { value: 'matchworn', label: 'Matchworn' },
      { value: 'signed', label: 'Signed' },
      { value: 'framed', label: 'Framed' },
    ],
    handleChange,
  );

  filters.player = buildChipGroup(
    playerGroup,
    Array.from(playersMap.entries())
      .sort((a, b) => byAlpha(a[1], b[1]))
      .map(([value, label]) => ({ value, label })),
    handleChange,
  );

  clearBtn?.addEventListener('click', () => {
    let changed = false;
    Object.values(filters).forEach(filterControl => {
      if (filterControl) {
        changed = filterControl.clear(true) || changed;
      }
    });
    if (changed) {
      applyFilter();
    }
    updateCounts();
  });

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
