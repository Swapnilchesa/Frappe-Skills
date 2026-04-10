---
name: frappe-dashboard-design
description: >
  Binding design system for every dashboard, page, widget, or UI component built on the Frappe framework.
  Use this skill whenever: building Frappe Page HTML dashboards, Frappe client scripts with UI,
  Frappe Workspace customizations, ERPNext page design, mGrant dashboards, NGO dashboards,
  grant management UI, program MIS interfaces, CSR dashboards, donor dashboards,
  or any data-visualization interface inside ERPNext/Frappe (v15 or v16).
  Also use when the user says "make a dashboard", "design a page", "build a UI",
  "create a Frappe page", or references KPI cards, filter strips, or India maps in a Frappe context.
  Produces a "Refined Utility" aesthetic — Shadcn-level restraint with elevated craft,
  ColorBrewer palettes, Indian number formatting, and pixel-perfect alignment.
  ALWAYS apply this skill BEFORE writing any HTML, CSS, or JS for Frappe dashboards — even for quick prototypes.
---

# Frappe Dashboard Design System

This skill is a **binding design contract**. Follow every rule. No exceptions. No creative reinterpretation unless the user explicitly overrides a specific rule.

**Frappe version compatibility**: This skill targets **Frappe v15 and v16**. In v16, the sidebar is fixed-width and always visible — never collapse or override it. The Page API (`frappe.ui.make_app_page`) works identically across both versions. If the user specifies a version, honor it; otherwise assume v16.

Before writing any code, read this file completely, then read `REFERENCE.md` in this same directory for the **complete CSS tokens, hex values, code snippets, and component specs** — every `§` reference in this file points to a section there.

## Design Philosophy — "Refined Utility"

The aesthetic is a better-than-Shadcn approach combining:

- **Shadcn's restraint**: Clean surfaces, consistent spacing, predictable component anatomy
- **Elevated craft**: Subtle shadows, micro-animations, considered iconography
- **Data-first clarity**: Every pixel serves comprehension — no decorative noise
- **Clear CTAs & Nudges**: Every screen must answer "what should I do next?"

**The Golden Rule**: If a user squints at the screen, the most important number or action must still be visually dominant.

---

## Critical Rules — Never Violate

These 8 rules are non-negotiable. Check every one before outputting code.

### Rule 1: Zero Whitespace Waste

No unintended whitespace anywhere. Every gap must be a deliberate multiple of 4px. Use the spacing scale from REFERENCE.md. Cards in a row must have identical heights (`align-items: stretch` or explicit `min-height`). No orphan cards floating in empty space.

### Rule 2: Names, Not IDs

Never display internal IDs, doctype names, or link field values to the user. Always resolve to human-readable names. Show `Pratham Education Foundation`, not `GRT-00042`. Show `Active`, not `1`. Show `Mumbai`, not `MH-MUM`.

### Rule 3: Indian Number Formatting

Use `Intl.NumberFormat('en-IN')` for ALL numbers. For KPI cards use shortened forms: `1K`, `1.5L`, `1Cr`. Always show the full number in a tooltip on hover. Never display raw unformatted numbers like `100000`. See REFERENCE.md §4 for complete rules.

### Rule 4: India Heatmap with fitBounds + Drill-down

When building India map visualizations: use TopoJSON, always call `fitBounds()` so the map fills its container (no tiny map in big whitespace), default to state-level choropleth, click state to drill to district view, include a "Back to India" button, use ColorBrewer sequential palette. See REFERENCE.md §6.5 for full spec.

### Rule 5: Frappe Sidebar + Top Tabs

Never customize the Frappe sidebar — use it as-is. Use horizontal top tabs within the page content area for sub-navigation (Overview, Grants, Reports, Settings). Active tab gets `--color-info` text + 2px bottom border.

### Rule 6: Mock Data Banner

When the dashboard uses demo, test, or hardcoded data, always show a persistent top banner with a diagonal-striped amber background: `"⚠ Displaying mock data — Connect API for live data"`. Remove only when live API is connected. See REFERENCE.md §9.3 for CSS.

### Rule 7: Universal Filters

Every dashboard page must have a filter strip below the tabs: Date Range, Entity/Organization, Status, Search, Reset Filters. All charts, tables, and cards on the page must react to filter changes. Show active filter count badge. "Reset Filters" appears only when filters are active.

### Rule 8: Light Theme + Subtle Motion

Always light theme. Background: `#F9FAFB`. Card surfaces: `#FFFFFF`. Cards lift on hover (`translateY(-1px)` + shadow elevation). KPI numbers count up on page load (600ms). Charts animate on first render (bars grow, lines draw). Use skeleton shimmer during loading. Never use dark mode unless explicitly requested.

### Rule 9: Chart Type Prompting — Sankey, Lollipop, GitHub Heatmap

**Before choosing a chart type, apply these three prompts:**

**Sankey Prompt** — Whenever data has a flow, funnel, or allocation structure (budget distribution, grant pipeline stages, fund routing, beneficiary pathways), **stop and ask the user**: *"This data has a flow structure — would you like a Sankey diagram using eCharts? It will show volume and routing between stages with hover tooltips."* If yes, use eCharts Sankey (not Chart.js). See REFERENCE.md §12.1 for full spec.

**Lollipop Prompt** — Whenever you would use a horizontal bar chart, **first consider**: does the exact bar length matter, or is the ranking and relative magnitude the key insight? If ranking/comparison is the point, prefer a lollipop chart (dot + stem). It reduces ink, shows rank more clearly, and avoids bar-fill distraction. Only keep horizontal bars when cumulative fill (stacked) or precise area comparison is required. See REFERENCE.md §12.2.

**GitHub Heatmap Prompt** — Whenever data has a time × intensity grid (submissions per day over months, activity calendars, disbursement frequency, report submission patterns), **offer the GitHub-style calendar heatmap** as an option. It shows temporal density better than any line or bar chart for daily/weekly cadence data. See REFERENCE.md §12.3.

---

## Page Structure Template

Every Frappe dashboard page follows this structure top-to-bottom:

```
┌─────────────────────────────────────────────────┐
│  Frappe Sidebar (standard, unmodified)          │
├─────────────────────────────────────────────────┤
│  Top Tab Bar (horizontal sub-navigation)        │
├─────────────────────────────────────────────────┤
│  Universal Filter Strip                         │
│  [Date Range] [Entity] [Status] [Search] [Reset]│
├─────────────────────────────────────────────────┤
│  KPI Summary Cards Row (3-4 cards, equal height)│
├─────────────────────────────────────────────────┤
│  Charts Row / Map Section (1-2 charts)          │
├─────────────────────────────────────────────────┤
│  Data Table Section (with sort + pagination)    │
└─────────────────────────────────────────────────┘
```

Do not deviate from this order. If a section is not needed, omit it but do not reorder the remaining sections.

---

## Component Quick-Reference

Detailed CSS and specs are in REFERENCE.md. Here is the anatomy you must follow for each component.

### KPI / Metric Cards

This is the **signature component**. Every KPI card must have exactly this anatomy:

```
┌─────────────────────────────────────┐
│  ┌──────┐                           │
│  │ Icon │   (40x40, rounded 10px,   │
│  └──────┘    semantic tinted bg)     │
│                                     │
│  1,247                              │  ← 28px, weight 700, --gray-900
│                                     │
│  Active Grantees                    │  ← 14px, weight 400, --gray-500
│                                     │
│  ↑ 8% vs last FY                   │  ← 12px, green for positive, red for negative
└─────────────────────────────────────┘
```

- White background, `border-radius: 12px`, elevation-1 shadow
- Hover: elevation-2 + `translateY(-1px)` over 150ms
- Number must use Indian formatting or shortened form
- Growth indicator MUST include comparison context ("vs last FY", "MoM")
- Positive = green `↑`, Negative = red `↓`, Neutral = gray `–`
- Full number shown in tooltip on hover

### Status Chips

**Every status field must render as a colored chip. Never plain text.**

- Fully rounded (`border-radius: 9999px`), 12px font, weight 500
- Tinted background + matching dark text (e.g., green-50 bg + green-600 text)
- Optional leading dot (6px circle) for table rows
- Standard mapping: Active→green, Pending→amber, Rejected→red, Inactive→gray, New→blue, On Hold→purple
- See REFERENCE.md §6.2 for full hex values

### Tables

- Left-align text, right-align numbers, center-align status chips and actions
- Sticky header row with uppercase labels (12px, weight 600, `--gray-500`)
- Row hover: `--gray-50` background
- Min row height: 48px
- Paginate at 20 rows default with "Showing 1–20 of 1,247" footer
- Wrap the table in a card with `border-radius: 12px` and `overflow: hidden`
- Empty state: centered icon + headline + helpful subtext + CTA

### Charts

- Always use ColorBrewer palettes — write the palette name as a code comment
- Include tooltips with full formatted numbers
- Axis labels: 12px, `--gray-500`
- Grid lines: `--gray-100`, dashed, 1px
- Legend: below chart, horizontal layout
- Animate on first load: bars grow up (400ms), lines draw left-to-right (500ms)
- Never use pie charts — use donut charts for part-to-whole
- See REFERENCE.md §6.4 for chart type selection guide (updated with new types below)

#### Sankey Diagram (eCharts)
- Use eCharts, not Chart.js — `import * as echarts from 'https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.esm.min.js'`
- **Always ask the user first** (see Rule 9) — never auto-select Sankey
- Nodes: use semantic colors from §2.3; left-to-right flow direction
- Hover: show source → target label + formatted volume + % of total flow
- Node labels: always visible, not overlap; 13px Inter
- See REFERENCE.md §12.1 for full eCharts config

#### Lollipop Chart
- Preferred over horizontal bars for pure ranking/comparison use cases
- Dot: 10px circle, filled with ColorBrewer color; Stem: 2px line, `--gray-200`
- Animate: stems grow left-to-right (400ms), dots pop in with `--ease-spring` (500ms)
- Label: value right-aligned after the dot; category name left of stem
- See REFERENCE.md §12.2

#### GitHub Calendar Heatmap
- Use for time × frequency/intensity data (daily/weekly cadence over months)
- 7-row grid (Mon–Sun), columns = weeks; cell size 12px, gap 3px, border-radius 3px
- Color: ColorBrewer Blues 5-step (empty cell = `--gray-100`)
- Hover tooltip: exact date + formatted count
- Month labels above column groups; day labels (M/W/F) left of rows
- See REFERENCE.md §12.3

### Buttons & CTAs

- One primary CTA per section maximum
- Primary (filled blue) → Secondary (outlined) → Ghost (text only) → Danger (red, destructive only)
- Primary CTA always right-aligned or bottom-right of its container
- "View All →" links go bottom-right of card sections
- Cancel/Back always goes left of the primary CTA

### Nudges

Show contextual nudge bars for actionable items:
- Pending approvals → amber: "5 grants awaiting your review →"
- Overdue items → red: "3 reports overdue by 7+ days →"
- Setup incomplete → blue: "Complete your profile to unlock dashboards →"
- Success → green (auto-dismiss 5s): "Report submitted ✓"

### Empty States

Every empty state must include:
1. Subtle icon or illustration (64px, `--gray-300`)
2. Headline: "No active grantees yet"
3. Subtext: "Grantees will appear here once grants are disbursed."
4. CTA if applicable: `[+ Add Grantee]`

---

## Color Rules

- **Base palette**: Neutral gray scale from `--gray-50` (#F9FAFB) to `--gray-900` (#111827). See REFERENCE.md §2.1.
- **Semantic colors**: Success green, Warning amber, Danger red, Info blue — each with a light tint background variant. See REFERENCE.md §2.3.
- **Data visualization**: ALWAYS source from ColorBrewer2.org. Recommended palettes: Set2 (qualitative), YlOrRd (sequential/heatmaps), RdYlGn (diverging), Blues (sequential cool). See REFERENCE.md §2.2. Never pick chart colors by feel or intuition.

---

## Typography Rules

- **Font**: `'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`
- **Monospace**: `'JetBrains Mono', 'Fira Code', monospace`
- **Scale**: 36px display → 28px KPI numbers → 20px section headings → 16px card titles → 14px body → 13px secondary → 12px captions → 11px overline
- **Text colors**: Headings `--gray-800`, body `--gray-600`, secondary `--gray-500`, disabled `--gray-400`
- See REFERENCE.md §3 for the full type scale table

---

## Animation Timing

```css
--ease-default: cubic-bezier(0.4, 0, 0.2, 1);
--duration-fast: 100ms;     /* button press */
--duration-normal: 200ms;   /* hover states, tooltips */
--duration-slow: 300ms;     /* page load stagger, modals */
```

- Card hover: 150ms translateY + shadow
- KPI count-up: 600ms ease-out
- Chart bars: 400ms ease-out
- Chart lines: 500ms ease-out
- Page load cards: 300ms fade+slide, 50ms stagger between cards
- Skeleton shimmer: 1.5s infinite pulse
- See REFERENCE.md §8 for the full animation table

---

## Shadows — Three Levels Only

| Level | Use | CSS |
|-------|-----|-----|
| elevation-1 | Cards at rest | `0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.06)` |
| elevation-2 | Cards on hover, modals | `0 4px 12px rgba(0,0,0,0.08), 0 2px 4px rgba(0,0,0,0.04)` |
| elevation-3 | Popovers, floating panels | `0 12px 24px rgba(0,0,0,0.12), 0 4px 8px rgba(0,0,0,0.06)` |

Cards default to elevation-1. On hover, transition to elevation-2 over 200ms.

---

## NFR Standards

These apply to every dashboard without exception.

### Accessibility (WCAG 2.1 AA)
- Minimum contrast: 4.5:1 for body text, 3:1 for large text and UI controls
- All interactive elements must have `:focus-visible` ring: `outline: 2px solid var(--blue-500); outline-offset: 2px`
- Icon-only buttons must have `aria-label`
- Status chips: add `aria-label="Status: Active"` (never rely on color alone)
- KPI count-up: wrap in `aria-live="polite"` so screen readers announce final value
- Charts: always include `aria-label` describing what the chart shows; provide a summary caption
- Skeleton loaders: `aria-busy="true"` on container during load, `aria-busy="false"` after
- See REFERENCE.md §13 for full tokens and focus ring CSS

### Performance Budget
- Max 3 Chart.js instances per page render — beyond that, use deferred/lazy rendering
- eCharts (for Sankey): load from CDN, not bundled; lazy-init on tab visibility
- Filter interactions: debounce at 300ms before triggering `frappe.call()`
- Independent API calls: always parallelized with `Promise.all()` — never serial chain
- Chart re-render on filter change: destroy and recreate instance — never mutate data in place (Chart.js mutation causes ghost renders)
- India map TopoJSON: always lazy-load the JSON file from CDN; never inline
- See REFERENCE.md §19

### Error States
Three error states are mandatory — spec them before writing any API call:
- **API Error / 500**: Red nudge bar in the affected section + Retry button
- **Permission Error (403)**: Gray locked card — `"You don't have access to this data"`
- **Timeout (>8s)**: Skeleton replaced by warning — `"Taking longer than usual…"`
- See REFERENCE.md §14 for CSS + HTML

### XSS Prevention
- Never use `.innerHTML` with raw API response data — always use `textContent` or `frappe.utils.escape_html()`
- `frappe.render_template()` is safe — prefer for templated content
- All user-generated strings going into DOM must be escaped

### Filter State Persistence
- Persist active filters to `sessionStorage` keyed as `dashboard_{page_name}_filters`
- Restore on re-visit; clear on explicit "Reset Filters"
- See REFERENCE.md §19 for snippet

### Responsive Breakpoints
- Desktop ≥1280px: 4-col KPI grid, full filter strip, full map
- Tablet 768–1279px: 2-col KPI grid, filter strip wraps to 2 rows
- Mobile ≤767px: 1-col KPI grid, filter strip collapses to "Filters" button + drawer
- Tables: horizontal scroll on tablet/mobile — preserve min-width, never truncate data
- India map: min-height 300px on mobile; `fitBounds()` still required
- See REFERENCE.md §20

### Print / Export
- Every table section gets a top-right "Export" ghost button: dropdown → CSV / Excel / Print
- `@media print`: hide sidebar, filter strip, action buttons; expand table; remove shadows
- Chart PNG export: `chart.toBase64Image()` for Chart.js; `chart.getDataURL()` for eCharts
- See REFERENCE.md §21

---

## Extended UI Components

### Drawer / Side Panel
- 480px wide, slides in from right, `rgba(0,0,0,0.3)` backdrop
- Header: title + close (×); Body: 24px padding, scrollable; Footer: sticky, primary left + secondary right
- Trigger: clicking any table row or a detail link
- Close on: × button, Escape key, backdrop click
- See REFERENCE.md §15

### Modal / Confirmation Dialog
- Max-width 480px, centered, backdrop `blur(2px)` + `rgba(0,0,0,0.4)`
- Two types: **Confirmation** (icon + message + Cancel/Confirm) and **Form modal** (title + body + footer)
- Destructive action: red primary button; never pre-focus "Confirm" on destructive modals
- Focus trap: Tab key cycles within modal while open
- See REFERENCE.md §16

### Multi-Select Filter
- Dropdown with checkboxes, "Select All / Clear" at top
- Selected count badge on filter button: `Status (2)`
- Active chip strip below filter bar with × per chip
- Full keyboard nav: arrow keys to move, Space to toggle, Enter to confirm
- See REFERENCE.md §17

### Timeline / Activity Feed
- Vertical timeline, left-aligned connector line in `--gray-200`
- Each event: colored dot (8px) + timestamp (`--gray-400`) + actor + action
- Collapse at 5 events: "Show N more ↓"
- Event types: Created (blue), Approved (green), Rejected (red), Updated (amber), Commented (gray)
- See REFERENCE.md §18

### Tooltip (Universal Spec)
- Max-width 240px; dark bg (`--gray-900`, 90% opacity); white text; `border-radius: 6px`; 8px padding
- Appear after 400ms delay (prevents flicker on fast mouse movement)
- Auto-reposition if viewport-clipped — prefer opposite side
- Required on: all KPI numbers (full value), all truncated text, all status chips in dense views

---



## Pre-Flight Checklist

Before outputting any dashboard code, mentally verify ALL of these:

**Numbers & Data**
- [ ] All numbers use Indian comma formatting (`1,00,000`)
- [ ] KPI cards show shortened numbers with tooltip for full value
- [ ] Currency shows ₹ symbol with proper formatting
- [ ] Percentages max 1 decimal. Dates use DD Mon YYYY.
- [ ] Names shown everywhere, never IDs

**Layout & Alignment**
- [ ] Card row heights are equal
- [ ] All four edges of card rows aligned
- [ ] Consistent `gap` between cards (no ad-hoc margins)
- [ ] Tables: text-left, numbers-right, status-center
- [ ] Page follows structure template (tabs → filters → KPIs → charts → table)

**Visual Quality**
- [ ] Cards have elevation-1 shadow with hover lift
- [ ] ALL status fields are colored chips
- [ ] KPI cards: icon + number + label + growth indicator
- [ ] Charts use ColorBrewer palette (name in comment)
- [ ] Skeleton loading during data fetch
- [ ] Empty states have icon + headline + subtext + CTA
- [ ] Mock data banner if using test data

**Interactions & Frappe**
- [ ] Hover, count-up, chart animations all present
- [ ] Filters affect all widgets
- [ ] Frappe sidebar unmodified, top tabs for sub-nav
- [ ] API calls use `frappe.call()` properly
- [ ] Light theme enforced

**Chart Type Prompts (Rule 9)**
- [ ] If flow/allocation data → asked user about Sankey (eCharts)
- [ ] If horizontal bar → considered lollipop alternative
- [ ] If time × frequency/intensity data → considered GitHub calendar heatmap

**NFR**
- [ ] No raw `.innerHTML` with unsanitized API data (XSS)
- [ ] All interactive elements have `:focus-visible` ring
- [ ] Error states defined: API error, permission error, timeout
- [ ] Independent `frappe.call()` calls parallelized with `Promise.all()`
- [ ] Filter debounced at 300ms
- [ ] Responsive breakpoints applied (4-col → 2-col → 1-col)
- [ ] Export button on every table section

---

## Do's and Don'ts — Quick Scan

| ✅ DO | ❌ DON'T |
|-------|----------|
| ColorBrewer palettes for all data viz | Pick chart colors by intuition |
| Numbers as `1,00,000` or `1.5L` | Display raw `100000` |
| Status as colored chips | Status as plain text |
| Align all edges of card rows | Uneven card heights |
| Show names, not IDs | Display `GRT-00042` |
| elevation-1 shadows on cards | Flat cards or heavy drop shadows |
| Subtle animations on load + hover | Flashy or distracting animations |
| Skeleton loading states | Blank screens or spinners only |
| Right-align numbers in tables | Left-align numbers |
| Growth indicators with comparison context | "+8%" without context |
| One primary CTA per section | Multiple competing primary buttons |
| Donut charts for part-to-whole | Pie charts (ever) |
| Consistent 4px-multiple spacing | Arbitrary padding/margins |
| `fitBounds()` on India maps | Tiny map in big container |
| Ask user before adding Sankey | Auto-select Sankey without prompting |
| Lollipop for ranking comparisons | Horizontal bar when fill area doesn't add meaning |
| GitHub heatmap for daily cadence data | Line chart for daily submission patterns |
| `textContent` / `escape_html()` for API data | Raw `.innerHTML` with API responses |
| `Promise.all()` for parallel API calls | Serial `frappe.call()` chains |
| `:focus-visible` ring on all interactive elements | Removing default focus outlines |
| Error state for every API call | Silently failing with empty UI |

---

**Now read `REFERENCE.md` in this directory.** It contains: §1 Spacing, §2 Colors + ColorBrewer palettes, §3 Typography, §4 Indian number formatting with code, §5 Shadows, §6 Full component CSS (KPI cards, status chips, filter strip, chart defaults, India map), §7 Tab bar, §8 Animation timing with code snippets, §9 Mock banner + skeleton + nudge bars, §10 Buttons, §11 Frappe-specific patterns, §12 New chart types (Sankey/eCharts, Lollipop, GitHub heatmap), §13 Accessibility, §14 Error states, §15 Drawer/side panel, §16 Modal, §17 Multi-select filter, §18 Timeline, §19 Performance + filter persistence, §20 Responsive breakpoints, §21 Print/export. Do not write any code before reading it.

