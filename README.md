# Frappe Skills

AI agent skills for building, designing, and deploying on Frappe Framework v15/v16.

## 3 Skills

| Skill | Purpose | When to load |
|---|---|---|
| **frappe-build** | Deployment — Pages, Web Pages, CHBs (Shadow DOM), Client Scripts (form + list view), Workspaces, Server Scripts. Config-vs-Code decisions. Platform Order. Cache invalidation. | Any time code is being deployed to Frappe |
| **frappe-design** | Data design (DocType specs, fields, permissions, workflows) + Visual design (dashboard aesthetic, component library, infographic charts, India maps). | Any time speccing or designing UI |
| **frappe-reports** | Script Reports — safe_exec sandbox, SQL injection prevention, filter/column storage, workspace wiring. | Only when building Script Reports |

## Installation

### Claude Code / Cowork
Place each skill folder in `~/.claude/skills/` or your project's skills directory.

### Cross-References
- `frappe-build` references `frappe-design` for specs and `frappe-reports` for report deployment
- `frappe-design` includes a `REFERENCE.md` companion file with CSS tokens, hex values, and component code templates
- `frappe-reports` is self-contained but references `frappe-build` for general deployment patterns

## Origin

Built from real production deployment sessions on Frappe v16 instances. Every rule maps to a documented failure. Incorporates patterns from the [Builder Protocol](https://prody-dris.github.io/ai-playground-sessions/frameworks/builder-protocol.html).

## License

MIT


## Bundled data asset — `assets/india-admin-geo/`

Canonical India admin hierarchy (State → District → CD Block), LGD-keyed, web-optimised TopoJSON.
Shipped in this repo so the `frappe-design` skill can build drill-down maps without any external
data pipeline.

| File | Features | jsDelivr URL |
|---|---:|---|
| `topo/states.json` | 36 | `https://cdn.jsdelivr.net/gh/Swapnilchesa/Frappe-Skills@main/assets/india-admin-geo/topo/states.json` |
| `topo/districts.json` | 780 | `https://cdn.jsdelivr.net/gh/Swapnilchesa/Frappe-Skills@main/assets/india-admin-geo/topo/districts.json` |
| `topo/blocks.json` | 6,803 | `https://cdn.jsdelivr.net/gh/Swapnilchesa/Frappe-Skills@main/assets/india-admin-geo/topo/blocks.json` |

See `assets/india-admin-geo/README.md` for schema, install-time copy instructions, and provenance. Drop-in CHB code is at `assets/india-admin-geo/reference/custom_html_block.html`. The design pattern and ColorBrewer picker lives in `frappe-design/REFERENCE.md` §6.6.

Data license: **ODbL-1.0** (derived from geoBoundaries + Survey of India). The skill files themselves remain MIT.
