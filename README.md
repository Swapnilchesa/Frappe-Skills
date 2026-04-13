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
