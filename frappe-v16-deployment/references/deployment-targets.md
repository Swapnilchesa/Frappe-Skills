# Deployment Targets — Detailed Reference

> Full detail on JS bundle availability, CDN restrictions, sidebar navigation,
> iframe pitfalls, Server Script limits, and API virtual fields.
> Referenced from SKILL.md §4–14 — read the relevant section when needed.

---

## Table of Contents

- [§4 JS Bundle Availability by Context](#4-js-bundles)
- [§8 CDN and External Script Restrictions](#8-cdn)
- [§9 Sidebar and Navigation in v16](#9-sidebar)
- [§10 Bundle Hash Discovery](#10-bundle-hash)
- [§11 iframe Embedding Pitfalls](#11-iframe)
- [§12 Custom Workspace Themes (e.g., SVA)](#12-themes)
- [§13 Server Script Limitations](#13-server-scripts)
- [§14 API Field Names — Real vs Virtual](#14-api-fields)

---

## §4 JS Bundle Availability by Context {#4-js-bundles}

| Bundle | Desk Pages `/app/*` | Web Pages `/route` | Contents |
|--------|:-:|:-:|---|
| `libs.bundle.js` | ✅ | ✅ | jQuery, Moment.js, Socket.io client |
| `desk.bundle.js` | ✅ | ❌ | `frappe.call()`, `frappe.Chart`, `frappe.ui.*` |
| `frappe-web.bundle.js` | ❌ | ✅ | Minimal web context (no Chart, no desk UI) |
| `report.bundle.js` | Reports only | ❌ | Report-specific UI |
| `form.bundle.js` | Forms only | ❌ | Form-specific UI |

**Consequence:** A Web Page using `frappe.Chart` or `frappe.call()` fails silently. Use the frappe.call shim from Template C (references/working-templates.md) or load desk.bundle manually (see §10 for hash discovery).

**Shared JS across targets:** Any function shared between a CHB, Desk Page, or Client Script must use `frappe.provide` in a bundle loaded via `app_include_js` in `hooks.py`. See SKILL.md §4 for the full pattern.

---

## §8 CDN and External Script Restrictions {#8-cdn}

**Never load scripts from external CDNs inside Frappe pages.** Safari (Intelligent Tracking Prevention), Brave, and Firefox Enhanced Tracking Protection silently block:
- `cdnjs.cloudflare.com`
- `jsdelivr.net`
- `unpkg.com`
- `cdn.jsdelivr.net`

The script callback never fires → blank page with no error.

**Safe alternatives:**
- Use `frappe.Chart` (bundled, always available in desk context)
- Install Chart.js locally: `npm install chart.js@4.4.1 --prefix /tmp/chartjs`, copy UMD to script field
- Use Apache ECharts from same-origin upload
- Inline SVG for simple charts

**Detection:** If a dashboard works in Chrome but not Safari/Brave → CDN block is the cause.

---

## §9 Sidebar and Navigation in v16 {#9-sidebar}

v16 sidebar is app-based, not module-based. The key changes:
- Navigation via App Switcher (top-left icon)
- `Workspace Sidebar` is a new DocType (separate from `Workspace`)
- Form/list detail sidebar moved to **right side**
- `add_to_apps_screen` in `hooks.py` is mandatory for app to appear

For full step-by-step sidebar setup and all known v16 bugs, see:
`/mnt/skills/user/frappe-doctype-skill/references/v16-sidebar.md`

The doctype skill's sidebar guide is canonical — do not duplicate it here.

---

## §10 Bundle Hash Discovery {#10-bundle-hash}

Bundle filenames include a content hash that changes on every `bench build`.
**Never hardcode bundle hashes** — they break on every deployment.

```python
import requests, re

def get_bundle_hash(base, hdr, bundle_name="desk"):
    """Discover current bundle hash from the Frappe assets manifest."""
    r = requests.get(f"{base}/assets/frappe/dist/assets-manifest.json", headers=hdr)
    if r.status_code == 200:
        manifest = r.json()
        for key, value in manifest.items():
            if bundle_name in key and key.endswith(".js"):
                return value  # Returns the hashed filename
    # Fallback: scrape from login page
    r2 = requests.get(f"{base}/login", headers=hdr)
    matches = re.findall(r'src="(/assets/frappe/dist/js/' + bundle_name + r'\.[A-Z0-9]+\.js)"', r2.text)
    return matches[0] if matches else None

# Usage
hash_path = get_bundle_hash(BASE, HDR, "desk")
# → "/assets/frappe/dist/js/desk.bundle.QTB7ATHN.js"
```

**If hash discovery fails:** Use the dynamic loader approach:
```javascript
// Poll for frappe.Chart availability rather than hardcoding the path
function waitForFrappeChart(callback, attempts) {
    attempts = attempts || 0;
    if (typeof frappe !== 'undefined' && frappe.Chart) {
        callback();
    } else if (attempts < 20) {
        setTimeout(function() { waitForFrappeChart(callback, attempts + 1); }, 100);
    }
}
```

---

## §11 iframe Embedding Pitfalls {#11-iframe}

Common issues when embedding Frappe pages inside iframes:

| Problem | Cause | Fix |
|---|---|---|
| White strip at bottom | Body margin/padding | Add `body { margin: 0; padding: 0; }` to embedded page |
| Scrollbar appears | Content slightly exceeds iframe height | Use `overflow: hidden` on body + JS `postMessage` for dynamic height |
| CSRF token errors | Cross-origin iframe | Only embed same-origin Frappe URLs |
| Auth not passing | Cookies not sent cross-origin | Use same-domain embedding only |
| Content Security Policy block | Frappe default CSP blocks iframing | Set `x_frame_options = "SAMEORIGIN"` in `site_config.json` |

**Correct iframe embed pattern:**
```html
<iframe
  src="/app/my-workspace"
  style="width:100%; height:600px; border:none; display:block;"
  sandbox="allow-same-origin allow-scripts allow-forms"
></iframe>
```

**Avoid negative margins** (`margin-top: -60px`) to hide Frappe header — this is fragile and breaks on version updates. Instead, use the `show_title: 0` field on Web Pages or `frappe.ui.make_app_page` for Desk Pages.

---

## §12 Custom Workspace Themes (e.g., SVA) {#12-themes}

Some Frappe deployments use custom workspace themes that override default rendering.

**Detection:**
```python
# Check for custom desk.bundle overrides
r = requests.get(f"{BASE}/api/method/frappe.client.get_value",
    headers=HDR,
    params={"doctype": "System Settings", "fieldname": "desk_theme"})
theme = r.json().get("message", {}).get("desk_theme", "Light")
print(f"Desk theme: {theme}")

# Check for custom app bundles
r2 = requests.get(f"{BASE}/login", headers=HDR)
custom_bundles = re.findall(r'src="(/assets/[^/]+/dist/[^"]+\.js)"', r2.text)
print("Custom bundles:", [b for b in custom_bundles if 'frappe' not in b])
```

**Impact on CHBs:** Custom themes may inject additional CSS that overrides `:host` styles in shadow DOM, or modify workspace content rendering. If a CHB looks correct in dev but wrong in prod, check for custom theme overrides.

**Safe practice:** Use CSS variables (`var(--primary-color)`) over hardcoded hex values — custom themes typically define these variables, so your CHB inherits the theme automatically.

---

## §13 Server Script Limitations {#13-server-scripts}

Server Scripts run Python in a sandboxed environment. Key restrictions:

| Feature | Available? | Notes |
|---|---|---|
| `frappe.db.sql()` | ✅ | With `as_dict=True` |
| `frappe.get_doc()` | ✅ | |
| `frappe.get_list()` | ✅ | |
| `import` statements | ❌ | Cannot import Python modules |
| `frappe.sendmail()` | ✅ | |
| `frappe.cache()` | ✅ | |
| File system access | ❌ | No `open()`, `os`, `pathlib` |
| External HTTP requests | ❌ | No `requests`, `urllib` |
| `frappe.whitelist` | ❌ | Use custom app method instead |

**When Server Script is not enough:** Move logic to a whitelisted Python method in a custom app. Server Scripts are suitable for simple automation; complex business logic belongs in controllers.

---

## §14 API Field Names — Real vs Virtual {#14-api-fields}

Some Frappe fields appear in `as_dict()` output but are NOT database columns. Setting them via API silently does nothing.

| DocType | Field | DB Column? | Notes |
|---|---|---|---|
| Page | `script` | ❌ Virtual | Read from filesystem. Write requires `developer_mode` |
| Page | `style` | ❌ Virtual | Read from filesystem |
| Page | `content` | ❌ Virtual | Read from filesystem |
| Web Page | `main_section_html` | ✅ | v15+ field name (was `main_section` in older versions) |
| Web Page | `main_section` | ✅ | Legacy field — check your version |
| Workspace | `content` | ✅ | JSON string of block array |
| Workspace | `custom_blocks` | ✅ (child table) | Separate from `content` — must be synced |
| Custom HTML Block | `script` | ✅ | Stored in DB, writable via API |
| Custom HTML Block | `html` | ✅ | Stored in DB |

**Version check for Web Page field name:**
```python
r = requests.get(f"{BASE}/api/resource/Web Page/{page_name}", headers=HDR)
data = r.json().get("data", {})
# v15+: 'main_section_html' key present
# older: 'main_section' key
field = "main_section_html" if "main_section_html" in data else "main_section"
```
