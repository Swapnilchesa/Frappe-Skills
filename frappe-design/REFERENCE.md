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

| Data shape | Recommended chart | Library |
|------------|-------------------|---------|
| Trend over time (1 series) | Line chart | Chart.js |
| Trend over time (2-4 series) | Multi-line | Chart.js |
| Category comparison (≤7 items) | Horizontal bar | Chart.js |
| Category comparison (>7 items) | Sorted horizontal bar with scroll | Chart.js |
| Part-to-whole (≤6 parts) | Donut chart | Chart.js |
| Part-to-whole (>6 parts) | Stacked bar | Chart.js |
| Geographic distribution | India choropleth map | D3 + TopoJSON |
| Correlation | Scatter plot | Chart.js |
| Funnel / pipeline | Funnel (custom) | SVG / HTML |
| Gender/demographic split | Pictorial (ISOTYPE) grid | HTML/CSS |
| Percentage composition (visual) | Waffle chart (10×10 grid) | HTML/CSS |
| Target attainment | Progress gauge (semi-circle or linear) | SVG / HTML |
| Percentage bar (inline) | 100% stacked bar | HTML/CSS |
| **Never use** | Pie chart, 3D chart, bubble (without clear purpose) | — |

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

### §6.5 — Infographic & Non-Chart Visualizations

These are pure HTML/CSS components — no Chart.js needed. Use them when the data is simple and human-scale (≤100 units).

#### Pictorial (ISOTYPE) Grid — Gender Split, Participation Rate

10 person icons where filled vs outline shows ratio. Classic for male/female splits, target vs actual in human-scale numbers.

```html
<div class="pictorial-grid" style="display:flex;gap:3px;flex-wrap:wrap;max-width:220px">
  <!-- Repeat: filled icon for count, outline for remainder -->
</div>

<style>
.person-icon { width:20px; height:32px; position:relative; }
.person-icon .head { width:8px; height:8px; border-radius:50%; position:absolute; top:0; left:6px; }
.person-icon .body { width:14px; height:18px; border-radius:7px 7px 3px 3px; position:absolute; top:10px; left:3px; }
.person-icon.filled .head, .person-icon.filled .body { background: var(--color); }
.person-icon.outline .head, .person-icon.outline .body { border: 1.5px solid var(--color); background: transparent; }
</style>
```

**Usage pattern:**
```javascript
// Gender split: 6 male, 4 female out of 10
function renderPictorial(container, filled, total, color) {
    var html = '';
    for (var i = 0; i < total; i++) {
        var cls = i < filled ? 'filled' : 'outline';
        html += '<div class="person-icon ' + cls + '" style="--color:' + color + '">' +
                '<div class="head"></div><div class="body"></div></div>';
    }
    container.innerHTML = html;
}
```

**Color conventions:**
- Male: `#2563EB` (blue-600), Female: `#EC4899` (pink-500)
- Target met: `#16A34A` (green-600), Gap: `#E5E7EB` (gray-200)
- Always label with actual numbers, not just icons

#### Waffle Chart — 10×10 Percentage Grid

100 small squares showing percentage composition. Better than donut for showing "73% complete" at a glance.

```html
<div class="waffle-grid" style="display:grid;grid-template-columns:repeat(10,1fr);gap:2px;width:160px;height:160px">
  <!-- 100 cells, colored by category -->
</div>
```

```javascript
// ColorBrewer Set2 — 3-color qualitative
function renderWaffle(container, segments) {
    // segments = [{count: 73, color: '#66C2A5', label: 'Complete'}, {count: 27, color: '#E5E7EB', label: 'Remaining'}]
    var cells = [];
    segments.forEach(function(seg) {
        for (var i = 0; i < seg.count; i++) {
            cells.push('<div style="background:' + seg.color + ';border-radius:2px" title="' + seg.label + '"></div>');
        }
    });
    container.innerHTML = cells.join('');
}
```

#### Progress Gauge — Target Attainment

Semi-circular or linear progress bar. Use for "43 of 100 candidates placed" type metrics.

```html
<!-- Linear progress -->
<div style="background:#F3F4F6;border-radius:6px;height:8px;overflow:hidden;width:100%">
  <div style="background:#16A34A;height:100%;width:43%;border-radius:6px;transition:width 600ms ease"></div>
</div>
<div style="display:flex;justify-content:space-between;font-size:11px;color:#6B7280;margin-top:4px">
  <span>43 placed</span><span>100 target</span>
</div>
```

```html
<!-- Semi-circular gauge (SVG) -->
<svg viewBox="0 0 120 70" width="160">
  <path d="M10 65 A50 50 0 0 1 110 65" fill="none" stroke="#E5E7EB" stroke-width="8" stroke-linecap="round"/>
  <path d="M10 65 A50 50 0 0 1 110 65" fill="none" stroke="#16A34A" stroke-width="8" stroke-linecap="round"
        stroke-dasharray="157" stroke-dashoffset="89.5" style="transition:stroke-dashoffset 800ms ease"/>
  <!-- dashoffset = 157 * (1 - percentage/100) -->
  <text x="60" y="58" text-anchor="middle" font-size="18" font-weight="700" fill="#1F2937">43%</text>
</svg>
```

#### 100% Stacked Bar — Inline Composition

Single horizontal bar showing composition. Simpler than Chart.js stacked bars for simple part-to-whole.

```html
<div style="display:flex;height:24px;border-radius:6px;overflow:hidden;width:100%">
  <div style="background:#66C2A5;width:45%;display:flex;align-items:center;justify-content:center;font-size:10px;color:#fff;font-weight:600">Career 45%</div>
  <div style="background:#FC8D62;width:35%;display:flex;align-items:center;justify-content:center;font-size:10px;color:#fff;font-weight:600">Employ 35%</div>
  <div style="background:#8DA0CB;width:20%;display:flex;align-items:center;justify-content:center;font-size:10px;color:#fff;font-weight:600">Entrep 20%</div>
</div>
<!-- Always use ColorBrewer palette — annotated in comment -->
<!-- ColorBrewer Set2 — 3-color qualitative: #66C2A5, #FC8D62, #8DA0CB -->
```

#### Funnel Chart — Pipeline Visualization

For lead/conversion pipelines. Pure HTML, no library needed.

```html
<div style="display:flex;flex-direction:column;align-items:center;gap:2px">
  <div style="background:#DBEAFE;height:36px;width:100%;border-radius:4px;display:flex;align-items:center;padding:0 16px;font-size:12px;font-weight:600;color:#1D4ED8">
    Leads <span style="margin-left:auto;font-size:14px">142</span>
  </div>
  <div style="background:#E0E7FF;height:36px;width:80%;border-radius:4px;display:flex;align-items:center;padding:0 16px;font-size:12px;font-weight:600;color:#4338CA">
    Contacted <span style="margin-left:auto;font-size:14px">89</span>
  </div>
  <div style="background:#FEF3C7;height:36px;width:55%;border-radius:4px;display:flex;align-items:center;padding:0 16px;font-size:12px;font-weight:600;color:#B45309">
    Scheduled <span style="margin-left:auto;font-size:14px">52</span>
  </div>
  <div style="background:#DCFCE7;height:36px;width:30%;border-radius:4px;display:flex;align-items:center;padding:0 16px;font-size:12px;font-weight:600;color:#15803D">
    Converted <span style="margin-left:auto;font-size:14px">31</span>
  </div>
</div>
```

**Rules for all infographic components:**
- Always include actual numbers alongside visual representation
- Use Indian number formatting for values ≥1,000
- ColorBrewer palettes required — annotate in code comment
- All animations via CSS `transition`, not JavaScript — keep it lightweight
- Accessible: `title` attributes on interactive elements, sufficient contrast

---

### §6.6 — India Drill-down Map (State → District → Block)

**Canonical dataset:** LGD-keyed unified TopoJSON living in this repo at
`assets/india-admin-geo/topo/{states,districts,blocks}.json`. 36 states, 780 districts, 6,803 CD blocks. Every block carries its full LGD parent chain (`state_lgd` → `district_lgd`) so drill-down is a single `.filter()`. See `assets/india-admin-geo/README.md` for schema, jsDelivr URLs, and provenance.

**Two delivery modes:**
- **Production (install-time copy, recommended):** `curl` the three files into `apps/<app>/<app>/public/geo/` and reference as `/assets/<app>/geo/states.json` etc. No runtime CDN dependency. Get the copy script from `assets/india-admin-geo/README.md`.
- **Prototype (CDN):** reference directly from `https://cdn.jsdelivr.net/gh/Swapnilchesa/Frappe-Skills@main/assets/india-admin-geo/topo/…`. Pin `@v1.0.0` (or a commit SHA) for anything past demo.

**Drop-in CHB code:** `assets/india-admin-geo/reference/custom_html_block.html`. Paste into a Custom HTML Block with placeholders filled — see Phase 1 below for what to ask the user.

---

#### Phase 1 — Clarify before generating code (always)

Ask the user, one AskUserQuestion at a time:

1. **Frappe app name** → decides `/assets/<app>/geo/` path.
2. **Workspace** to embed in.
3. **Grant/record DocType + fields:** state LGD field, district LGD field, block field, primary numeric metric, portfolio/programme field (optional), grantee field.
4. **Metric aggregation:** sum | count | count_distinct | avg.
5. **Metric format:** `inr_crore` | `inr_lakh` | `count` | `percent`.
6. **Aspirational district source:** DocType + field, or static JSON.
7. **ColorBrewer scheme** — pick from the picker below.
8. **Hover card fields per level** — pick from the field menu below.
9. **Delivery mode** — install-time copy (production) or CDN (prototype).

Restate interpreted intent back before writing the CHB.

---

#### ColorBrewer scheme picker

Always expose this as a dropdown at skill invocation — the choropleth scheme is a design decision, not a hard-coded default. All schemes below are baked into `reference/custom_html_block.html` as a `PALETTES` const; user picks by name.

**Sequential (single-hue) — use for monotonic positive metrics (sanctioned, disbursed, beneficiaries, grantees):**
`Reds` · `Blues` · `Greens` · `Purples` · `Oranges` · `Greys`

**Sequential (multi-hue) — stronger visual range, same semantics:**
`YlOrRd` · `YlOrBr` · `YlGn` · `YlGnBu` · `GnBu` · `BuGn` · `BuPu` · `PuBuGn` · `PuRd` · `RdPu` · `OrRd`

**Diverging — use for signed / above-vs-below metrics (budget variance, % vs target, YoY change):**
`RdYlGn` · `RdYlBu` · `RdBu` · `PiYG` · `PRGn` · `PuOr` · `BrBG` · `Spectral`

**Qualitative (categorical) — use only for "dominant category" maps (e.g. dominant theme per district), never for numeric choropleths:**
`Set2` · `Set3` · `Pastel1` · `Dark2` · `Accent`

**Default nudge:** positive metric → `Reds` (mGrant baseline). Signed metric → `RdYlGn`. Categorical map → `Set2`. Override if the user has a stronger preference. Never use diverging on a pure positive metric — it manufactures a fake midpoint and misleads the eye.

---

#### Hover card field picker

The right-side info card and hover tooltip show whatever the user picks at each level. Ask separately for country / state / district levels. Each field is `{key, label, format}`:

- `format` ∈ `currency` | `inr_lakh` | `count` | `number` | `percent` | `text` | `badge` | `chips`
- `chips` renders categorical portfolio pills (colours from the categorical palette in §2.2).
- `badge` renders a flag (e.g. Aspirational star) — use with a boolean field.

**Typical menus — use these as starting suggestions:**

| Level | Field keys to offer |
|---|---|
| Country (state hover) | `metric` (Sanctioned / ₹), `disbursed`, `grants_count`, `grantees` (count distinct), `themes` (chips), `aspirational_count` |
| State (district hover) | `metric`, `disbursed`, `grantees`, `portfolios` (chips), `block_count`, `aspirational` (badge), `last_disbursed_on` |
| District (block hover) | `metric`, `grantees`, `portfolios` (chips), `aspirational` (badge), `lead_partner`, `last_disbursed_on` |

Whatever the user picks flows into the `HOVER_FIELDS` placeholder of `custom_html_block.html` **and** becomes the contract for the `map_metrics` API (see `reference/api.py`) — the method must return exactly those keys per row.

Default choice if user is unsure: `[{key:"metric",label:"<Metric label>",format:"currency"},{key:"grantees",label:"Grantees",format:"count"},{key:"portfolios",label:"Themes",format:"chips"},{key:"aspirational",label:"Aspirational",format:"badge"}]` at every level.

---

#### Design tokens (level-specific)

| Level | Fill | Stroke | Hover |
|---|---|---|---|
| States | Chosen ramp by metric | `#1f2937` 1px | `#dc2626` 2px |
| Districts | Chosen ramp by metric | `#374151` 0.8px | `#dc2626` 2px |
| Blocks | Muted `#d1d5db` 0.25 opacity | `#9ca3af` 0.4px | `#ef4444` 0.45 fill |

Blocks are intentionally de-emphasised — user is inside district context, the hover card and chips carry the information.

Other chrome: header `#111827` band, info card `#ffffff` + 1px `#e5e7eb` + 10px radius + `0 1px 2px rgba(0,0,0,.03)` shadow. Typography per §3. Numbers via `Intl.NumberFormat("en-IN")` + Cr/L post-processing (see §4).

---

#### Legend

Horizontal, 5 stops, bottom-left of map. Renders the picked ColorBrewer ramp. Label min/max with formatted metric. Hidden at block level. See `renderLegendBar()` in `custom_html_block.html`.

---

#### Portfolio chips (categorical)

Baked mapping (override with a `PORTFOLIO_COLOURS` prop if the user has their own taxonomy):

```js
const PORTFOLIO = {
  "Education":"#3b82f6","Rural Upliftment":"#f97316","Nutrition":"#fb923c",
  "Water & Sanitation":"#14b8a6","Health":"#22c55e","Arts & Culture":"#ec4899",
  "Livelihood":"#8b5cf6","Skill Development":"#eab308","_default":"#6b7280"
};
```

---

#### Implementation contract (do not deviate)

- **Never key on `state_name`** (Unicode vs ASCII mismatch — `Bihār` vs `bihar`). Always `state_lgd` (zero-padded string).
- Use **Leaflet + topojson-client** (not D3) — handles 6,800 block polygons on canvas without DOM blow-up. `preferCanvas: true`.
- **No `localStorage` / `sessionStorage`** — Frappe Desk strips. Use in-memory cache keyed on LGD.
- Basemap: CARTO light (no token). One level of zoom control.
- `frappe.call` to `<app>.api.map_metrics` per level, whitelisted. Returns `[{key, metric, <user-picked fields>, portfolios:[{name,count}], aspirational}]`. See `assets/india-admin-geo/reference/api.py`.
- **Preet Vihar (Delhi) block:** `district_lgd` is null. Either override to `0174` (East Delhi) or filter out — flag to user in Phase 1.
- **Shadow DOM:** see frappe-build §6 for label-matching and `frappe.create_shadow_element` contract. Script tags inject inside the block, not parent document.

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
