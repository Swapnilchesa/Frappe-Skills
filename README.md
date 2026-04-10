# Frappe Skills

A curated library of Claude AI skills used at **[Dhwani RIS](https://dhwaniris.com)** whenever a custom project is developed on the [Frappe Framework](https://frappeframework.com) (v15/v16). Each skill is a structured instruction set that Claude reads before executing a task — replacing ad-hoc prompting with a repeatable, version-controlled standard. Loading a skill ensures Claude follows the same design contracts, deployment patterns, and code conventions across every project, every session, without re-explaining context.

---

## Skills

### [`frappe-dashboard-design`](./frappe-dashboard-design/)

The binding design system for every dashboard, page, widget, or UI component built inside Frappe. It enforces a "Refined Utility" aesthetic — Shadcn-level restraint with elevated craft — covering KPI card anatomy, ColorBrewer chart palettes, Indian number formatting (`1.5L`, `₹12Cr`), India choropleth maps with `fitBounds()` drill-down, and a mandatory filter strip on every page. Includes three new chart types: **Sankey diagrams** (eCharts, always ask user first), **lollipop charts** (preferred over horizontal bars for ranking data), and a **GitHub-style calendar heatmap** for daily cadence data. Expanded with full NFR coverage: WCAG 2.1 AA accessibility rules, performance budgets, error state specs (API error / permission / timeout), responsive breakpoints (4→2→1 col), drawer/side-panel, modal, multi-select filters, timeline component, and print/export patterns. Apply this skill before writing a single line of HTML, CSS, or JS for any Frappe page.

---

### [`frappe-doctype-skill`](./frappe-doctype-skill/)

Governs the design, specification, and review of Frappe DocTypes before any code is written. It produces complete, Claude Code-ready DocType schemas covering every field property (`depends_on`, `fetch_from`, `in_list_view`, `search_index`, `permlevel`), workflow state definitions with Frappe indicator colors, permissions matrices, and list view configuration. Covers both Frappe v15 and v16, with explicit handling of v16's sidebar changes and the new `custom_blocks` workspace pattern. The skill's output is a spec document that a developer or Claude Code session can execute without needing to ask follow-up architecture questions. Use it for any new feature discussion, DocType redesign, workflow planning, or approval chain setup.

---

### [`frappe-custom-html-block`](./frappe-custom-html-block/)

Solves the non-obvious deployment of Custom HTML Blocks (CHBs) inside Frappe v15/v16 Workspaces via the REST API — without SSH or `developer_mode`. The skill documents the shadow DOM rendering context (all DOM queries must use `root_element`, not `document.getElementById()`), the exact label-match rule between `custom_blocks` child table and workspace content JSON (mismatch causes silent blank renders), the mandatory three-field split (HTML / CSS / JS in separate `html`, `style`, `script` fields), and the CDN restriction (external scripts fail inside shadow DOM — use `frappe.Chart` or inline). Essential reading before deploying any dashboard widget, KPI card, or interactive element directly into a Frappe Workspace.

---

### [`frappe-v16-deployment`](./frappe-v16-deployment/)

A comprehensive knowledge base for deploying custom Pages, Workspaces, and HTML Blocks on Frappe v15/v16 instances — particularly when accessed only via REST API without bench or SSH access. Documents the four deployment targets (standalone Frappe Page, Custom HTML Block, Script Report, standard Desk view) and when each is appropriate, the `developer_mode` dependency for file-based JS/CSS, the `add_to_apps_screen["name"]` lowercase enforcement, workspace sidebar visibility rules (a workspace is invisible unless a role has read permission on at least one of its DocTypes), and JS bundle availability per deployment context. Read this skill before writing any deployment script or attempting to wire a custom page into the Frappe navigation.

---

## Usage

These skills are consumed by Claude (via [Claude.ai](https://claude.ai) or [Claude Code](https://claude.ai/code)) before executing Frappe-related tasks. In Claude.ai, reference a skill by pointing Claude at the relevant `SKILL.md` file path. In Claude Code, add the skill path to your `CLAUDE.md` or reference it in your session context.

Each skill folder follows this structure:

```
skill-name/
├── SKILL.md          # The primary instruction set — Claude reads this first
├── REFERENCE.md      # Extended code snippets, tokens, and component specs (where applicable)
└── evals/
    └── evals.json    # Test cases for validating skill performance
```

Skills are designed to be **composable**. A typical Frappe project activates multiple skills in sequence — `frappe-doctype-skill` to review the data model, `frappe-dashboard-design` for admin UI, and `frappe-custom-html-block` or `frappe-v16-deployment` for wiring pages into Frappe Desk.

---

## Contributing

Skills are updated as real project failures surface new edge cases. When adding or updating a skill:

1. Keep `SKILL.md` to binding rules and decision logic — things Claude must always do
2. Move verbose code snippets and reference tables to `REFERENCE.md`
3. Add a test case to `evals/evals.json` for the scenario that prompted the change
4. Update this README's five-line summary to reflect the new capability

---

## License

MIT — see [LICENSE](./LICENSE)
