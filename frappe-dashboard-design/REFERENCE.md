# Frappe Dashboard Design System — Complete Reference

This file contains all CSS tokens, hex values, code snippets, and component specs referenced from SKILL.md.

---

## §1 — Spacing Scale

Base unit: **4px**. All spacing MUST be a multiple of 4px.

| Token | Value | Use |
|-------|-------|-----|
| `--space-1` | 4px | Icon internal gap |
| `--space-2` | 8px | Inline label gap |
| `--space-3` | 12px | Chip padding |
| `--space-4` | 16px | Card padding (small) |
| `--space-5` | 20px | Filter strip padding |
| `--space-6` | 24px | Card padding (standard) |
| `--space-8` | 32px | Section gap |
| `--space-10` | 40px | Page section gap |
| `--space-12` | 48px | Large section gap |

**Standard card padding**: `24px` (`--space-6`)
**Card grid gap**: `16px` or `24px` — pick one and use it consistently across the whole page.

---

## §2 — Color System

### §2.1 — Neutral Gray Scale

```css
:root {
  --gray-50:  #F9FAFB;  /* Page background */
  --gray-100: #F3F4F6;  /* Grid lines, dividers */
  --gray-200: #E5E7EB;  /* Input borders, card borders (optional) */
  --gray-300: #D1D5DB;  /* Disabled text, empty state icons */
  --gray-400: #9CA3AF;  /* Placeholder text */
  --gray-500: #6B7280;  /* Secondary text, axis labels, table headers */
  --gray-600: #4B5563;  /* Body text */
  --gray-700: #374151;  /* Subheadings */
  --gray-800: #1F2937;  /* Headings */
  --gray-900: #111827;  /* KPI numbers, primary text */
}
```

### §2.2 — ColorBrewer Palettes for Data Visualization

**RULE**: Never pick chart colors by intuition. Always use one of these.

#### Qualitative (categories without order) — Set2
```
8-color: #66C2A5, #FC8D62, #8DA0CB, #E78AC3, #A6D854, #FFD92F, #E5C494, #B3B3B3
6-color: #66C2A5, #FC8D62, #8DA0CB, #E78AC3, #A6D854, #FFD92F
4-color: #66C2A5, #FC8D62, #8DA0CB, #E78AC3
2-color: #66C2A5, #FC8D62
```

#### Qualitative (bolder, higher contrast) — Set1
```
5-color: #E41A1C, #377EB8, #4DAF4A, #984EA3, #FF7F00
```

#### Sequential (low→high, heatmaps warm) — YlOrRd
```
9-step: #FFFFCC, #FFEDA0, #FED976, #FEB24C, #FD8D3C, #FC4E2A, #E31A1C, #BD0026, #800026
5-step: #FFFFB2, #FECC5C, #FD8D3C, #F03B20, #BD0026
```

#### Sequential (cool, funding/financial) — Blues
```
9-step: #F7FBFF, #DEEBF7, #C6DBEF, #9ECAE1, #6BAED6, #4292C6, #2171B5, #08519C, #08306B
5-step: #EFF3FF, #BDD7E7, #6BAED6, #2171B5, #08519C
```

#### Sequential (green, positive metrics) — Greens
```
5-step: #EDF8E9, #BAE4B3, #74C476, #31A354, #006D2C
```

#### Diverging (good/bad, above/below target) — RdYlGn
```
9-step: #D73027, #F46D43, #FDAE61, #FEE08B, #FFFFBF, #D9EF8B, #A6D96A, #66BD63, #1A9850
5-step: #D7191C, #FDAE61, #FFFFBF, #A6D96A, #1A9641
```

**Annotate palette in code comment:**
```js
// ColorBrewer Set2 — 4-color qualitative
const CHART_COLORS = ['#66C2A5', '#FC8D62', '#8DA0CB', '#E78AC3'];
```

### §2.3 — Semantic Color Tokens

```css
:root {
  /* Success */
  --green-50:  #F0FDF4;
  --green-100: #DCFCE7;
  --green-500: #22C55E;
  --green-600: #16A34A;
  --green-700: #15803D;

  /* Warning */
  --amber-50:  #FFFBEB;
  --amber-100: #FEF3C7;
  --amber-500: #F59E0B;
  --amber-600: #D97706;
  --amber-700: #B45309;

  /* Danger */
  --red-50:  #FFF1F2;
  --red-100: #FFE4E6;
  --red-500: #EF4444;
  --red-600: #DC2626;
  --red-700: #B91C1C;

  /* Info / Primary */
  --blue-50:  #EFF6FF;
  --blue-100: #DBEAFE;
  --blue-500: #3B82F6;
  --blue-600: #2563EB;
  --blue-700: #1D4ED8;

  /* Purple / On Hold */
  --purple-50:  #FAF5FF;
  --purple-100: #F3E8FF;
  --purple-500: #A855F7;
  --purple-600: #9333EA;

  /* Convenience aliases */
  --color-success: var(--green-600);
  --color-warning: var(--amber-600);
  --color-danger:  var(--red-600);
  --color-info:    var(--blue-600);
}
```

---

## §3 — Typography Scale

```css
:root {
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
}

/* Scale table */
/* 36px — Display / Page Title          weight 700  color --gray-900 */
/* 28px — KPI Numbers                   weight 700  color --gray-900 */
/* 20px — Section Headings / Tab Labels weight 600  color --gray-800 */
/* 16px — Card Titles                   weight 600  color --gray-800 */
/* 14px — Body / Table rows             weight 400  color --gray-600 */
/* 13px — Secondary info                weight 400  color --gray-500 */
/* 12px — Captions / Axis labels        weight 400  color --gray-500 */
/* 11px — Overline labels (uppercase)   weight 600  color --gray-500 letter-spacing 0.08em */
```

**Usage snippet:**
```css
.kpi-number    { font-size: 28px; font-weight: 700; color: var(--gray-900); font-family: var(--font-sans); }
.section-title { font-size: 20px; font-weight: 600; color: var(--gray-800); }
.card-title    { font-size: 16px; font-weight: 600; color: var(--gray-800); }
.body-text     { font-size: 14px; font-weight: 400; color: var(--gray-600); }
.secondary     { font-size: 13px; font-weight: 400; color: var(--gray-500); }
.caption       { font-size: 12px; font-weight: 400; color: var(--gray-500); }
.overline      { font-size: 11px; font-weight: 600; color: var(--gray-500); text-transform: uppercase; letter-spacing: 0.08em; }
```

---

## §4 — Indian Number Formatting

### Always use `Intl.NumberFormat('en-IN')`

```js
// Full number (tables, tooltips)
function formatIN(n) {
  return new Intl.NumberFormat('en-IN').format(n);
  // 1234567 → "12,34,567"
}

// Currency (full)
function formatINR(n) {
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(n);
  // 1234567 → "₹12,34,567"
}

// Shortened for KPI cards
function shortIN(n) {
  if (n >= 1e7)  return (n / 1e7).toFixed(1).replace(/\.0$/, '') + ' Cr';
  if (n >= 1e5)  return (n / 1e5).toFixed(1).replace(/\.0$/, '') + ' L';
  if (n >= 1e3)  return (n / 1e3).toFixed(1).replace(/\.0$/, '') + ' K';
  return String(n);
  // 10000000 → "1 Cr"  |  150000 → "1.5 L"  |  1500 → "1.5 K"
}

// With tooltip showing full value
function kpiCard(value, label) {
  return `
    <div class="kpi-number" title="${formatIN(value)}">${shortIN(value)}</div>
    <div class="kpi-label">${label}</div>
  `;
}
```

**Rules:**
- All raw numbers in tables → `formatIN(n)`
- KPI card big numbers → `shortIN(n)` + `title="${formatIN(n)}"` tooltip
- Currency KPIs → `₹` prefix + `shortIN(n)` (e.g., `₹1.5 Cr`)
- Percentages → max 1 decimal place (`8.3%`)
- Dates → `DD Mon YYYY` format (e.g., `14 Mar 2025`)
- Never display: `100000`, `1000000`, `1234567` without formatting

---

## §5 — Shadow Tokens

```css
:root {
  --shadow-1: 0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.06);   /* Cards at rest */
  --shadow-2: 0 4px 12px rgba(0,0,0,0.08), 0 2px 4px rgba(0,0,0,0.04);  /* Hover / modals */
  --shadow-3: 0 12px 24px rgba(0,0,0,0.12), 0 4px 8px rgba(0,0,0,0.06); /* Popovers */
}

.card {
  background: #fff;
  border-radius: 12px;
  box-shadow: var(--shadow-1);
  transition: box-shadow 200ms ease, transform 150ms ease;
}
.card:hover {
  box-shadow: var(--shadow-2);
  transform: translateY(-1px);
}
```

---

## §6 — Component Specs

### §6.1 — KPI Card Full CSS

```css
.kpi-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: var(--shadow-1);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  transition: box-shadow 200ms ease, transform 150ms ease;
  min-width: 0;
}
.kpi-card:hover {
  box-shadow: var(--shadow-2);
  transform: translateY(-1px);
}
.kpi-icon-wrap {
  width: 40px; height: 40px;
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 4px;
}
/* Tinted icon backgrounds — use semantic color */
.kpi-icon-wrap.success { background: var(--green-100); color: var(--green-700); }
.kpi-icon-wrap.warning { background: var(--amber-100); color: var(--amber-700); }
.kpi-icon-wrap.danger  { background: var(--red-100);   color: var(--red-700); }
.kpi-icon-wrap.info    { background: var(--blue-100);  color: var(--blue-700); }

.kpi-number {
  font-size: 28px; font-weight: 700;
  color: var(--gray-900);
  cursor: default; /* tooltip on hover */
}
.kpi-label { font-size: 14px; color: var(--gray-500); }

.kpi-delta { font-size: 12px; display: flex; align-items: center; gap: 4px; }
.kpi-delta.up   { color: var(--green-600); }
.kpi-delta.down { color: var(--red-600); }
.kpi-delta.flat { color: var(--gray-500); }

/* Grid layout for row of KPI cards */
.kpi-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  align-items: stretch; /* CRITICAL: equal heights */
}
```

**KPI card HTML template:**
```html
<div class="kpi-card">
  <div class="kpi-icon-wrap info">
    <svg><!-- icon --></svg>
  </div>
  <div class="kpi-number" title="12,34,567">12.3 L</div>
  <div class="kpi-label">Total Disbursed</div>
  <div class="kpi-delta up">↑ 8% vs last FY</div>
</div>
```

### §6.2 — Status Chips Full Spec

```css
.chip {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 3px 10px;
  border-radius: 9999px;
  font-size: 12px; font-weight: 500;
  white-space: nowrap;
}
.chip-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }

/* Status mappings */
.chip.active      { background: #DCFCE7; color: #15803D; } /* green-100 / green-700 */
.chip.pending     { background: #FEF3C7; color: #B45309; } /* amber-100 / amber-700 */
.chip.rejected    { background: #FFE4E6; color: #B91C1C; } /* red-100 / red-700 */
.chip.inactive    { background: #F3F4F6; color: #374151; } /* gray-100 / gray-700 */
.chip.new         { background: #DBEAFE; color: #1D4ED8; } /* blue-100 / blue-700 */
.chip.on-hold     { background: #F3E8FF; color: #7C3AED; } /* purple-100 / purple-700 */
.chip.completed   { background: #DCFCE7; color: #15803D; }
.chip.closed      { background: #F3F4F6; color: #374151; }
.chip.draft       { background: #F0F9FF; color: #0369A1; } /* sky-100 / sky-700 */
```

**Usage:**
```html
<span class="chip active"><span class="chip-dot" style="background:#15803D"></span>Active</span>
<span class="chip pending"><span class="chip-dot" style="background:#B45309"></span>Pending</span>
```

### §6.3 — Filter Strip

```html
<div class="filter-strip">
  <div class="filter-group">
    <label>Date Range</label>
    <input type="date" id="date-from"> <span>to</span> <input type="date" id="date-to">
  </div>
  <div class="filter-group">
    <label>Organization</label>
    <select id="filter-org"><option value="">All</option></select>
  </div>
  <div class="filter-group">
    <label>Status</label>
    <select id="filter-status"><option value="">All</option></select>
  </div>
  <div class="filter-group">
    <input type="search" id="filter-search" placeholder="Search…">
  </div>
  <button id="btn-reset" class="btn-ghost" style="display:none">
    Reset Filters <span id="filter-count-badge" class="badge">0</span>
  </button>
</div>
```

```css
.filter-strip {
  display: flex; flex-wrap: wrap; gap: 12px; align-items: flex-end;
  padding: 16px 24px;
  background: #fff;
  border-bottom: 1px solid var(--gray-100);
}
.filter-group { display: flex; flex-direction: column; gap: 4px; }
.filter-group label { font-size: 11px; font-weight: 600; color: var(--gray-500); text-transform: uppercase; letter-spacing: 0.06em; }
.filter-group input,
.filter-group select {
  height: 36px; padding: 0 10px;
  border: 1px solid var(--gray-200); border-radius: 8px;
  font-size: 13px; color: var(--gray-700);
  background: #fff;
  outline: none;
}
.filter-group input:focus,
.filter-group select:focus { border-color: var(--blue-500); box-shadow: 0 0 0 2px var(--blue-100); }
.badge {
  display: inline-flex; align-items: center; justify-content: center;
  min-width: 18px; height: 18px; border-radius: 9999px;
  background: var(--blue-600); color: #fff;
  font-size: 11px; font-weight: 600; padding: 0 5px;
}
```

### §6.4 — Chart Type Selection Guide

| Data shape | Recommended chart | Library | Prompt? |
|------------|-------------------|---------|---------|
| Trend over time (1 series) | Line chart | Chart.js | — |
| Trend over time (2-4 series) | Multi-line | Chart.js | — |
| Category comparison — ranking focus | **Lollipop** (preferred) | Chart.js/SVG | Suggest to user |
| Category comparison — fill/area matters | Horizontal bar | Chart.js | — |
| Category comparison (>7 items) | Sorted horizontal bar with scroll | Chart.js | — |
| Part-to-whole (≤6 parts) | Donut chart | Chart.js | — |
| Part-to-whole (>6 parts) | Stacked bar | Chart.js | — |
| Flow / allocation / pipeline routing | **Sankey diagram** | eCharts | **Ask user first** |
| Geographic distribution | India choropleth map | D3 + TopoJSON | — |
| Time × frequency/intensity (daily cadence) | **GitHub calendar heatmap** | SVG/JS | Suggest to user |
| Correlation | Scatter plot | Chart.js | — |
| **Never use** | Pie chart, 3D chart, bubble (without clear purpose) | — | — |

**Chart.js boilerplate defaults:**
```js
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.font.size = 12;
Chart.defaults.color = '#6B7280'; // --gray-500
Chart.defaults.plugins.legend.position = 'bottom';
Chart.defaults.plugins.tooltip.callbacks = {
  label: (ctx) => ' ' + formatIN(ctx.raw)
};
// Grid lines
Chart.defaults.scale.grid.color = '#F3F4F6';   // --gray-100
Chart.defaults.scale.grid.borderDash = [4, 4];
```

**Bar chart animation:**
```js
animation: { duration: 400, easing: 'easeOutQuart' }
```

**Line chart animation:**
```js
animation: { duration: 500, easing: 'easeInOutCubic' }
```

### §6.5 — India Heatmap (TopoJSON + D3)

```html
<div id="india-map-container" style="width:100%; height:480px; position:relative;">
  <button id="back-to-india" style="display:none; position:absolute; top:12px; left:12px; z-index:10;">
    ← Back to India
  </button>
  <svg id="india-map"></svg>
</div>
```

```js
// CDN deps (add to <head>):
// <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
// <script src="https://cdnjs.cloudflare.com/ajax/libs/topojson/3.0.2/topojson.min.js"></script>
// TopoJSON source: https://raw.githubusercontent.com/deldersveld/topojson/master/countries/india/india-states.json

async function renderIndiaMap(container, data) {
  const svg = d3.select('#india-map');
  const { width, height } = container.getBoundingClientRect();
  svg.attr('width', width).attr('height', height);

  const projection = d3.geoMercator();
  const path = d3.geoPath().projection(projection);

  const topo = await d3.json(INDIA_TOPO_URL);
  const states = topojson.feature(topo, topo.objects.states);

  // CRITICAL: fitBounds so map fills container — never skip this
  projection.fitSize([width, height], states);

  // ColorBrewer YlOrRd sequential for choropleth
  const colorScale = d3.scaleQuantize()
    .domain([0, d3.max(Object.values(data))])
    .range(['#FFFFCC','#FFEDA0','#FED976','#FEB24C','#FD8D3C','#FC4E2A','#E31A1C','#BD0026','#800026']);

  svg.selectAll('path')
    .data(states.features)
    .join('path')
      .attr('d', path)
      .attr('fill', d => colorScale(data[d.properties.NAME_1] || 0))
      .attr('stroke', '#fff')
      .attr('stroke-width', 0.5)
      .on('click', (event, d) => drillDown(d.properties.NAME_1))
      .append('title')
        .text(d => `${d.properties.NAME_1}: ${formatIN(data[d.properties.NAME_1] || 0)}`);
}

// Drill-down: on state click, load district-level data
function drillDown(stateName) {
  document.getElementById('back-to-india').style.display = 'block';
  // Load district TopoJSON for stateName and re-render
}

document.getElementById('back-to-india').onclick = () => {
  document.getElementById('back-to-india').style.display = 'none';
  renderIndiaMap(/* top-level data */);
};
```

---

## §7 — Top Tab Bar

```html
<nav class="top-tabs">
  <button class="tab active" data-tab="overview">Overview</button>
  <button class="tab" data-tab="grants">Grants</button>
  <button class="tab" data-tab="reports">Reports</button>
  <button class="tab" data-tab="settings">Settings</button>
</nav>
```

```css
.top-tabs {
  display: flex; gap: 0;
  border-bottom: 1px solid var(--gray-200);
  background: #fff;
  padding: 0 24px;
}
.tab {
  padding: 14px 20px;
  font-size: 14px; font-weight: 500;
  color: var(--gray-500);
  background: none; border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: color 150ms, border-color 150ms;
  white-space: nowrap;
}
.tab:hover { color: var(--gray-700); }
.tab.active {
  color: var(--color-info);       /* --blue-600 */
  border-bottom-color: var(--color-info);
  font-weight: 600;
}
```

```js
document.querySelectorAll('.tab').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    btn.classList.add('active');
    document.querySelectorAll('.tab-pane').forEach(p => p.style.display = 'none');
    document.getElementById('tab-' + btn.dataset.tab).style.display = 'block';
  });
});
```

---

## §8 — Animation Timing Table

```css
:root {
  --ease-default:  cubic-bezier(0.4, 0, 0.2, 1);
  --ease-out:      cubic-bezier(0, 0, 0.2, 1);
  --ease-in:       cubic-bezier(0.4, 0, 1, 1);
  --ease-spring:   cubic-bezier(0.34, 1.56, 0.64, 1);  /* subtle bounce */

  --duration-fast:   100ms;  /* Button press ripple */
  --duration-normal: 200ms;  /* Hover states, tooltip appear */
  --duration-slow:   300ms;  /* Modal open, page sections */
}
```

| Element | Duration | Easing | Property |
|---------|----------|--------|----------|
| Button press | 100ms | ease-default | background-color |
| Card hover lift | 150ms | ease-out | transform + box-shadow |
| Tooltip appear | 200ms | ease-out | opacity + translateY(4px) |
| Filter chip appear | 200ms | ease-spring | scale(0.8→1) |
| Modal open | 300ms | ease-out | opacity + scale(0.96→1) |
| Page load card stagger | 300ms, 50ms delay each | ease-out | opacity + translateY(8px→0) |
| KPI count-up | 600ms | ease-out | JS counter |
| Chart bars grow | 400ms | ease-out | Chart.js animation |
| Chart line draw | 500ms | ease-in-out | Chart.js animation |
| Skeleton shimmer | 1.5s infinite | linear | background-position |

**Page load stagger snippet:**
```js
document.querySelectorAll('.kpi-card').forEach((card, i) => {
  card.style.opacity = '0';
  card.style.transform = 'translateY(8px)';
  setTimeout(() => {
    card.style.transition = 'opacity 300ms ease, transform 300ms ease';
    card.style.opacity = '1';
    card.style.transform = 'translateY(0)';
  }, i * 50);
});
```

**KPI count-up snippet:**
```js
function countUp(el, target, duration = 600) {
  const start = performance.now();
  function step(now) {
    const p = Math.min((now - start) / duration, 1);
    const ease = 1 - Math.pow(1 - p, 3); // ease-out cubic
    const current = Math.round(ease * target);
    el.textContent = shortIN(current);
    if (p < 1) requestAnimationFrame(step);
    else el.textContent = shortIN(target);
  }
  requestAnimationFrame(step);
}
```

---

## §9 — Special UI Patterns

### §9.1 — Skeleton Loading

```css
.skeleton {
  background: var(--gray-100);
  border-radius: 6px;
  position: relative;
  overflow: hidden;
}
.skeleton::after {
  content: '';
  position: absolute; inset: 0;
  background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.6) 50%, transparent 100%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite linear;
}
@keyframes shimmer {
  from { background-position: 200% 0; }
  to   { background-position: -200% 0; }
}
/* Usage: <div class="skeleton" style="height:28px; width:80px;"></div> */
```

### §9.2 — Empty States

```html
<div class="empty-state">
  <svg class="empty-icon" viewBox="0 0 24 24"><!-- icon --></svg>
  <h3 class="empty-title">No active grantees yet</h3>
  <p class="empty-sub">Grantees will appear here once grants are disbursed.</p>
  <button class="btn-primary">+ Add Grantee</button>
</div>
```

```css
.empty-state {
  display: flex; flex-direction: column; align-items: center;
  gap: 12px; padding: 48px 24px; text-align: center;
}
.empty-icon { width: 64px; height: 64px; color: var(--gray-300); }
.empty-title { font-size: 16px; font-weight: 600; color: var(--gray-700); margin: 0; }
.empty-sub { font-size: 14px; color: var(--gray-500); margin: 0; max-width: 320px; }
```

### §9.3 — Mock Data Banner

```html
<div id="mock-data-banner" class="mock-banner">
  ⚠ Displaying mock data — Connect API for live data
</div>
```

```css
.mock-banner {
  position: sticky; top: 0; z-index: 100;
  padding: 10px 20px;
  font-size: 13px; font-weight: 500;
  color: #92400E; /* amber-800 */
  text-align: center;
  background-image: repeating-linear-gradient(
    -45deg,
    #FEF3C7,
    #FEF3C7 10px,
    #FDE68A 10px,
    #FDE68A 20px
  );
  border-bottom: 1px solid #FCD34D;
}
/* Remove banner once API is live: */
/* document.getElementById('mock-data-banner').remove(); */
```

### §9.4 — Nudge Bars

```html
<!-- Pending approvals — amber -->
<div class="nudge nudge-warning">
  <span>5 grants awaiting your review</span>
  <a href="#" class="nudge-cta">Review now →</a>
</div>

<!-- Overdue — red -->
<div class="nudge nudge-danger">
  <span>3 reports overdue by 7+ days</span>
  <a href="#" class="nudge-cta">View overdue →</a>
</div>
```

```css
.nudge {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 20px; border-radius: 8px;
  font-size: 13px; font-weight: 500;
  margin-bottom: 12px;
}
.nudge-warning { background: var(--amber-50); color: var(--amber-700); border-left: 3px solid var(--amber-500); }
.nudge-danger  { background: var(--red-50);   color: var(--red-700);   border-left: 3px solid var(--red-500); }
.nudge-info    { background: var(--blue-50);  color: var(--blue-700);  border-left: 3px solid var(--blue-500); }
.nudge-success { background: var(--green-50); color: var(--green-700); border-left: 3px solid var(--green-500); }
.nudge-cta { font-weight: 600; text-decoration: none; color: inherit; }
.nudge-cta:hover { text-decoration: underline; }
```

---

## §10 — Button Styles

```css
.btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 8px 16px; border-radius: 8px;
  font-size: 13px; font-weight: 500;
  cursor: pointer; border: none;
  transition: background 100ms, box-shadow 100ms;
  white-space: nowrap;
}
/* Primary */
.btn-primary { background: var(--blue-600); color: #fff; }
.btn-primary:hover { background: var(--blue-700); box-shadow: var(--shadow-1); }

/* Secondary */
.btn-secondary {
  background: #fff; color: var(--blue-600);
  border: 1px solid var(--blue-200);
}
.btn-secondary:hover { background: var(--blue-50); }

/* Ghost */
.btn-ghost { background: transparent; color: var(--gray-600); }
.btn-ghost:hover { background: var(--gray-100); }

/* Danger */
.btn-danger { background: var(--red-600); color: #fff; }
.btn-danger:hover { background: var(--red-700); }

/* Small variant */
.btn-sm { padding: 5px 12px; font-size: 12px; }
```

---

## §11 — Frappe-Specific Patterns

### `frappe.call()` wrapper

```js
// Standard pattern for all API calls
async function getData(method, args = {}) {
  const res = await frappe.call({ method, args });
  if (res.exc) {
    frappe.msgprint({ title: 'Error', message: res.exc, indicator: 'red' });
    return null;
  }
  return res.message;
}

// Usage
const data = await getData('myapp.api.get_dashboard_data', { year: 2025 });
```

### Page initialization pattern

```js
frappe.pages['my-dashboard'].on_page_load = function(wrapper) {
  const page = frappe.ui.make_app_page({
    parent: wrapper,
    title: 'Dashboard Title',
    single_column: true
  });

  // Inject CSS once
  if (!document.getElementById('dashboard-styles')) {
    const style = document.createElement('style');
    style.id = 'dashboard-styles';
    style.textContent = DASHBOARD_CSS; // your CSS string
    document.head.appendChild(style);
  }

  // Build HTML
  $(page.body).html(DASHBOARD_HTML);
  initDashboard();
};
```

### Link field name resolution

```js
// Never show link field value (e.g., GRT-00042) directly
// Always resolve to display name via frappe.db.get_value or include in API response

// In Python (controller):
# Return: {"grant_id": "GRT-00042", "grant_name": "Education for All 2025"}

// In JS: use grant_name, never grant_id in the UI
```

---

*End of REFERENCE.md — Return to SKILL.md for design rules and pre-flight checklist.*

---

## §12 — New Chart Types

### §12.1 — Sankey Diagram (eCharts)

**When to use**: Fund routing, budget allocation, beneficiary pathways, grant pipeline stage transitions, CSR portfolio distribution. Any time value "flows" from one set of nodes to another.

**Always ask the user first** (Rule 9) — never auto-apply.

**CDN:**
```html
<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
```

**Full eCharts Sankey config:**
```js
// ColorBrewer Set2 — qualitative node colors
const SANKEY_COLORS = ['#66C2A5','#FC8D62','#8DA0CB','#E78AC3','#A6D854','#FFD92F'];

const sankeyOption = {
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'item',
    triggerOn: 'mousemove',
    formatter: (params) => {
      if (params.dataType === 'edge') {
        // Flow tooltip
        return `
          <div style="font-family:Inter,sans-serif;font-size:13px;padding:8px 12px;">
            <div style="font-weight:600;color:#111827;margin-bottom:4px;">
              ${params.data.source} → ${params.data.target}
            </div>
            <div style="color:#4B5563;">
              Volume: <strong>₹${shortIN(params.data.value)}</strong>
            </div>
            <div style="color:#6B7280;font-size:12px;">
              ${((params.data.value / totalFlow) * 100).toFixed(1)}% of total flow
            </div>
          </div>`;
      }
      // Node tooltip
      return `
        <div style="font-family:Inter,sans-serif;font-size:13px;padding:8px 12px;">
          <div style="font-weight:600;color:#111827;">${params.name}</div>
          <div style="color:#4B5563;">Total: ₹${shortIN(params.value)}</div>
        </div>`;
    },
    backgroundColor: '#fff',
    borderColor: '#E5E7EB',
    borderWidth: 1,
    extraCssText: 'box-shadow: 0 4px 12px rgba(0,0,0,0.08); border-radius: 8px;'
  },
  series: [{
    type: 'sankey',
    layout: 'none',
    orient: 'horizontal',      // left → right
    nodeWidth: 20,
    nodeGap: 12,
    nodeAlign: 'justify',
    draggable: false,          // disable drag for consistent layout
    emphasis: {
      focus: 'adjacency',      // highlight connected flows on hover
      lineStyle: { opacity: 0.8 }
    },
    lineStyle: {
      color: 'gradient',       // gradient between source and target colors
      opacity: 0.3,
      curveness: 0.5
    },
    itemStyle: {
      borderWidth: 0,
      borderRadius: 4
    },
    label: {
      fontFamily: 'Inter, sans-serif',
      fontSize: 13,
      color: '#1F2937',        // --gray-800
      fontWeight: 500
    },
    // Assign ColorBrewer Set2 colors to nodes in order
    color: SANKEY_COLORS,
    data: [
      // { name: 'Tata Trusts', itemStyle: { color: '#66C2A5' } }, ...
    ],
    links: [
      // { source: 'Tata Trusts', target: 'Education', value: 5000000 }, ...
    ]
  }]
};

// Init — lazy-init on tab visibility, not on page load
const sankeyChart = echarts.init(document.getElementById('sankey-container'), null, {
  renderer: 'canvas',
  useDirtyRect: true         // performance optimization
});
sankeyChart.setOption(sankeyOption);

// Responsive resize
window.addEventListener('resize', () => sankeyChart.resize());
```

**Container HTML:**
```html
<div class="card" style="padding:24px;">
  <div class="card-header">
    <h3 class="card-title">Fund Flow</h3>
    <button class="btn-ghost btn-sm" onclick="exportSankey()">Export PNG</button>
  </div>
  <div id="sankey-container" style="width:100%; height:400px;"
       aria-label="Sankey diagram showing fund flow from donors to programs"
       role="img">
  </div>
</div>
```

**Export:**
```js
function exportSankey() {
  const url = sankeyChart.getDataURL({ type: 'png', pixelRatio: 2, backgroundColor: '#fff' });
  const a = document.createElement('a'); a.href = url; a.download = 'fund-flow.png'; a.click();
}
```

---

### §12.2 — Lollipop Chart

**When to use**: Ranking comparisons where the exact bar fill area is not the insight — organization performance rankings, top NGO recipients, state-wise grant distribution sorted by value.

**Use instead of horizontal bar when**: the question is "who is highest/lowest?" not "how much total area?". Keep horizontal bar when stacked/cumulative comparison matters.

```html
<div class="card" style="padding:24px;">
  <h3 class="card-title">Top Grantees by Disbursement</h3>
  <div id="lollipop-chart" style="width:100%;"></div>
</div>
```

```js
// ColorBrewer Blues sequential — 5-step
// Data: [{ label: 'Pratham', value: 5000000 }, ...]
function renderLollipop(containerId, data, maxValue) {
  const container = document.getElementById(containerId);
  const BAR_HEIGHT = 36; // row height
  const LEFT_PAD = 180;  // label column width
  const RIGHT_PAD = 80;
  const DOT_R = 6;
  const COLOR = '#2171B5'; // Blues[6]
  const STEM_COLOR = '#E5E7EB'; // --gray-200

  container.style.position = 'relative';

  const html = data.map((d, i) => {
    const pct = (d.value / maxValue) * 100;
    return `
      <div class="lollipop-row" style="
        display:flex; align-items:center; height:${BAR_HEIGHT}px;
        opacity:0; transform:translateX(-8px);
        animation: lollipopIn 400ms cubic-bezier(0.34,1.56,0.64,1) ${i * 60}ms forwards;
      ">
        <div class="lollipop-label" style="
          width:${LEFT_PAD}px; flex-shrink:0;
          font-size:13px; color:var(--gray-700); text-align:right;
          padding-right:16px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;
        " title="${d.label}">${d.label}</div>

        <div style="flex:1; position:relative; height:100%; display:flex; align-items:center;">
          <!-- Stem track (full width, gray) -->
          <div style="position:absolute; left:0; right:0; height:2px; background:var(--gray-100);"></div>
          <!-- Stem (colored, up to value) -->
          <div style="
            position:absolute; left:0; height:2px;
            width:calc(${pct}% - ${DOT_R}px);
            background:${STEM_COLOR};
            transition: width 400ms cubic-bezier(0,0,0.2,1) ${i * 60}ms;
          "></div>
          <!-- Dot -->
          <div
            class="lollipop-dot"
            style="
              position:absolute; left:${pct}%;
              width:${DOT_R * 2}px; height:${DOT_R * 2}px;
              border-radius:50%; background:${COLOR};
              border:2px solid #fff; box-shadow: var(--shadow-1);
              transform:translateX(-50%);
              cursor:default;
              transition: transform 150ms, box-shadow 150ms;
            "
            title="${d.label}: ₹${formatIN(d.value)}"
          ></div>
        </div>

        <!-- Value label -->
        <div style="
          width:${RIGHT_PAD}px; flex-shrink:0;
          font-size:13px; font-weight:600; color:var(--gray-800);
          padding-left:16px;
        ">₹${shortIN(d.value)}</div>
      </div>`;
  }).join('');

  container.innerHTML = `
    <style>
      @keyframes lollipopIn {
        to { opacity:1; transform:translateX(0); }
      }
      .lollipop-dot:hover {
        transform: translateX(-50%) scale(1.4);
        box-shadow: var(--shadow-2);
      }
    </style>
    ${html}`;
}
```

---

### §12.3 — GitHub Calendar Heatmap

**When to use**: Submission frequency over time, report activity calendars, disbursement patterns, login activity — any data where the question is "how often, on which days, over months?"

**Color**: ColorBrewer Blues 5-step. Empty cell: `--gray-100`.

```html
<div class="card" style="padding:24px;">
  <h3 class="card-title">Submission Activity</h3>
  <p class="secondary" style="margin-bottom:16px;">Last 12 months</p>
  <div id="gh-heatmap" role="img" aria-label="Calendar heatmap of submission activity"></div>
  <div class="gh-legend" style="display:flex;align-items:center;gap:6px;margin-top:12px;justify-content:flex-end;">
    <span class="caption">Less</span>
    <div style="width:12px;height:12px;border-radius:3px;background:#F3F4F6;"></div>
    <div style="width:12px;height:12px;border-radius:3px;background:#BDD7E7;"></div>
    <div style="width:12px;height:12px;border-radius:3px;background:#6BAED6;"></div>
    <div style="width:12px;height:12px;border-radius:3px;background:#2171B5;"></div>
    <div style="width:12px;height:12px;border-radius:3px;background:#08306B;"></div>
    <span class="caption">More</span>
  </div>
</div>
```

```js
// ColorBrewer Blues 5-step (empty → dense)
const GH_COLORS = ['#F3F4F6', '#BDD7E7', '#6BAED6', '#2171B5', '#08306B'];
const CELL = 13; // cell size px
const GAP = 3;   // gap px

function renderGHHeatmap(containerId, activityMap) {
  // activityMap: { 'YYYY-MM-DD': count, ... }
  const container = document.getElementById(containerId);
  const today = new Date();
  const start = new Date(today); start.setFullYear(today.getFullYear() - 1);
  // Align start to Monday
  const startDay = start.getDay(); // 0=Sun
  const alignedStart = new Date(start);
  alignedStart.setDate(start.getDate() - ((startDay + 6) % 7));

  const weeks = [];
  let week = [];
  const cursor = new Date(alignedStart);
  const maxCount = Math.max(...Object.values(activityMap), 1);

  while (cursor <= today) {
    const key = cursor.toISOString().slice(0, 10);
    const count = activityMap[key] || 0;
    const colorIdx = count === 0 ? 0 : Math.ceil((count / maxCount) * 4);
    week.push({ date: key, count, color: GH_COLORS[colorIdx] });
    if (week.length === 7) { weeks.push(week); week = []; }
    cursor.setDate(cursor.getDate() + 1);
  }
  if (week.length) weeks.push(week);

  // Month labels
  const monthLabels = weeks.map((w, i) => {
    const firstDayDate = new Date(w[0].date);
    if (firstDayDate.getDate() <= 7) {
      return { col: i, label: firstDayDate.toLocaleString('en-IN', { month: 'short' }) };
    }
    return null;
  }).filter(Boolean);

  const svgW = weeks.length * (CELL + GAP) + 24; // 24px for day labels
  const svgH = 7 * (CELL + GAP) + 28; // 28px for month labels

  const cells = weeks.flatMap((w, wi) =>
    w.map((d, di) => `
      <rect
        x="${24 + wi * (CELL + GAP)}" y="${28 + di * (CELL + GAP)}"
        width="${CELL}" height="${CELL}"
        rx="3" ry="3"
        fill="${d.color}"
        style="cursor:default; transition:opacity 150ms;"
        onmouseover="this.style.opacity=0.7;document.getElementById('gh-tip').innerHTML='${d.date}: ${formatIN(d.count)} submissions';document.getElementById('gh-tip').style.display='block';"
        onmouseout="this.style.opacity=1;document.getElementById('gh-tip').style.display='none';"
      />`)
  ).join('');

  const dayLabels = ['M','','W','','F','',''].map((l, i) =>
    l ? `<text x="18" y="${28 + i * (CELL + GAP) + CELL - 2}" text-anchor="end" font-size="10" fill="#9CA3AF">${l}</text>` : ''
  ).join('');

  const mLabels = monthLabels.map(m =>
    `<text x="${24 + m.col * (CELL + GAP)}" y="18" font-size="11" fill="#6B7280" font-family="Inter,sans-serif">${m.label}</text>`
  ).join('');

  container.innerHTML = `
    <div style="position:relative; overflow-x:auto;">
      <svg width="${svgW}" height="${svgH}" font-family="Inter,sans-serif">
        ${mLabels}${dayLabels}${cells}
      </svg>
      <div id="gh-tip" style="
        display:none; position:fixed; background:#111827; color:#fff;
        font-size:12px; padding:6px 10px; border-radius:6px;
        pointer-events:none; z-index:999; white-space:nowrap;
      "></div>
    </div>`;
}
```

---

## §13 — Accessibility (WCAG 2.1 AA)

```css
/* Universal focus ring — apply to all interactive elements */
:focus-visible {
  outline: 2px solid var(--blue-500);
  outline-offset: 2px;
  border-radius: 4px;
}

/* Remove default outline only when :focus-visible is supported */
:focus:not(:focus-visible) {
  outline: none;
}
```

**ARIA patterns for dashboard components:**
```html
<!-- KPI card with live region for count-up -->
<div class="kpi-card" role="region" aria-label="Active Grantees metric">
  <div class="kpi-number" aria-live="polite" aria-atomic="true">12.3 L</div>
  <div class="kpi-label">Active Grantees</div>
</div>

<!-- Status chip -->
<span class="chip active" role="status" aria-label="Status: Active">Active</span>

<!-- Icon-only button -->
<button class="btn-ghost btn-sm" aria-label="Export data as CSV">
  <svg aria-hidden="true"><!-- icon --></svg>
</button>

<!-- Chart wrapper -->
<div role="img" aria-label="Bar chart showing quarterly disbursements. Q1: ₹1.2Cr, Q2: ₹1.5Cr, Q3: ₹1.8Cr">
  <canvas id="quarterly-chart"></canvas>
</div>

<!-- Skeleton loader -->
<div class="kpi-card skeleton-wrapper" aria-busy="true" aria-label="Loading metric data">
  <div class="skeleton" style="height:28px;width:80px;"></div>
</div>
<!-- After load: -->
<div class="kpi-card" aria-busy="false">...</div>
```

**Contrast quick-check for this system's palette:**
| Pair | Ratio | Pass |
|------|-------|------|
| `--gray-900` on white | 16.1:1 | ✅ AAA |
| `--gray-700` on white | 10.7:1 | ✅ AAA |
| `--gray-500` on white | 4.6:1 | ✅ AA |
| `--blue-600` on white | 4.9:1 | ✅ AA |
| `--green-600` on white | 4.5:1 | ✅ AA (border) |
| white on `--blue-600` | 4.9:1 | ✅ AA |

---

## §14 — Error States

Three mandatory error states. Every section that makes a `frappe.call()` must handle all three.

```css
.error-nudge {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 16px; border-radius: 8px;
  background: var(--red-50); color: var(--red-700);
  border-left: 3px solid var(--red-500);
  font-size: 13px; font-weight: 500;
  margin-bottom: 12px;
}
.locked-card {
  display: flex; flex-direction: column; align-items: center;
  gap: 12px; padding: 40px 24px; text-align: center;
  background: var(--gray-50); border-radius: 12px;
  border: 1px dashed var(--gray-200);
}
.timeout-state {
  display: flex; align-items: center; gap: 10px;
  padding: 12px 16px; border-radius: 8px;
  background: var(--amber-50); color: var(--amber-700);
  border-left: 3px solid var(--amber-500);
  font-size: 13px;
}
```

```html
<!-- API Error / 500 -->
<div class="error-nudge" role="alert">
  <span>⚠ Failed to load grant data</span>
  <button class="btn-ghost btn-sm" onclick="retryLoad()">Retry →</button>
</div>

<!-- Permission Error / 403 -->
<div class="locked-card" role="status">
  <svg style="width:40px;height:40px;color:var(--gray-300);" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
    <path d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
  </svg>
  <p style="font-size:14px;font-weight:600;color:var(--gray-700);margin:0;">Access Restricted</p>
  <p style="font-size:13px;color:var(--gray-500);margin:0;">You don't have permission to view this data. Contact your administrator.</p>
</div>

<!-- Timeout (>8s) -->
<div class="timeout-state" role="status">
  <svg style="width:16px;height:16px;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>
  </svg>
  <span>Taking longer than usual — still loading…</span>
</div>
```

**Standard API call wrapper with all three states:**
```js
async function loadSection(sectionId, method, args) {
  const el = document.getElementById(sectionId);
  el.setAttribute('aria-busy', 'true');
  showSkeleton(el);

  const timeout = setTimeout(() => showTimeoutState(el), 8000);

  try {
    const res = await frappe.call({ method, args });
    clearTimeout(timeout);

    if (res.exc?.includes('PermissionError')) {
      showLockedCard(el);
      return null;
    }
    if (res.exc) {
      showErrorNudge(el, () => loadSection(sectionId, method, args));
      return null;
    }

    el.setAttribute('aria-busy', 'false');
    return res.message;
  } catch (err) {
    clearTimeout(timeout);
    showErrorNudge(el, () => loadSection(sectionId, method, args));
    return null;
  }
}
```

---

## §15 — Drawer / Side Panel

```css
.drawer-backdrop {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.3);
  z-index: 200;
  opacity: 0; pointer-events: none;
  transition: opacity 200ms ease;
}
.drawer-backdrop.open { opacity: 1; pointer-events: all; }

.drawer {
  position: fixed; top: 0; right: 0; bottom: 0;
  width: 480px; max-width: 95vw;
  background: #fff;
  box-shadow: var(--shadow-3);
  z-index: 201;
  display: flex; flex-direction: column;
  transform: translateX(100%);
  transition: transform 300ms cubic-bezier(0, 0, 0.2, 1);
}
.drawer.open { transform: translateX(0); }

.drawer-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--gray-100);
  flex-shrink: 0;
}
.drawer-header h2 { font-size: 16px; font-weight: 600; color: var(--gray-800); margin: 0; }
.drawer-close {
  width: 32px; height: 32px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  background: none; border: none; cursor: pointer; color: var(--gray-500);
  transition: background 150ms;
}
.drawer-close:hover { background: var(--gray-100); color: var(--gray-700); }

.drawer-body { flex: 1; overflow-y: auto; padding: 24px; }

.drawer-footer {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 24px;
  border-top: 1px solid var(--gray-100);
  flex-shrink: 0;
}
```

```html
<div id="drawer-backdrop" class="drawer-backdrop" onclick="closeDrawer()"></div>
<div id="detail-drawer" class="drawer" role="dialog" aria-modal="true" aria-labelledby="drawer-title">
  <div class="drawer-header">
    <h2 id="drawer-title">Grant Details</h2>
    <button class="drawer-close" onclick="closeDrawer()" aria-label="Close panel">✕</button>
  </div>
  <div class="drawer-body" id="drawer-content"><!-- populated dynamically --></div>
  <div class="drawer-footer">
    <button class="btn-ghost" onclick="closeDrawer()">Close</button>
    <button class="btn-primary" onclick="saveDrawer()">Save Changes</button>
  </div>
</div>
```

```js
function openDrawer(title, content) {
  document.getElementById('drawer-title').textContent = title;
  document.getElementById('drawer-content').innerHTML = content;
  document.getElementById('detail-drawer').classList.add('open');
  document.getElementById('drawer-backdrop').classList.add('open');
  document.body.style.overflow = 'hidden';
  // Focus first interactive element inside drawer
  setTimeout(() => {
    const first = document.querySelector('#detail-drawer button, #detail-drawer input, #detail-drawer select');
    first?.focus();
  }, 310);
}

function closeDrawer() {
  document.getElementById('detail-drawer').classList.remove('open');
  document.getElementById('drawer-backdrop').classList.remove('open');
  document.body.style.overflow = '';
}

// Close on Escape
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeDrawer(); });
```

---

## §16 — Modal / Confirmation Dialog

```css
.modal-backdrop {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.4);
  backdrop-filter: blur(2px);
  z-index: 300;
  display: flex; align-items: center; justify-content: center;
  opacity: 0; pointer-events: none;
  transition: opacity 200ms ease;
}
.modal-backdrop.open { opacity: 1; pointer-events: all; }

.modal {
  background: #fff;
  border-radius: 16px;
  box-shadow: var(--shadow-3);
  width: 100%; max-width: 480px;
  max-height: 90vh;
  display: flex; flex-direction: column;
  transform: scale(0.96);
  transition: transform 300ms cubic-bezier(0, 0, 0.2, 1);
  overflow: hidden;
}
.modal-backdrop.open .modal { transform: scale(1); }

.modal-header {
  padding: 24px 24px 0;
  display: flex; align-items: flex-start; justify-content: space-between;
}
.modal-body { padding: 16px 24px; flex: 1; overflow-y: auto; }
.modal-footer {
  padding: 16px 24px;
  border-top: 1px solid var(--gray-100);
  display: flex; gap: 8px; justify-content: flex-end;
}
```

```html
<!-- Confirmation Modal (destructive) -->
<div id="confirm-modal" class="modal-backdrop" role="dialog" aria-modal="true" aria-labelledby="modal-title">
  <div class="modal">
    <div class="modal-header">
      <div style="display:flex;align-items:center;gap:12px;">
        <div style="width:40px;height:40px;border-radius:10px;background:var(--red-100);display:flex;align-items:center;justify-content:center;flex-shrink:0;">
          <svg style="width:20px;height:20px;color:var(--red-600);" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
          </svg>
        </div>
        <h2 id="modal-title" style="font-size:16px;font-weight:600;color:var(--gray-800);margin:0;">Reject Grant?</h2>
      </div>
    </div>
    <div class="modal-body">
      <p style="font-size:14px;color:var(--gray-600);margin:0;">
        This will permanently reject the grant and notify the grantee. This action cannot be undone.
      </p>
    </div>
    <div class="modal-footer">
      <button class="btn-ghost" onclick="closeModal('confirm-modal')">Cancel</button>
      <button class="btn-danger" onclick="confirmReject()">Reject Grant</button>
    </div>
  </div>
</div>
```

```js
function openModal(id) {
  document.getElementById(id).classList.add('open');
  document.body.style.overflow = 'hidden';
}
function closeModal(id) {
  document.getElementById(id).classList.remove('open');
  document.body.style.overflow = '';
}
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') document.querySelectorAll('.modal-backdrop.open').forEach(m => m.classList.remove('open'));
});
```

---

## §17 — Multi-Select Filter

```css
.multiselect { position: relative; display: inline-block; }
.multiselect-btn {
  height: 36px; padding: 0 12px;
  border: 1px solid var(--gray-200); border-radius: 8px;
  font-size: 13px; color: var(--gray-700); background: #fff;
  display: flex; align-items: center; gap: 6px; cursor: pointer;
  white-space: nowrap;
}
.multiselect-btn:focus-visible { outline: 2px solid var(--blue-500); outline-offset: 2px; }
.multiselect-btn.has-selection { border-color: var(--blue-400); background: var(--blue-50); color: var(--blue-700); }

.multiselect-dropdown {
  position: absolute; top: calc(100% + 4px); left: 0; z-index: 50;
  background: #fff; border: 1px solid var(--gray-200); border-radius: 8px;
  box-shadow: var(--shadow-2);
  min-width: 200px; max-height: 280px; overflow-y: auto;
  display: none;
}
.multiselect-dropdown.open { display: block; }
.multiselect-header {
  display: flex; justify-content: space-between;
  padding: 10px 12px; border-bottom: 1px solid var(--gray-100);
  font-size: 12px; font-weight: 600; color: var(--gray-500);
}
.multiselect-header button { background: none; border: none; cursor: pointer; color: var(--blue-600); font-size: 12px; }
.multiselect-item {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 12px; font-size: 13px; color: var(--gray-700); cursor: pointer;
}
.multiselect-item:hover { background: var(--gray-50); }
.multiselect-item input[type="checkbox"] { accent-color: var(--blue-600); width: 14px; height: 14px; }

/* Active chips below filter strip */
.filter-chip-strip { display: flex; flex-wrap: wrap; gap: 6px; padding: 8px 24px; }
.filter-chip {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 3px 8px; border-radius: 9999px;
  background: var(--blue-50); color: var(--blue-700);
  border: 1px solid var(--blue-200);
  font-size: 12px; font-weight: 500;
}
.filter-chip-remove {
  background: none; border: none; cursor: pointer;
  color: var(--blue-400); font-size: 14px; line-height: 1; padding: 0;
}
.filter-chip-remove:hover { color: var(--blue-700); }
```

---

## §18 — Timeline / Activity Feed

```css
.timeline { padding: 0; list-style: none; margin: 0; }
.timeline-item {
  display: flex; gap: 16px;
  padding-bottom: 20px;
  position: relative;
}
/* Connector line */
.timeline-item:not(:last-child)::before {
  content: '';
  position: absolute; left: 7px; top: 16px; bottom: 0;
  width: 2px; background: var(--gray-200);
}
.timeline-dot {
  width: 16px; height: 16px; border-radius: 50%;
  flex-shrink: 0; margin-top: 2px;
  border: 2px solid #fff; box-shadow: var(--shadow-1);
}
.timeline-dot.created  { background: var(--blue-500); }
.timeline-dot.approved { background: var(--green-500); }
.timeline-dot.rejected { background: var(--red-500); }
.timeline-dot.updated  { background: var(--amber-500); }
.timeline-dot.commented{ background: var(--gray-400); }

.timeline-body { flex: 1; min-width: 0; }
.timeline-meta {
  display: flex; align-items: baseline; gap: 8px;
  font-size: 13px; margin-bottom: 2px;
}
.timeline-actor { font-weight: 600; color: var(--gray-800); }
.timeline-action { color: var(--gray-600); }
.timeline-time { font-size: 12px; color: var(--gray-400); margin-left: auto; white-space: nowrap; }
.timeline-detail { font-size: 13px; color: var(--gray-500); }

.timeline-expand {
  background: none; border: none; cursor: pointer;
  font-size: 13px; color: var(--blue-600); padding: 4px 0;
}
.timeline-expand:hover { text-decoration: underline; }
```

```html
<ul class="timeline" aria-label="Activity history">
  <li class="timeline-item">
    <div class="timeline-dot approved"></div>
    <div class="timeline-body">
      <div class="timeline-meta">
        <span class="timeline-actor">Priya Sharma</span>
        <span class="timeline-action">approved this grant</span>
        <span class="timeline-time">2 hours ago</span>
      </div>
      <p class="timeline-detail">Grant amount: ₹25L. Disbursement scheduled for 15 Mar 2025.</p>
    </div>
  </li>
  <!-- more items -->
</ul>
<!-- Show more -->
<button class="timeline-expand" onclick="expandTimeline()">Show 8 more ↓</button>
```

---

## §19 — Performance & Filter Persistence

### Parallel API calls
```js
// CORRECT — parallel
const [grants, kpis, mapData] = await Promise.all([
  getData('myapp.api.get_grants', filters),
  getData('myapp.api.get_kpis', filters),
  getData('myapp.api.get_map_data', filters)
]);

// WRONG — serial (3× slower)
const grants = await getData('myapp.api.get_grants', filters);
const kpis = await getData('myapp.api.get_kpis', filters);
const mapData = await getData('myapp.api.get_map_data', filters);
```

### Debounced filter application
```js
function debounce(fn, delay) {
  let timer;
  return (...args) => { clearTimeout(timer); timer = setTimeout(() => fn(...args), delay); };
}
const applyFilters = debounce(async () => {
  const filters = collectFilters();
  saveFilterState(filters);
  showSkeletons();
  await loadAllSections(filters);
}, 300);

document.querySelectorAll('.filter-group input, .filter-group select').forEach(el => {
  el.addEventListener('change', applyFilters);
});
```

### Filter state persistence
```js
const PAGE_KEY = `dashboard_${frappe.get_route_str()}_filters`;

function saveFilterState(filters) {
  sessionStorage.setItem(PAGE_KEY, JSON.stringify(filters));
}
function loadFilterState() {
  try { return JSON.parse(sessionStorage.getItem(PAGE_KEY)) || {}; }
  catch { return {}; }
}
function clearFilterState() {
  sessionStorage.removeItem(PAGE_KEY);
}

// On page load: restore filters
const savedFilters = loadFilterState();
if (Object.keys(savedFilters).length) applyRestoredFilters(savedFilters);
```

### Chart instance management
```js
// CORRECT — destroy before recreate on filter change
const chartInstances = {};

function renderChart(id, config) {
  if (chartInstances[id]) {
    chartInstances[id].destroy();       // Chart.js
    // For eCharts: chartInstances[id].dispose();
  }
  chartInstances[id] = new Chart(document.getElementById(id), config);
}
```

---

## §20 — Responsive Breakpoints

```css
/* Breakpoints */
/* Desktop  ≥ 1280px — default styles */
/* Tablet   768–1279px */
/* Mobile   ≤ 767px */

/* KPI card grid */
.kpi-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr); /* desktop: 4 cols */
  gap: 16px;
  align-items: stretch;
}
@media (max-width: 1279px) {
  .kpi-row { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 767px) {
  .kpi-row { grid-template-columns: 1fr; }
}

/* Filter strip */
.filter-strip { flex-wrap: wrap; gap: 12px; }
@media (max-width: 767px) {
  .filter-strip { display: none; } /* collapsed — show via "Filters" button */
  .filter-toggle-btn { display: flex; } /* show Filters button */
}

/* Table */
.table-wrapper {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}
.data-table { min-width: 700px; } /* preserve layout on scroll */

/* India map */
#india-map-container {
  height: 480px;
}
@media (max-width: 767px) {
  #india-map-container { height: 300px; }
}

/* Drawer */
@media (max-width: 767px) {
  .drawer { width: 100%; max-width: 100%; }
}
```

---

## §21 — Print / Export

### Print stylesheet
```css
@media print {
  /* Hide non-content UI */
  .frappe-sidebar, .navbar, .filter-strip, .top-tabs,
  .btn, .nudge, .mock-banner, .drawer, .modal-backdrop { display: none !important; }

  /* Layout */
  body { background: #fff !important; }
  .card { box-shadow: none !important; border: 1px solid #E5E7EB; break-inside: avoid; }
  .kpi-row { grid-template-columns: repeat(4, 1fr) !important; }

  /* Tables — expand to full width */
  .table-wrapper { overflow: visible !important; }
  .data-table { width: 100% !important; min-width: 0 !important; }

  /* Typography */
  body { font-size: 11pt; color: #000; }
  .kpi-number { font-size: 20pt; }

  /* Page breaks */
  .chart-section { break-before: auto; }
  .print-page-break { break-before: page; }
}
```

### Export button pattern
```html
<!-- Top-right of every table card header -->
<div class="card-header" style="display:flex;align-items:center;justify-content:space-between;padding:20px 24px 0;">
  <h3 class="card-title">Grant List</h3>
  <div style="position:relative;">
    <button class="btn-ghost btn-sm export-btn" onclick="toggleExportMenu(this)" aria-haspopup="true">
      <svg style="width:14px;height:14px;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/>
      </svg>
      Export
    </button>
    <div class="export-menu" style="display:none;position:absolute;right:0;top:calc(100%+4px);background:#fff;border:1px solid var(--gray-200);border-radius:8px;box-shadow:var(--shadow-2);min-width:140px;z-index:50;">
      <button class="export-item" onclick="exportCSV()">Download CSV</button>
      <button class="export-item" onclick="exportExcel()">Download Excel</button>
      <button class="export-item" onclick="window.print()">Print</button>
    </div>
  </div>
</div>
```

```css
.export-item {
  display: block; width: 100%;
  padding: 8px 14px; text-align: left;
  font-size: 13px; color: var(--gray-700);
  background: none; border: none; cursor: pointer;
}
.export-item:hover { background: var(--gray-50); }
.export-item:first-child { border-radius: 8px 8px 0 0; }
.export-item:last-child { border-radius: 0 0 8px 8px; }
```

```js
function exportCSV(data, filename = 'export.csv') {
  const headers = Object.keys(data[0]).join(',');
  const rows = data.map(row => Object.values(row).map(v => `"${String(v).replace(/"/g,'""')}"`).join(','));
  const csv = [headers, ...rows].join('\n');
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a'); a.href = url; a.download = filename; a.click();
  URL.revokeObjectURL(url);
  frappe.show_alert({ message: 'Export complete', indicator: 'green' });
}
```

---

*End of REFERENCE.md — Return to SKILL.md for design rules and pre-flight checklist.*

