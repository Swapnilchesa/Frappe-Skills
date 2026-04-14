---
name: frappe-build
description: >
  Complete deployment and build skill for Frappe v15/v16 — covers Pages, Web Pages, Custom
  HTML Blocks (CHBs with Shadow DOM), Client Scripts (form and list view), Workspaces, and
  Server Scripts. Includes the Config-vs-Code decision framework, Platform Order for greenfield
  builds, cache invalidation, CDN restrictions, bundle discovery, and the Layer Stack discipline.
  MUST READ before deploying ANY code to a Frappe instance. Triggers on: deploying to Frappe,
  building Frappe UI, Client Script, Custom HTML Block, CHB, workspace wiring, shadow DOM,
  form enhancement, list view customization, cache clearing, developer_mode, Property Setter,
  Translation record, or any API-based Frappe deployment without SSH/bench access.
  Cross-references: frappe-design (for DocType specs and visual design), frappe-reports (for Script Reports).
---

# Frappe Build & Deployment Skill

> **Purpose**: This skill prevents Claude from making repeated errors when deploying custom
> dashboards, Client Scripts, Custom HTML Blocks, and UI to Frappe instances. Every section
> documents a real mistake and the correct approach. Read this ENTIRELY before writing any
> deployment code.
>
> **Part A** covers deployment targets, infrastructure, and decision frameworks.
> **Part B** covers Custom HTML Blocks in deep detail (Shadow DOM, label matching, workspace wiring).

---

## Table of Contents

1. [Frappe Page Architecture — How It Actually Works](#1-frappe-page-architecture)
2. [The developer_mode Gate](#2-the-developer_mode-gate)
3. [Four Deployment Targets Compared](#3-four-deployment-targets)
4. [JS Bundle Availability by Context](#4-js-bundle-availability)
5. [Workspace Content JSON Structure](#5-workspace-content-json)
6. [Custom HTML Block — Correct Usage](#6-custom-html-block)
7. [Web Page — Limitations and Workarounds](#7-web-page)
8. [CDN and External Script Restrictions](#8-cdn-restrictions)
9. [Sidebar and Navigation in v16](#9-sidebar-and-navigation)
10. [Bundle Hash Discovery](#10-bundle-hash-discovery)
11. [iframe Embedding Pitfalls](#11-iframe-embedding)
12. [Custom Workspace Themes (e.g., SVA)](#12-custom-workspace-themes)
13. [Server Script Limitations](#13-server-script-limitations)
14. [API Field Names — What's Real vs Virtual](#14-api-field-names)
15. [Decision Tree — Which Deployment Path?](#15-decision-tree)
16. [Pre-Flight Checklist](#16-pre-flight-checklist)
17. [Working Code Templates](#17-working-code-templates)
18. [Client Script Deployment — Form and List View](#18-client-script-deployment)
19. [Cache Invalidation](#19-cache-invalidation)
20. [Platform Order — Greenfield Build Sequence](#20-platform-order)

**Part B — Custom HTML Blocks (Deep Reference)**

21. [How CHBs Render — Shadow DOM](#1-shadow-dom)
22. [The Critical Label-Match Rule](#2-label-match)
23. [DOM Querying — What Works vs What Fails](#3-dom-querying)
24. [Three-Field Split](#4-three-fields)
25. [Workspace Wiring — content JSON + child table sync](#5-workspace-wiring)
26. [Chart Libraries — CDN Will Fail](#6-charts)
27. [page_data Discovery](#7-page-data)
28. [CHB Pre-Flight Checklist](#8-checklist)
29. [CHB Debugging Protocol](#9-debug)
30. [CHB Post-Mortem](#10-postmortem)

---

## 1. Frappe Page Architecture — How It Actually Works {#1-frappe-page-architecture}

### âŒ WRONG ASSUMPTION (Claude kept making this error)

> "I'll create a Page via API and set the `script` and `style` fields — they'll persist in the database."

### ✅ REALITY

The **Page doctype** in Frappe stores `script`, `style`, and `content` fields **on the filesystem**, NOT in the database.

```
apps/<app_name>/<app_name>/<module>/page/<page_name>/
├── <page_name>.json     # Page metadata (stored in DB + exported to file)
├── <page_name>.js       # JavaScript (FILESYSTEM ONLY)
├── <page_name>.css      # Styles (FILESYSTEM ONLY)
└── <page_name>.html     # HTML template (FILESYSTEM ONLY)
```

**Key behaviors:**
- When you call `frappe.db.set_value('Page', 'my-page', 'script', js_code)`, it does NOT create a DB column — the `script` field is a **virtual property** loaded from the `.js` file.
- The Page API's `as_dict()` method includes `script`, `style`, `content` by reading from the filesystem — but you CANNOT write to them via the API unless `developer_mode` is ON and the page belongs to a custom app.
- Without `developer_mode`, the API will accept the POST/PUT silently but the values won't persist — the page will be **blank**.

### Source Code Proof

From `frappe/core/doctype/page/page.py`:
```python
def as_dict(self, **kwargs):
    d = super().as_dict(**kwargs)
    for key in ("script", "style", "content"):
        d[key] = self.get(key)  # Reads from filesystem
    return d

def on_trash(self):
    if not frappe.conf.developer_mode and not frappe.flags.in_migrate:
        frappe.throw(_("Deletion of this document is only permitted in developer mode."))
```

### Rule

**NEVER attempt to deploy a Page's JS/CSS via API unless you have confirmed `developer_mode = 1` on the target instance.** If developer_mode is OFF, use Web Page or Custom HTML Block instead.

---

## 2. The developer_mode Gate {#2-the-developer_mode-gate}

### What developer_mode Controls

| Action | developer_mode ON | developer_mode OFF |
|--------|:-:|:-:|
| Create Page with JS/CSS that persists | ✅ | âŒ Blank page |
| Create non-custom DocType | ✅ | âŒ |
| Delete standard Pages | ✅ | âŒ |
| Export module JSON | ✅ | âŒ |
| Create Web Page via API | ✅ | ✅ |
| Create Custom HTML Block via API | ✅ | ✅ |
| Create Workspace via API | ✅ | ✅ |
| Create Server Script via API | ✅ | ✅ |
| `frappe.call()` works in Desk context | ✅ | ✅ |

### How to Check

```python
# Via API
resp = requests.get(f"{BASE}/api/method/frappe.client.get_value",
    headers=HDR,
    params={"doctype": "System Settings", "fieldname": "developer_mode"})
# OR
resp = requests.get(f"{BASE}/api/method/frappe.get_conf",
    headers=HDR)
# Check resp.json()['message'].get('developer_mode')
```

### CRITICAL RULE

**Always ask the user about developer_mode status BEFORE choosing a deployment strategy.** Don't assume it's ON. Don't attempt Page deployment and then scramble to Web Page when it fails.

---

## 3. Four Deployment Targets Compared {#3-four-deployment-targets}

| Feature | **Page** (Desk) | **Web Page** (Portal) | **Custom HTML Block** (Workspace) | **Client Script** |
|---------|:-:|:-:|:-:|:-:|
| Requires developer_mode | ✅ YES | âŒ No | âŒ No | âŒ No |
| Runs inside Frappe Desk | ✅ Full desk context | âŒ Portal context | ✅ Inside workspace | ✅ On form/list |
| Has jQuery | ✅ | âŒ Only if desk bundle loaded | ✅ | ✅ |
| Has `frappe.call()` | ✅ | âŒ Not natively | ✅ | ✅ |
| Has `frappe.Chart` | ✅ | âŒ Not natively | ✅ | ✅ |
| Has Frappe sidebar | ✅ | âŒ | ✅ Workspace sidebar | ✅ |
| Supports inline `<script>` | ✅ | ⚠️ Depends on version | ⚠️ Depends on theme | N/A |
| URL pattern | `/app/<page-name>` | `/<route>` | `/app/<workspace-name>` | N/A |
| Max content size | Unlimited (filesystem) | ~5MB (DB field) | ~2MB (DB field) | ~64KB |
| Deployment via API (no SSH) | âŒ Without dev mode | ✅ | ✅ | ✅ |

### When to Use Each

- **Page**: Best option IF developer_mode is ON. Full desk context, all JS libraries available, proper URL routing.
- **Web Page**: Fallback when developer_mode is OFF. But you lose desk context (no sidebar, no frappe.Chart unless you load desk.bundle).
- **Custom HTML Block**: Best for embedding content inside an existing Workspace. But limited by workspace theme and block rendering logic.
- **Client Script**: Best for small UI augmentations on existing forms/lists. Not suitable for full dashboards.

---

## 4. JS Bundle Availability by Context {#4-js-bundle-availability}

### âŒ WRONG ASSUMPTION (Claude kept making this error)

> "Web Pages have jQuery and frappe.Chart available since they're served from the same Frappe instance."

### ✅ REALITY

Frappe loads DIFFERENT JavaScript bundles depending on the page context:

| Bundle | Desk Pages (`/app/*`) | Web Pages (`/route`) | What It Contains |
|--------|:-:|:-:|---|
| `libs.bundle.js` | ✅ | ✅ | jQuery, Moment.js, Socket.io client |
| `desk.bundle.js` | ✅ | âŒ | `frappe.call()`, `frappe.Chart`, `frappe.ui.*`, full Frappe desk framework |
| `frappe-web.bundle.js` | âŒ | ✅ | Minimal web context (no Chart, no desk UI) |
| `report.bundle.js` | Only on reports | âŒ | Report-specific frappe UI |
| `form.bundle.js` | Only on forms | âŒ | Form-specific frappe UI |

### Consequence

If you deploy a dashboard to a **Web Page** and your code uses `frappe.Chart`, `frappe.call()`, or `frappe.ui.make_app_page()`, **it will fail silently or throw errors**.

### Workaround for Web Pages

You CAN manually load `desk.bundle.js` from the same origin:

```html
<script src="/assets/frappe/dist/js/libs.bundle.HASH.js"></script>
<script src="/assets/frappe/dist/js/desk.bundle.HASH.js"></script>
```

But you MUST:
1. Discover the correct bundle hash first (see §10)
2. Poll-wait for dependencies before initializing your code
3. Accept that this loads ~2MB of extra JS and may cause conflicts

### Better Workaround

If you need charts on a Web Page without loading desk.bundle, use:
- **Chart.js** (from same-origin if CDN is blocked)
- **Apache ECharts** (lighter than desk.bundle)
- Inline SVG generation for simple charts
- `frappe-charts` standalone IIFE from same-origin upload

---

## 5. Workspace Content JSON Structure {#5-workspace-content-json}

### âŒ WRONG ASSUMPTION (Claude kept making this error)

> "I'll set workspace content to `[{"type": "custom_block", "data": {"custom_block_name": "My Block", "col": 12}}]`"

### ✅ REALITY

Frappe v15/v16 workspace `content` field stores a JSON array of blocks. The exact structure varies by Frappe version and any custom workspace themes (like SVA). The **correct minimal structure** for a standard Frappe v15+ workspace block is:

```json
[
  {
    "id": "unique-random-id-1",
    "type": "custom_block",
    "data": {
      "custom_block_name": "My Custom HTML Block",
      "col": 12
    }
  }
]
```

**Critical fields that Claude kept missing:**
- `id` — **REQUIRED**. Every block needs a unique ID string. Without it, the workspace rendering may fail silently.
- `type` — Must match exactly: `"header"`, `"paragraph"`, `"chart"`, `"shortcut"`, `"card"`, `"custom_block"`, `"number_card"`, `"onboarding"`, `"spacer"`

### Working Block Types

```json
// Header block
{"id": "h1", "type": "header", "data": {"text": "Dashboard", "col": 12}}

// Shortcut block
{"id": "s1", "type": "shortcut", "data": {"shortcut_name": "My Shortcut", "col": 4}}

// Chart block
{"id": "c1", "type": "chart", "data": {"chart_name": "My Chart", "col": 6}}

// Number card block
{"id": "n1", "type": "number_card", "data": {"number_card_name": "My Card", "col": 3}}

// Custom HTML Block
{"id": "b1", "type": "custom_block", "data": {"custom_block_name": "My Block", "col": 12}}

// Spacer
{"id": "sp1", "type": "spacer", "data": {"col": 12}}
```

### How to Discover the Correct Structure

**ALWAYS** examine an existing working workspace on the same instance before creating new content:

```python
# Get a working workspace's content
resp = requests.get(f"{BASE}/api/resource/Workspace/{working_ws_name}", headers=HDR)
content = resp.json()['data']['content']
blocks = json.loads(content)
# Study the block structure before creating your own
```

---


## 6. Custom HTML Block — Correct Usage {#6-custom-html-block}

### What It Is

A `Custom HTML Block` is a standalone doctype that stores HTML, CSS, and JavaScript embedded inside a Workspace. Frappe renders it inside a **Web Component with Shadow DOM** via `frappe.create_shadow_element()`.

### Fields — THREE SEPARATE FIELDS (CRITICAL)

| Field | Type | What goes here |
|-------|------|----------------|
| `name` | Data | Unique identifier |
| `html` | Code | **Structure only** — pure HTML markup, NO `<style>` or `<script>` tags |
| `style` | Code | **All CSS** — never put in `html` field |
| `script` | Code | **All JavaScript** — never put in `html` field |
| `private` | Check | If checked, only visible to specific roles |

### ❌ WRONG — Everything jammed in html field

```python
# WRONG. Frappe calls frappe.dom.remove_script_and_style(html) before rendering.
# Both <style> and <script> are SILENTLY STRIPPED.
block_doc = {
    "html": "<style>.foo{color:red}</style><div id='root'></div><script>init();</script>",
}
```

### ✅ CORRECT — Three separate fields

```python
block_doc = {
    "doctype": "Custom HTML Block",
    "name": "My Dashboard",
    "html": "<div id='my-root'><p id='msg'>Loading...</p></div>",
    "style": ":host { display: block; } #my-root { padding: 20px; }",
    "script": "root_element.querySelector('#msg').textContent = 'Loaded!';",
    "private": 0
}
requests.put(f"{BASE}/api/resource/Custom HTML Block/My Dashboard",
    headers=HDR, json=block_doc)
```

### Why: How Frappe Renders CHBs (verified from desk.bundle source)

```javascript
// Frappe's create_shadow_element does:
div.innerHTML = frappe.dom.remove_script_and_style(html); // strips style+script from html
shadowRoot.appendChild(styleEl);   // styleEl.textContent = style field
scriptEl.textContent = `
  (function() {
    let root_element = document.querySelector('${cname}').shadowRoot;
    ${script}   // <-- your script field, with root_element injected
  })();
`;
shadowRoot.appendChild(scriptEl);
```

**Consequences:**
- `<style>` and `<script>` in the `html` field are permanently stripped before render
- Your script runs inside Shadow DOM — `document.getElementById()` **will not find elements**
- `root_element` is **auto-injected** into your script scope

### DOM Querying in Scripts

```javascript
// ❌ WRONG — crosses shadow DOM boundary, always returns null
var el = document.getElementById('my-root');

// ✅ CORRECT — root_element is the shadowRoot, auto-injected by Frappe
var el = root_element.querySelector('#my-root');
root_element.querySelectorAll('.my-card').forEach(function(c) { ... });
```

### CSS Scope in Style Field

```css
/* :host targets the web component element itself */
:host { display: block; width: 100%; }
* { box-sizing: border-box; font-family: Inter, sans-serif; }
/* No scoping prefixes needed — shadow DOM isolates styles */
```

### frappe.Chart in Shadow DOM

```javascript
// Pass the DOM element, not a CSS selector string
var container = root_element.querySelector('#my-chart');
new frappe.Chart(container, {
    type: 'donut',
    data: { labels: ['A','B'], datasets: [{values: [30, 70]}] },
    height: 200
});
```

### ⚠️ Other Gotchas

1. **`frappe.call()` works normally** from inside shadow DOM scripts
2. **`frappe.Chart` works** — pass DOM element directly, not a selector
3. **DOMContentLoaded won't fire** — DOM is already ready; execute directly
4. **Custom workspace themes** may have their own rendering — verify by reading a working CHB on the same instance first


## 7. Web Page — Limitations and Workarounds {#7-web-page}

### What It Is

A `Web Page` creates a publicly routable page at `/<route>`. It's part of Frappe's portal/website system, NOT the Desk.

### Key Fields

| Field | Type | Notes |
|-------|------|-------|
| `name` | Data | Internal name |
| `title` | Data | Page title |
| `route` | Data | URL route (e.g., `my-dashboard` → `/my-dashboard`) |
| `content_type` | Select | "Rich Text", "Markdown", "HTML" |
| `main_section` | Code | **v14**: Main HTML content field |
| `main_section_html` | Code | **v15+**: Main HTML content field when content_type is HTML |
| `published` | Check | Must be 1 to be accessible |
| `full_width` | Check | Set to 1 to remove page margins |
| `show_title` | Check | Set to 0 to hide the page title |

### ⚠️ Field Name Confusion (Claude made this error)

**v14** uses `main_section` for the HTML content.
**v15+** may use `main_section_html` OR `main_section` depending on `content_type`.

**Always check by reading the doctype schema first:**
```python
resp = requests.get(f"{BASE}/api/doctype/Web Page", headers=HDR)
fields = resp.json()['data']['fields']
html_fields = [f for f in fields if 'html' in f['fieldname'].lower() or 'section' in f['fieldname'].lower()]
```

### What's NOT Available in Web Page Context

- `frappe.call()` (no desk.bundle)
- `frappe.Chart` (no desk.bundle)
- `frappe.ui.*` (no desk.bundle)
- Frappe Desk sidebar/navbar
- User avatar/session info (must use cookie or API)

### Minimal frappe.call Shim for Web Pages

If you MUST use `frappe.call()` patterns in a Web Page:

```javascript
// Minimal shim — NOT full frappe.call
if (typeof frappe === 'undefined') window.frappe = {};
if (!frappe.call) {
    frappe.call = function(opts) {
        return fetch('/api/method/' + opts.method, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Frappe-CSRF-Token': frappe.csrf_token || ''
            },
            credentials: 'include',
            body: JSON.stringify(opts.args || {})
        })
        .then(r => r.json())
        .then(d => { if (opts.callback) opts.callback(d); return d; })
        .catch(e => { if (opts.error) opts.error(e); });
    };
}
```

**Note:** This shim does NOT handle all `frappe.call` options (async, freeze, etc.). Keep it minimal.

---

## 8. CDN and External Script Restrictions {#8-cdn-restrictions}

### âŒ WRONG ASSUMPTION (Claude kept making this error)

> "I'll load frappe-charts from jsdelivr CDN."

### ✅ REALITY

Many browsers (especially Safari, Brave, Firefox with Enhanced Tracking Protection) **block third-party scripts** from CDN domains like:
- `cdn.jsdelivr.net`
- `cdnjs.cloudflare.com`
- `unpkg.com`

This is NOT a Frappe issue — it's browser Tracking Prevention. The scripts are silently blocked with no console error in some browsers.

### Rules

1. **NEVER rely on external CDNs** for critical dashboard functionality.
2. **Always use same-origin scripts** — load from `/assets/` on the same Frappe instance.
3. If you need a library that's not in Frappe's bundles, either:
   - Upload it as a File attachment and reference `/files/library-name.min.js`
   - Inline the library code directly in the HTML (increases payload but guarantees loading)
   - Use the copy bundled inside `desk.bundle.js` (e.g., frappe-charts is inside desk.bundle)

### Finding Same-Origin Equivalents

```python
# Check what's available in Frappe's asset directory
resp = requests.get(f"{BASE}/assets/frappe/dist/js/", headers=HDR)
# Parse the directory listing to find available bundles

# Check if a specific library is inside a bundle
resp = requests.get(f"{BASE}/assets/frappe/dist/js/libs.bundle.HASH.js", headers=HDR)
has_chart = 'frappe.Chart' in resp.text  # Usually NO — it's in desk.bundle
```

---

## 9. Sidebar and Navigation in v16 {#9-sidebar-and-navigation}

### v16 Changes

- The **Desk sidebar** is now organized by **Apps** with grouped workspaces
- Apps have dedicated sidebars with logo
- Full-width mode is the **default** (not toggled manually)
- Document detail sidebar moved to the **right side**

### âŒ WRONG APPROACH (Claude kept making this error)

> "I'll create a custom sidebar inside my dashboard HTML and hide the Frappe sidebar."

### ✅ CORRECT APPROACH

1. **Use Frappe's native Workspace sidebar** — don't fight it
2. Create a **Workspace** for your dashboard (appears in the sidebar automatically)
3. Use **horizontal top tabs** within the workspace content area for sub-navigation
4. If embedding a full-page dashboard, the dashboard should NOT have its own sidebar

### â—ï¸ Workspace Sidebar Context Loss on `frappe.new_doc()`

When a Client Script calls `frappe.new_doc('Other DocType', {...})`, the browser navigates to `/app/other-doctype/new`. If "Other DocType" is NOT linked in the current workspace, the sidebar switches from the workspace sidebar to a flat module sidebar. This is a common gotcha when building cross-DocType conversion flows (e.g., Lead → Candidate).

**Symptoms:** User clicks "Convert to Candidate" on a lead form → the Candidate Registration form opens → but the left sidebar changes from the workspace's People > Leads, Candidates, etc. to a generic module sidebar.

**Root cause:** Frappe resolves the sidebar from the workspace that "owns" the target DocType. If the target DocType isn't linked in the current workspace, Frappe falls back to the module sidebar.

**Fixes (in order of preference):**
1. **Ensure both DocTypes are linked in the same workspace** — add a shortcut block for the target DocType in the workspace content JSON.
2. **Open in new tab** — use `window.open('/app/other-doctype/new?field=value', '_blank')` instead of `frappe.new_doc()`. Preserves the original workspace context in the parent tab.
3. **Use `frappe.route_options` + `frappe.set_route()`** — navigate via the workspace-aware route: `frappe.route_options = {field: value}; frappe.set_route('app', 'other-doctype', 'new');`

### Adding a Dashboard to the Sidebar

```python
# Create a workspace that appears in the sidebar
ws_doc = {
    "doctype": "Workspace",
    "name": "my-dashboard",
    "title": "My Dashboard",
    "label": "My Dashboard",
    "module": "Custom",  # Or your app's module
    "icon": "chart-bar",
    "is_hidden": 0,
    "public": 1,
    "content": json.dumps([
        {
            "id": "block-1",
            "type": "custom_block",
            "data": {
                "custom_block_name": "My Dashboard Block",
                "col": 12
            }
        }
    ])
}
requests.post(f"{BASE}/api/resource/Workspace", headers=HDR, json=ws_doc)
```

---

## 10. Bundle Hash Discovery {#10-bundle-hash-discovery}

### The Problem

Frappe's JS bundles have content-based hashes in filenames:
- `libs.bundle.TIV7ZGVY.js`
- `desk.bundle.QTB7ATHN.js`

These hashes **change with every build**. Hardcoding them is fragile.

### Discovery Methods

```python
# Method 1: Parse the desk page HTML for script tags
resp = requests.get(f"{BASE}/app/home", headers=HDR)
import re
scripts = re.findall(r'/assets/frappe/dist/js/(\w+\.bundle\.\w+\.js)', resp.text)
bundles = {s.split('.')[0]: s for s in scripts}
# bundles = {'libs': 'libs.bundle.TIV7ZGVY.js', 'desk': 'desk.bundle.QTB7ATHN.js', ...}

# Method 2: List the assets directory
resp = requests.get(f"{BASE}/assets/frappe/dist/js/", headers=HDR)
# Parse directory listing

# Method 3: Use the build manifest (if available)
resp = requests.get(f"{BASE}/assets/frappe/dist/build.json", headers=HDR)
```

### Rule

**NEVER hardcode bundle hashes.** Always discover them dynamically from the target instance.

---

## 11. iframe Embedding Pitfalls {#11-iframe-embedding}

### Common Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| Double scrollbar | iframe height too small | Use `height: 100vh` or dynamically resize |
| Top whitespace | Frappe page wrappers add padding | Negative margin or CSS override inside iframe |
| No Frappe sidebar | Web Page doesn't have desk chrome | Expected — use workspace for sidebar |
| Login redirect | Session cookie not passed | Use `credentials: 'include'` in fetch |
| Cross-origin errors | Different subdomain | Ensure iframe src is same-origin |

### If You Must Use iframe

```html
<!-- In Custom HTML Block -->
<div style="margin: -20px -30px; overflow: hidden;">
  <iframe 
    src="/my-web-page-route" 
    width="100%" 
    height="calc(100vh - 60px)" 
    frameborder="0" 
    style="border: none; display: block;">
  </iframe>
</div>
<script>
// Strip workspace padding
var el = document.currentScript.parentElement;
while (el) {
    if (el.classList && (
        el.classList.contains('widget-body') || 
        el.classList.contains('custom-block-container') ||
        el.classList.contains('workspace-block-container')
    )) {
        el.style.padding = '0';
        el.style.margin = '0';
    }
    el = el.parentElement;
}
</script>
```

### Better Alternative

**Don't use iframes.** Put your dashboard code directly inside the Custom HTML Block if the content is under ~2MB. This gives you:
- Full desk context (jQuery, frappe.call, frappe.Chart)
- No cross-context issues
- No double scrollbar
- Proper workspace integration

---

## 12. Custom Workspace Themes (e.g., SVA) {#12-custom-workspace-themes}

### The Problem Claude Hit

The mGrant instance uses an **SVA workspace theme** that overrides Frappe's standard workspace rendering. This theme:
- Has its OWN Custom HTML Block rendering logic
- Expects blocks to be registered in an `SVAWorkspace Configuration` doctype
- Silently ignores blocks that aren't registered in its configuration

### Rule

**Before deploying Custom HTML Blocks, always check if the instance has a custom workspace theme:**

```python
# Check for custom workspace themes
resp = requests.get(f"{BASE}/api/method/frappe.client.get_list",
    headers=HDR,
    params={
        'doctype': 'Custom HTML Block',
        'fields': '["name"]',
        'limit_page_length': 20
    })
existing_blocks = resp.json()['message']

# Check which blocks are actually rendered in working workspaces
resp2 = requests.get(f"{BASE}/api/resource/Workspace/{working_workspace_name}", headers=HDR)
content = json.loads(resp2.json()['data']['content'])
working_block_names = [b['data']['custom_block_name'] for b in content if b.get('type') == 'custom_block']

# Check if there's a custom workspace configuration doctype
for config_dt in ['SVAWorkspace Configuration', 'Workspace Configuration', 'Dashboard Configuration']:
    resp3 = requests.get(f"{BASE}/api/resource/{config_dt}", headers=HDR)
    if resp3.status_code == 200:
        print(f"Found custom config: {config_dt}")
```

### If Custom Theme Exists

Study how existing dashboards are deployed on that instance and replicate the exact pattern — don't try to invent a new deployment approach.

---

## 13. Server Script Limitations {#13-server-script-limitations}

### âŒ WRONG ASSUMPTION (Claude made this error)

> "I'll use a Server Script with `frappe.db.set_value('Page', 'my-page', 'script', js_code)` to deploy JS."

### ✅ REALITY

- The `script` field of a Page doctype **has NO database column** — it's a virtual property
- `frappe.db.set_value` writes to DB columns, so it will fail silently or error
- Server Scripts themselves run in a **restricted sandbox** with limited imports

### What Server Scripts CAN Do

- Create/update documents (doctypes that store fields in DB)
- Execute `frappe.call()` to whitelisted methods
- Read data with `frappe.db.get_value()`, `frappe.db.get_list()`
- Create Web Pages, Custom HTML Blocks, Workspaces (since their content fields ARE in the DB)

### What Server Scripts CANNOT Do

- Write files to the filesystem
- Import arbitrary Python modules
- Set virtual properties (like Page's `script` field)
- Execute shell commands

---

## 14. API Field Names — What's Real vs Virtual {#14-api-field-names}

### The Trap

When you fetch a Page via API, the response includes `script`, `style`, and `content`:

```json
{
  "data": {
    "name": "my-page",
    "title": "My Page",
    "script": "frappe.pages['my-page'].on_page_load = ...",
    "style": ".my-page { ... }",
    "content": "<div>...</div>"
  }
}
```

This makes it LOOK like these are database fields you can write to. They're NOT — they're loaded from the filesystem by `as_dict()`.

### How to Tell

```python
# Check actual DB columns for a doctype
resp = requests.get(f"{BASE}/api/doctype/Page", headers=HDR)
fields = resp.json()['data']['fields']
db_fields = [f['fieldname'] for f in fields if f.get('fieldtype') not in ['Section Break', 'Column Break', 'HTML']]
# 'script' and 'style' are NOT in this list for Page doctype
```

### Known Virtual Fields

| Doctype | Virtual Fields (NOT in DB) |
|---------|---------------------------|
| Page | `script`, `style`, `content` |
| Report | `script`, `report_script` (filesystem-based for standard reports) |

### Known Real DB Fields

| Doctype | Content Fields (IN DB) |
|---------|----------------------|
| Web Page | `main_section`, `main_section_html` |
| Custom HTML Block | `html`, `script`, `style` |
| Workspace | `content` (JSON string) |
| Server Script | `script` |
| Client Script | `script` |

---

## 15. Decision Tree — Which Deployment Path? {#15-decision-tree}

```
START: Need to deploy a custom dashboard to Frappe
│
├─ Q1: Do you have developer_mode ON?
│  ├─ YES → Use Page doctype (best option)
│  │        ├─ Full desk context (jQuery, frappe.Chart, frappe.call)
│  │        ├─ Proper URL: /app/my-dashboard
│  │        ├─ Deploy JS/CSS via API
│  │        └─ Add to Workspace sidebar for navigation
│  │
│  └─ NO → Continue to Q2
│
├─ Q2: Does the instance have a custom workspace theme?
│  ├─ YES → Study the existing theme's deployment pattern
│  │        ├─ Check for theme-specific configuration doctypes
│  │        ├─ Replicate how existing dashboards are deployed
│  │        └─ May need iframe embedding in Custom HTML Block
│  │
│  └─ NO or UNKNOWN → Continue to Q3
│
├─ Q3: Does your dashboard need frappe.Chart or frappe.call?
│  ├─ YES → Use Custom HTML Block in Workspace
│  │        ├─ Runs inside Desk context (all JS available)
│  │        ├─ Create block → Add to workspace content JSON
│  │        ├─ Appears in sidebar via workspace
│  │        └─ ⚠️ Content limit ~2MB
│  │
│  └─ NO (plain HTML/CSS or uses its own chart lib) →
│     Use Web Page
│     ├─ No desk context needed
│     ├─ Route: /my-dashboard
│     ├─ full_width: 1, show_title: 0
│     └─ Optionally embed in workspace via iframe
│
├─ Q4: Are you enhancing an EXISTING form or list view (not building a new page)?
│  ├─ YES → Use Client Script (see §18)
│  │        ├─ Form scripts: frappe.ui.form.on() for status banners, journey steps, CTAs
│  │        ├─ List scripts: frappe.listview_settings[] for formatters, row styling
│  │        ├─ Deploy via API: POST to /api/resource/Client Script
│  │        └─ ⚠️ Aggressively cached — see §19 for invalidation
│  │
│  └─ NO → Continue to FALLBACK
│
└─ FALLBACK: If nothing works →
   ├─ Ask user to enable developer_mode (even temporarily)
   ├─ Deploy Page, then disable developer_mode
   └─ The Page will continue to work after disabling
```

---

## 16. Pre-Flight Checklist {#16-pre-flight-checklist}

Before deploying ANY dashboard to a Frappe instance, verify ALL of these:

### Instance Discovery

- [ ] What Frappe version? (`/api/method/frappe.utils.change_log.get_versions`)
- [ ] Is `developer_mode` ON? (check site_config or System Settings)
- [ ] Is there a custom workspace theme? (check installed apps, existing workspaces)
- [ ] What JS bundles are available? (parse `/app/home` for script tags)
- [ ] What existing Custom HTML Blocks exist? (list them via API)
- [ ] What's the workspace content structure of a WORKING workspace?

### Deployment Strategy

- [ ] Chosen deployment target (Page / Web Page / Custom HTML Block)?
- [ ] Reason for choosing this target documented?
- [ ] All JS dependencies available in chosen context?
- [ ] No hardcoded bundle hashes?
- [ ] No external CDN dependencies?
- [ ] Content size within limits?

### Testing

- [ ] Read back the deployed content via API to verify it persisted?
- [ ] Tested in-browser to confirm rendering?
- [ ] Checked browser console for errors?
- [ ] Tested with the user's actual browser (CDN blocking varies)?

---

## 17. Working Code Templates {#17-working-code-templates}

### Template A: Custom HTML Block + Workspace (developer_mode OFF)

This is the **safest deployment path** when developer_mode is OFF.

```python
import requests, json, uuid

BASE = "https://your-site.example.com"
HDR = {"Authorization": "token API_KEY:API_SECRET"}

# Step 1: Build dashboard HTML (with inline CSS and JS)
dashboard_html = """
<style>
  .dash-root { font-family: Inter, sans-serif; padding: 16px; }
  /* ALL CSS INLINE */
</style>
<div class="dash-root" id="my-dashboard">
  <div style="text-align:center;padding:40px;color:#666;">Loading...</div>
</div>
<script>
(function() {
    // frappe.call IS available here (we're in desk context)
    frappe.call({
        method: 'frappe.client.get_list',
        args: { doctype: 'Your Doctype', fields: ['name', 'title'], limit_page_length: 20 },
        callback: function(r) {
            var root = document.getElementById('my-dashboard');
            if (r.message) {
                root.innerHTML = '<h3>' + r.message.length + ' records found</h3>';
                // Build your dashboard UI here
            }
        }
    });
})();
</script>
"""

# Step 1: Separate html, style, script into three fields
dashboard_html = """<div id="my-root"><p id="msg">Loading...</p></div>"""

dashboard_style = """
:host { display: block; width: 100%; }
* { box-sizing: border-box; font-family: Inter, sans-serif; }
#my-root { padding: 20px; background: #F9FAFB; }
"""

dashboard_script = """
// root_element is auto-injected by Frappe (it is the Shadow DOM root)
// NEVER use document.getElementById() — use root_element.querySelector()
frappe.call({
    method: 'frappe.client.get_list',
    args: { doctype: 'Candidate', fields: ['name'], limit_page_length: 5 },
    callback: function(r) {
        var el = root_element.querySelector('#msg');
        if (el) el.textContent = 'Found: ' + (r.message || []).length + ' records';
    }
});
"""

# Step 2: Create/Update Custom HTML Block with THREE separate fields
block_name = "My Dashboard"
resp = requests.put(f"{BASE}/api/resource/Custom HTML Block/{block_name}",
    headers=HDR,
    json={
        "html": dashboard_html,
        "style": dashboard_style,
        "script": dashboard_script,
    })
# Use POST if it doesn't exist yet:
# resp = requests.post(f"{BASE}/api/resource/Custom HTML Block",
#     headers=HDR,
#     json={"doctype":"Custom HTML Block","name":block_name,
#           "html":dashboard_html,"style":dashboard_style,"script":dashboard_script,"private":0})
print(f"Block: {resp.status_code}")

# Step 3: Verify all three fields stored
verify = requests.get(f"{BASE}/api/resource/Custom HTML Block/{block_name}", headers=HDR)
d = verify.json()['data']
assert d.get('script'), "WARNING: script field is empty!"
assert d.get('style'),  "WARNING: style field is empty!"
print(f"html={len(d['html'])} style={len(d['style'])} script={len(d['script'])} chars")

# Step 4: Create/Update Workspace — MUST sync BOTH content JSON and custom_blocks child table
ws_name = "my-dashboard"
ws_content = json.dumps([
    {"id": "ws-h1", "type": "header", "data": {"text": "My Dashboard", "level": 3, "col": 12}},
    {"id": "ws-cb1", "type": "custom_block", "data": {"custom_block_name": block_name, "col": 12}}
])
cb_row = {"custom_block_name": block_name, "label": block_name,
          "parentfield": "custom_blocks", "parenttype": "Workspace",
          "doctype": "Workspace Custom Block"}

resp2 = requests.post(f"{BASE}/api/resource/Workspace",
    headers=HDR,
    json={
        "doctype": "Workspace", "name": ws_name, "title": "My Dashboard",
        "label": "My Dashboard", "module": "Custom", "icon": "chart-bar",
        "is_hidden": 0, "public": 1,
        "content": ws_content,
        "custom_blocks": [cb_row]   # ← REQUIRED — content JSON alone is not enough
    })
print(f"Workspace: {resp2.status_code}")

# Step 5: Verify workspace content and child table are in sync
rv = requests.get(f"{BASE}/api/resource/Workspace/{ws_name}", headers=HDR)
d2 = rv.json()['data']
content_chbs = [b['data']['custom_block_name'] for b in json.loads(d2['content']) if b['type']=='custom_block']
table_chbs   = [c['custom_block_name'] for c in d2.get('custom_blocks',[])]
print(f"Content CHBs: {content_chbs} | Table CHBs: {table_chbs}")
assert set(content_chbs) == set(table_chbs), "OUT OF SYNC — blank page will result!"
print(f"Access at: {BASE}/app/{ws_name}")
```

### Template B: Page Deployment (developer_mode ON)

```python
import requests

BASE = "https://your-site.example.com"
HDR = {"Authorization": "token API_KEY:API_SECRET", "Content-Type": "application/json"}

page_name = "my-dashboard"
page_title = "My Dashboard"

# Step 1: Create/verify Page
resp = requests.post(f"{BASE}/api/resource/Page",
    headers=HDR,
    json={
        "doctype": "Page",
        "page_name": page_name,
        "title": page_title,
        "module": "Custom",
        "standard": "No"
    })

# Step 2: Set JS and CSS (only works with developer_mode ON)
js_code = f"""
frappe.pages['{page_name}'].on_page_load = function(wrapper) {{
    var page = frappe.ui.make_app_page({{
        parent: wrapper,
        title: '{page_title}',
        single_column: true
    }});
    
    // frappe.Chart, frappe.call, jQuery all available here
    $(page.body).html('<h2>Dashboard Loading...</h2>');
    
    frappe.call({{
        method: 'frappe.client.get_list',
        args: {{ doctype: 'Your Doctype', fields: ['name'], limit_page_length: 0 }},
        callback: function(r) {{
            $(page.body).html('<h2>' + r.message.length + ' records</h2>');
        }}
    }});
}};
"""

css_code = """
/* Your dashboard styles */
"""

resp2 = requests.put(f"{BASE}/api/resource/Page/{page_name}",
    headers=HDR,
    json={"script": js_code, "style": css_code})
print(f"Deploy: {resp2.status_code}")

# Step 3: Verify JS persisted
verify = requests.get(f"{BASE}/api/resource/Page/{page_name}", headers=HDR)
stored_script = verify.json()['data'].get('script', '')
if len(stored_script) < 10:
    print("⚠️ WARNING: Script did not persist — developer_mode may be OFF!")
else:
    print(f"✅ Script persisted ({len(stored_script)} chars)")
    print(f"Access at: {BASE}/app/{page_name}")
```

### Template C: Web Page with frappe.call Shim (developer_mode OFF, no desk context needed)

```python
import requests

BASE = "https://your-site.example.com"
HDR = {"Authorization": "token API_KEY:API_SECRET"}

html_content = """
<style>
  body { margin: 0; font-family: Inter, sans-serif; background: #f8fafc; }
  .dash { max-width: 1200px; margin: 0 auto; padding: 24px; }
  .web-footer, footer, .page-header-wrapper { display: none !important; }
</style>
<div class="dash" id="app-root">
  <p>Loading dashboard...</p>
</div>
<script>
// Minimal frappe.call shim for web context
if (typeof frappe === 'undefined') window.frappe = {};
if (!frappe.call) {
    frappe.call = function(opts) {
        return fetch('/api/method/' + opts.method, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            credentials: 'include',
            body: JSON.stringify(opts.args || {})
        })
        .then(function(r) { return r.json(); })
        .then(function(d) { if (opts.callback) opts.callback(d); return d; })
        .catch(function(e) { console.error('API error:', e); });
    };
}

// Your dashboard code here (NO frappe.Chart — use Chart.js or inline SVG)
frappe.call({
    method: 'frappe.client.get_list',
    args: { doctype: 'Your Doctype', fields: ['name', 'title'], limit_page_length: 20 },
    callback: function(r) {
        var root = document.getElementById('app-root');
        root.innerHTML = '<h2>' + (r.message ? r.message.length : 0) + ' records</h2>';
    }
});
</script>
"""

# Create Web Page
resp = requests.post(f"{BASE}/api/resource/Web Page",
    headers=HDR,
    json={
        "doctype": "Web Page",
        "name": "my-dashboard-view",
        "title": "My Dashboard",
        "route": "my-dashboard-view",
        "content_type": "HTML",
        "main_section_html": html_content,  # v15+ field name
        "published": 1,
        "full_width": 1,
        "show_title": 0
    })
print(f"Web Page: {resp.status_code}")
print(f"Access at: {BASE}/my-dashboard-view")
```

---

## 18. Client Script Deployment — Form and List View {#18-client-script-deployment}

Client Scripts are the correct deployment target for **enhancing existing forms and list views** without building full dashboards. They run in Desk context (jQuery, `frappe.call`, full DOM access) and deploy via API without `developer_mode`.

### Deployment via API

```python
# Create a Form Client Script
resp = requests.post(f"{BASE}/api/resource/Client Script",
    headers=HDR,
    json={
        "doctype": "Client Script",
        "name": "My DocType - Form Enhancement",
        "dt": "My DocType",              # Target DocType
        "script_type": "Client",
        "view": "Form",                  # "Form" or "List"
        "script": js_code,
        "enabled": 1
    })

# Update an existing Client Script
resp = requests.put(f"{BASE}/api/resource/Client Script/My DocType - Form Enhancement",
    headers=HDR,
    json={"script": updated_js_code})
```

### Form Scripts — `frappe.ui.form.on()`

Form scripts fire on lifecycle events: `refresh`, `onload`, `validate`, `before_save`, plus per-field triggers.

**Key patterns learned from production:**

#### Pattern 1: HTML Field as Render Container

Add an HTML field to the DocType (via API or Form Builder), then populate it from the `refresh` handler:

```javascript
frappe.ui.form.on('My DocType', {
    refresh: function(frm) {
        var wrapper = frm.fields_dict.my_html_field;
        if (wrapper) {
            $(wrapper.wrapper).html('<div>Dynamic content here</div>');
        }
    }
});
```

**â—ï¸ Layout trap:** An HTML field placed at idx 1 shares the row with adjacent fields. To make it full-width, wrap it in its own Section Break with `hide_border: 1`:

```python
# Add via API: Section Break + HTML field
requests.put(f"{BASE}/api/resource/DocType/My DocType", headers=HDR,
    json={"fields": [
        {"fieldname": "sec_journey", "fieldtype": "Section Break", "idx": 1,
         "hide_border": 1, "collapsible": 0},
        {"fieldname": "journey_html", "fieldtype": "HTML", "idx": 2},
        {"fieldname": "sec_main", "fieldtype": "Section Break", "idx": 3,
         "label": "Details"}
        # ... rest of fields with updated idx values
    ]})
```

#### Pattern 2: Status Banner Injection

Insert custom HTML before a known field wrapper, with fallback:

```javascript
var $target = frm.fields_dict.my_html_field && $(frm.fields_dict.my_html_field.wrapper);
if ($target && $target.length) {
    $('.my-banner').remove();  // Clean up previous renders
    $target.before('<div class="my-banner" style="...">Status: Active</div>');
} else {
    // Fallback: prepend to form layout
    $(frm.layout.wrapper).prepend('<div class="my-banner" style="...">Status</div>');
}
```

#### Pattern 3: Dynamic Field Descriptions as Hints

Use `frm.set_df_property('fieldname', 'description', html_string)` to inject contextual guidance below a field. Updates in real-time on field change:

```javascript
frappe.ui.form.on('My DocType', {
    my_select_field: function(frm) {
        var val = frm.doc.my_select_field;
        var hint = '';
        if (val === 'Option A') {
            hint = '<span style="color:#2563EB;font-size:11px">&rarr; Routes to <b>Pathway X</b></span>';
        }
        frm.set_df_property('my_select_field', 'description', hint);
    }
});
```

#### Pattern 4: Conditional Action Buttons (State Machine)

```javascript
frm.clear_custom_buttons();  // Reset on every refresh

if (frm.doc.status === 'New') {
    frm.add_custom_button(__('Mark Contacted'), function() {
        frm.set_value('status', 'Contacted');
        frm.save();
    }, __('Actions'));
}
// Only show valid transitions for current state
```

#### Pattern 5: Cross-DocType Conversion with Pre-fill

```javascript
function do_convert() {
    var frm = cur_frm;
    frappe.confirm('Create a new Registration from this lead?', function() {
        frappe.new_doc('Target DocType', {
            full_name: frm.doc.full_name,
            source_reference: frm.doc.name
        });
    });
}
window.do_convert = do_convert;  // Required for onclick in injected HTML
```

**â—ï¸ `window.fn_name` is required** — functions defined inside a Client Script are not accessible from inline `onclick` handlers in injected HTML. Expose them via `window`.

**â—ï¸ Sidebar context loss** — `frappe.new_doc()` navigates away and may switch the workspace sidebar. See §9 for fixes.

#### Pattern 6: CSS Injection (Idempotent)

```javascript
function inject_styles() {
    if (document.getElementById('my-script-styles')) return;  // Idempotent guard
    var style = document.createElement('style');
    style.id = 'my-script-styles';
    style.textContent = '@keyframes fade-in { from { opacity:0 } to { opacity:1 } }' +
        ' .my-btn:hover { background: #15803D !important; }';
    document.head.appendChild(style);
}
```

**Rule:** Always use an `id` guard to prevent duplicate style injection on multiple `refresh` calls.

#### Pattern 7: Age/Urgency Tinting on Fields

```javascript
var $ctrl = frm.fields_dict.status && $(frm.fields_dict.status.wrapper);
if ($ctrl && frm.doc.creation) {
    var days = Math.floor((new Date() - frappe.datetime.str_to_obj(frm.doc.creation)) / 86400000);
    if (days > 5) {
        $ctrl.find('.control-input-wrapper').css({'background': '#FFF1F2', 'border-radius': '6px'});
        frm.set_df_property('status', 'description',
            '<span style="color:#DC2626;font-size:11px">' + days + ' days old</span>');
    }
}
```

### List View Scripts — `frappe.listview_settings[]`

List scripts customize the DocType's list view: indicators, formatters, row decoration.

```javascript
frappe.listview_settings['My DocType'] = {

    // Extra fields loaded for each row (not visible as columns unless configured)
    add_fields: ['status', 'hub', 'category', 'assigned_to', 'creation'],

    // Status indicator dot color
    get_indicator: function(doc) {
        if (doc.status === 'Active')    return [__('Active'),    'green',  'status,=,Active'];
        if (doc.status === 'Pending')   return [__('Pending'),   'orange', 'status,=,Pending'];
        if (doc.status === 'Closed')    return [__('Closed'),    'red',    'status,=,Closed'];
        return [__(doc.status), 'grey', 'status,=,' + doc.status];
    },

    // Column-level formatters (only apply to VISIBLE columns)
    formatters: {
        category: function(val) {
            if (!val) return val;
            var colors = {
                'TypeA': {bg:'#DBEAFE', color:'#1D4ED8'},
                'TypeB': {bg:'#DCFCE7', color:'#15803D'}
            };
            var c = colors[val] || {bg:'#F3F4F6', color:'#374151'};
            return '<span style="display:inline-block;padding:1px 7px;border-radius:9999px;' +
                   'font-size:10px;font-weight:500;background:' + c.bg + ';color:' + c.color + '">' +
                   val + '</span>';
        }
    },

    // Runs once when list loads
    onload: function(listview) {
        // Inject CSS for row-level styling
        if (!document.getElementById('my-list-styles')) {
            var style = document.createElement('style');
            style.id = 'my-list-styles';
            style.textContent = '.list-row[data-status="Closed"] { opacity: 0.6; }';
            document.head.appendChild(style);
        }
    }
};
```

**â—ï¸ Column visibility trap:** `formatters` only apply to columns the user has configured as visible. Setting `in_list_view: 1` on a field via API does NOT override user-configured columns. Users must manually reset their column selection via the "..." menu in the list view header. **Document this for end users.**

### Debugging Checklist for Client Scripts

- [ ] Script `enabled` is `1`?
- [ ] `dt` matches exact DocType name (case-sensitive)?
- [ ] `view` is correct (`Form` or `List`)?
- [ ] Cleared server cache? (see §19)
- [ ] Hard-refreshed browser? (`Cmd+Shift+R` or `Ctrl+Shift+R`)
- [ ] Added `console.log()` markers to verify script loads?
- [ ] Wrapped main logic in `try/catch` to surface errors?
- [ ] Using ASCII-only characters? (Unicode →/✓ can break in some Frappe versions)
- [ ] All inline styles? (CSS classes from injected `<style>` may not apply on first render due to timing)

---

## 19. Cache Invalidation {#19-cache-invalidation}

Client Scripts and Server Scripts are aggressively cached by Frappe. After deploying or updating a script, you MUST invalidate caches.

### Server-Side Cache Clear

```python
# Clear all session caches (forces script re-evaluation on next page load)
resp = requests.post(f"{BASE}/api/method/frappe.sessions.clear",
    headers=HDR)
print(f"Cache clear: {resp.status_code}")
```

### Client-Side Cache Clear

The user must also clear their browser cache:
1. **Hard refresh**: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows/Linux)
2. **Or** run in browser console: `frappe.ui.toolbar.clear_cache()`
3. **Or** navigate to `/api/method/frappe.sessions.clear` directly in the browser

### Rule

**ALWAYS clear cache after every Client Script deployment.** The most common "my script isn't working" issue is stale cache. Include cache clearing as the final step in every deployment script:

```python
# Deploy + cache clear in one flow
requests.put(f"{BASE}/api/resource/Client Script/{script_name}",
    headers=HDR, json={"script": js_code})
requests.post(f"{BASE}/api/method/frappe.sessions.clear", headers=HDR)
print("Deployed and cache cleared. User must Cmd+Shift+R in browser.")
```

---

## Summary of Claude's Repeated Errors

| # | Error | Frequency | Root Cause |
|---|-------|-----------|------------|
| 1 | Trying to set Page `script`/`style` via API without developer_mode | 3+ times | Didn't understand filesystem storage |
| 2 | Assuming Web Pages have frappe.Chart/frappe.call | 2+ times | Didn't understand bundle loading contexts |
| 3 | Loading scripts from external CDNs (jsdelivr/cdnjs) | 2+ times | Didn't account for browser Tracking Prevention |
| 4 | Hardcoding bundle hashes (e.g., `desk.bundle.QTB7ATHN.js`) | 2+ times | Didn't know hashes change per build |
| 5 | Missing `id` field in workspace content JSON blocks | 1+ times | Didn't study working workspace structures first |
| 6 | Creating custom sidebar HTML instead of using Frappe workspace | 2+ times | Fought the framework instead of using it |
| 7 | Using `frappe.db.set_value` for virtual fields | 1+ times | Didn't verify which fields have DB columns |
| 8 | Not checking for custom workspace themes (SVA) | 1+ times | Assumed standard Frappe rendering |
| 9 | Using `DOMContentLoaded` in Custom HTML Blocks | 1+ times | Didn't know DOM was already loaded |
| 10 | iframe embedding with whitespace/scrollbar issues | 2+ times | Used negative margins instead of proper CSS |
| 11 | Using `main_section` vs `main_section_html` wrong | 1+ times | Didn't verify field name for Frappe version |
| 12 | Not verifying script tag preservation after save | 2+ times | Didn't read back stored content |
| 13 | Putting `<style>`/`<script>` in `html` field of CHB | 3+ times | Frappe silently strips both via `remove_script_and_style()` |
| 14 | Using `document.getElementById()` in CHB scripts | 3+ times | CHBs run in Shadow DOM — must use `root_element.querySelector()` |
| 15 | Only updating workspace `content` JSON, not `custom_blocks` child table | 3+ times | Frappe uses child table to render; content JSON mismatch causes blank page |
| 16 | Client Script deployed but nothing renders | 2+ times | Stale cache — must clear server cache via `frappe.sessions.clear` AND hard-refresh browser |
| 17 | HTML field overlaps with adjacent fields | 1+ times | HTML field shares row with other fields — must wrap in own Section Break with `hide_border: 1` |
| 18 | Inline onclick can't call Client Script functions | 2+ times | Client Script scope is isolated — must expose function via `window.fn_name = fn_name` |
| 19 | `frappe.new_doc()` changes workspace sidebar | 1+ times | Target DocType not linked in current workspace — see §9 for fixes |
| 20 | List view formatters don't appear | 1+ times | Formatters only apply to user-visible columns — `in_list_view: 1` doesn't override user config |


### ⚠️ CRITICAL: Workspace `custom_blocks` Child Table Must Be Synced

Frappe Workspace has TWO places that reference Custom HTML Blocks:
1. **`content` field** (JSON string) — the EditorJS block list
2. **`custom_blocks` child table** — a separate DB child table

**Frappe uses the child table to decide what to render. The content JSON alone is not enough.**

When you update a workspace via API to point to a new CHB, you **MUST update both**:

```python
def set_workspace_chb(ws_name, chb_name, header_text=None):
    # Get current workspace to preserve existing child row name/idx
    rv = requests.get(f"{BASE}/api/resource/Workspace/{ws_name}", headers=HDR)
    d = rv.json().get("data", {})
    existing_cb = d.get("custom_blocks", [])

    # Build content blocks
    content_blocks = [{"id": ws_name[:8]+"-cb1", "type": "custom_block",
        "data": {"custom_block_name": chb_name, "col": 12}}]
    if header_text:
        content_blocks.insert(0, {"id": ws_name[:8]+"-h1", "type": "header",
            "data": {"text": header_text, "level": 3, "col": 12}})

    # Reuse existing child row (to preserve name/idx), just update the CHB name
    if existing_cb:
        cb_row = existing_cb[0].copy()
        cb_row["custom_block_name"] = chb_name
        cb_row["label"] = chb_name
    else:
        cb_row = {"custom_block_name": chb_name, "label": chb_name,
                  "parentfield": "custom_blocks", "parenttype": "Workspace",
                  "doctype": "Workspace Custom Block"}

    # PUT both fields together in same request
    rv2 = requests.put(f"{BASE}/api/resource/Workspace/{ws_name}",
        headers=HDR,
        json={"content": json.dumps(content_blocks), "custom_blocks": [cb_row]})

    # VERIFY they are in sync
    rv3 = requests.get(f"{BASE}/api/resource/Workspace/{ws_name}", headers=HDR)
    d2 = rv3.json().get("data", {})
    content_chbs = [b.get("data",{}).get("custom_block_name")
                    for b in json.loads(d2.get("content","[]"))
                    if b.get("type") == "custom_block"]
    table_chbs = [c.get("custom_block_name") for c in d2.get("custom_blocks",[])]
    assert set(content_chbs) == set(table_chbs), f"OUT OF SYNC: content={content_chbs} table={table_chbs}"
```

**Symptom of mismatch:** The workspace page loads with the title but the content area is completely blank (empty white space). No error in console.

---

## 20. Platform Order — Greenfield Build Sequence {#20-platform-order}

When building a new Frappe application or module from scratch, implement in this order. Each layer must be stable before the next depends on it. Do NOT implement as a random ticket queue.

```
1. Login & Branding
2. Theme & Navigation (Workspace, sidebar links)
3. Settings & Setup (Single DocTypes, global config)
4. Users, Roles & Permissions
5. Fields & Form Hygiene (DocTypes, field specs, form layouts)
6. Approvals & Workflows
7. Alerts & Notifications
8. Dashboards & Reports
```

**Why this order matters:** Roles must exist before permissions can be assigned. Fields must exist before workflows can reference them. Workflows must exist before alerts can trigger on state changes. Dashboards need stable data before they can visualize anything.

### Config-vs-Code Decision

Before implementing ANY requirement, classify it using the decision tree in `frappe-doctype-skill` Part 0.3. The classification determines which deployment target (Translation, Property Setter, Client Script, Server Script, DocType fixture) you use. Getting this wrong causes 80% of iteration waste.

### The Layer Stack

All client work happens in Layer 4. Layers 1-3 are never modified for client-specific work.

| Layer | Contains | Modifiable? |
|---|---|---|
| 1 — Framework | Core platform, ORM, permissions engine | Never |
| 2 — Shared Extensions | Geo data, shared components, base theme | Never |
| 3 — Core Product | Grant lifecycle, compliance, core workflows | Never |
| 4 — Client App | All client-specific customizations | **Your work** |

If a requirement needs a change in Layers 1-3, **STOP and escalate to the System Architect**.


---

# PART B: Custom HTML Blocks — Deep Reference

> The following sections expand on §6 above with the full CHB deployment contract.
> Every rule below maps to a real failure from production deployment sessions.

---

## 1. How CHBs Actually Render — Shadow DOM {#1-shadow-dom}

Frappe renders every Custom HTML Block inside a **true Web Component with Shadow DOM**
via `frappe.create_shadow_element()`. This is the single most important thing to understand.

```javascript
// What Frappe does internally (from desk.bundle source):
frappe.create_shadow_element = function(container, html, style, script) {
  let cname = "custom-block-" + frappe.utils.get_random(5).toLowerCase();

  class CustomBlock extends HTMLElement {
    constructor() {
      super();
      let div = document.createElement("div");
      div.innerHTML = frappe.dom.remove_script_and_style(html); // ← strips <style> and <script> from html
      let styleEl = document.createElement("style");
      styleEl.textContent = style;                              // ← style field injected natively
      let scriptEl = document.createElement("script");
      scriptEl.textContent = `
        (function() {
          let root_element = document.querySelector('${cname}').shadowRoot; // ← injected by Frappe
          ${script}   // ← your script field runs here
        })();
      `;
      this.attachShadow({ mode: "open" });
      this.shadowRoot.appendChild(styleEl);
      this.shadowRoot.appendChild(div);
      this.shadowRoot.appendChild(scriptEl);
    }
  }
  customElements.define(cname, CustomBlock);
  container.innerHTML = `<${cname}></${cname}>`;
};
```

**Consequences you must never forget:**
- `<style>` and `<script>` tags in the `html` field are **silently stripped** before render
- Your script runs inside a shadow DOM — `document.getElementById()` **does not cross the boundary**
- Frappe auto-injects `root_element` (= `shadowRoot`) into your script scope — use it
- `frappe.call()`, `frappe.Chart`, jQuery — all work normally from inside the script field

---

## 2. The Critical Label-Match Rule {#2-label-match}

**This is the #1 cause of blank workspaces.** Confirmed from source code analysis.

Frappe's workspace renderer calls `lt.make("custom_block", custom_block_name)` which does:

```javascript
// From desk.bundle source — the make() function:
make(type, name) {
  let item = this.config.page_data[type + "s"].items.find(
    n => frappe.utils.unescape_html(n.label) == frappe.utils.unescape_html(__(name))
  );
  if (!item) return false;  // ← returns false silently, nothing renders
  // ... render the widget
}
```

`page_data.custom_blocks.items` is populated from the workspace's `custom_blocks` **child table**.
The `label` field in that child table row **must exactly equal** the `custom_block_name` value
used in the workspace `content` JSON.

### ✅ CORRECT

```python
# content JSON block:
{"id": "b1", "type": "custom_block", "data": {"custom_block_name": "my-dashboard-chb", "col": 12}}

# child table row — label MUST equal custom_block_name:
{"custom_block_name": "my-dashboard-chb", "label": "my-dashboard-chb", ...}
#                                                    ↑ must match exactly ↑
```

### ❌ WRONG (causes silent blank render)

```python
# child table row with a friendly label:
{"custom_block_name": "my-dashboard-chb", "label": "My Dashboard"}
# make() searches for label == "my-dashboard-chb", finds "My Dashboard" → returns false → blank
```

**Always verify with `get_desktop_page` after wiring:**

```python
r = requests.get(f"{BASE}/api/method/frappe.desk.desktop.get_desktop_page",
    headers=HDR,
    params={"page": json.dumps({"name": ws_name, "title": ws_name, "public": 1})})
items = r.json()["message"]["custom_blocks"]["items"]
for item in items:
    assert item["label"] == item["custom_block_name"], \
        f"LABEL MISMATCH: label={item['label']} != chb_name={item['custom_block_name']}"
```

---

## 3. DOM Querying — What Works vs What Silently Fails {#3-dom-querying}

`ShadowRoot` is NOT a `Document`. It does **not** have `getElementById()`.

| Method | Works? | Notes |
|---|---|---|
| `root_element.querySelector('#my-id')` | ✅ | Correct for all ID lookups |
| `root_element.querySelectorAll('.my-class')` | ✅ | Correct for class lookups |
| `document.getElementById('my-id')` | ❌ | Crosses shadow boundary — always returns `null` |
| `document.querySelector('#my-id')` | ❌ | Crosses shadow boundary — always returns `null` |
| `root_element.getElementById('my-id')` | ❌ | `TypeError` — method doesn't exist on ShadowRoot |

**Always use these helpers at the top of your script field:**

```javascript
// ── Shadow DOM helpers — use everywhere ────────────────────────────────────
function _q(sel)    { return root_element.querySelector(sel); }
function _qAll(sel) { return root_element.querySelectorAll(sel); }
function _el(id)    { return root_element.querySelector('#' + id); }
```

---

## 4. Three-Field Split {#4-three-fields}

**Never put `<style>` or `<script>` in the `html` field** — Frappe calls
`frappe.dom.remove_script_and_style(html)` before rendering, stripping both silently.

| Field | What goes here | What NOT to put here |
|---|---|---|
| `html` | Pure structural markup only | `<style>`, `<script>` tags |
| `style` | All CSS — injected into shadow DOM `<style>` | Do not put in `html` |
| `script` | All JavaScript — `root_element` auto-injected | Do not put in `html` |

**Correct structure:**

```python
chb_doc = {
    "name": "my-dashboard-chb",
    "html": '<div id="root"><div id="loading">Loading...</div></div>',
    "style": """
        :host { display: block; width: 100%; }
        #root { padding: 20px; font-family: Inter, sans-serif; }
    """,
    "script": """
        (function() {
            function _el(id) { return root_element.querySelector('#' + id); }
            _el('loading').textContent = 'Loaded at ' + new Date().toLocaleTimeString();
        })();
    """,
    "private": 0
}
```

---

## 5. Workspace Wiring — content JSON + child table must sync {#5-workspace-wiring}

Two places must be updated atomically in a single PUT — if they diverge, the workspace
renders blank with no error.

```python
import json, requests

def wire_chb_to_workspace(base, hdr, ws_name, chb_name):
    # Step 1: Build content JSON block
    content_blocks = [
        {"id": "ws-h1", "type": "header",
         "data": {"text": f"<span class='h4'><b>{ws_name}</b></span>", "col": 12}},
        {"id": "ws-chb-01", "type": "custom_block",
         "data": {"custom_block_name": chb_name, "col": 12}}  # ← chb_name here
    ]

    # Step 2: Build child table row — label MUST equal chb_name
    cb_row = {
        "custom_block_name": chb_name,
        "label": chb_name,         # ← MUST match content JSON custom_block_name exactly
        "parentfield": "custom_blocks",
        "parenttype": "Workspace",
        "doctype": "Workspace Custom Block"
    }

    # Step 3: PUT both together atomically
    r = requests.put(f"{base}/api/resource/Workspace/{requests.utils.quote(ws_name)}",
        headers={**hdr, "Content-Type": "application/json"},
        json={"content": json.dumps(content_blocks), "custom_blocks": [cb_row]})

    # Step 4: VERIFY via get_desktop_page (not just read-back)
    rv = requests.get(f"{base}/api/method/frappe.desk.desktop.get_desktop_page",
        headers=hdr,
        params={"page": json.dumps({"name": ws_name, "title": ws_name, "public": 1})})
    items = rv.json().get("message", {}).get("custom_blocks", {}).get("items", [])
    for item in items:
        assert item["label"] == item["custom_block_name"], \
            f"MISMATCH: {item['label']} != {item['custom_block_name']}"
    print(f"✅ Wired and verified: {chb_name} → {ws_name}")
```

**Also required when creating a new workspace:**

```python
ws_payload = {
    "name": ws_name,
    "label": ws_name,       # ← mandatory (required field)
    "title": ws_name,
    "module": "Dhwani Hrms",  # ← use existing module from working workspaces
    "for_user": "",           # ← must be empty string, not None
    "parent_page": "",        # ← must be empty string, not None
    "sequence_id": 57.0,
    "is_hidden": 0,
    "public": 1,
    "content": json.dumps(content_blocks),
    "custom_blocks": [cb_row]
}
```

---

## 6. Chart Libraries — CDN Will Fail, Inline Instead {#6-charts}

**Never load Chart.js or any library from an external CDN inside a CHB.** Safari, Brave,
and Firefox with Enhanced Tracking Protection silently block `cdnjs.cloudflare.com`,
`jsdelivr.net`, and `unpkg.com`. The script callback never fires → blank dashboard.

### Option A — Use `frappe.Chart` (recommended, zero deps)

`frappe.Chart` is the Frappe-bundled chart library (frappe/charts). Always available in
desk context. No CDN. Pass the DOM element directly, not a string selector.

```javascript
var container = root_element.querySelector('#my-chart');
new frappe.Chart(container, {
    type: 'bar',           // bar, line, donut, pie, percentage, heatmap, axis-mixed
    height: 280,
    data: {
        labels: ['Jan', 'Feb', 'Mar'],
        datasets: [{ values: [120, 85, 200] }]
    },
    colors: ['#66C2A5'],   // ColorBrewer Set2
    tooltipOptions: { formatTooltipY: d => new Intl.NumberFormat('en-IN').format(d) }
});
```

**Note:** `frappe.Chart` does NOT support horizontal bar charts. For horizontal bars,
use Option B.

### Option B — Inline Chart.js via npm (when you need horizontal bars)

```bash
npm install chart.js@4.4.1 --prefix /tmp/chartjs
# Copy /tmp/chartjs/node_modules/chart.js/dist/chart.umd.js into script field prefix
```

Then prepend the 205KB UMD source to your script field. The UMD exports to `globalThis.Chart`.
Confirm with `(globalThis.Chart != null)` before use.

### Option C — frappe.Chart for everything else

Horizontal bars can be approximated with a standard bar chart using `indexAxis: 'y'` in
Chart.js or use frappe.Chart's bar type with careful label wrapping.

---

## 7. page_data Discovery — How the Browser Loads CHBs {#7-page-data}

The browser uses `frappe.desk.desktop.get_desktop_page` (NOT `get_desktop_page_data`).
This is the canonical check for whether your CHB will render.

```python
# ✅ CORRECT — this is what the browser calls
r = requests.get(f"{BASE}/api/method/frappe.desk.desktop.get_desktop_page",
    headers=HDR,
    params={"page": json.dumps({"name": ws_name, "title": ws_name, "public": 1})})
page_data = r.json()["message"]
# page_data.keys() = ['charts', 'shortcuts', 'cards', 'onboardings',
#                     'quick_lists', 'number_cards', 'custom_blocks']

custom_block_items = page_data["custom_blocks"]["items"]
# Each item: {custom_block_name, label, parent, ...}

# ❌ WRONG — returns empty dict, useless for CHB verification
requests.post(f"{BASE}/api/method/frappe.desk.desktop.get_desktop_page_data", ...)
```

---

## 8. Pre-Flight Deployment Checklist {#8-checklist}

Run this before every CHB deployment:

```python
def verify_chb_deployment(base, hdr, chb_name, ws_name):
    results = {}

    # 1. CHB fields
    r = requests.get(f"{base}/api/resource/Custom HTML Block/{chb_name}", headers=hdr)
    chb = r.json().get("data", {})
    script = chb.get("script", "") or ""
    results["script_len > 100"]     = len(script) > 100
    results["style_len > 0"]        = len(chb.get("style") or "") > 0
    results["html has mount div"]   = len(chb.get("html") or "") > 10
    results["no document.getElementById in script"] = "document.getElementById(" not in script
    results["no root_element.getElementById"]       = "root_element.getElementById" not in script
    results["root_element used"]    = "root_element" in script
    results["no external CDN"]      = "cdnjs" not in script and "jsdelivr" not in script
    results["wrapped in IIFE"]      = script.strip().startswith("(function()")

    # 2. Workspace label match (THE CRITICAL CHECK)
    rv = requests.get(f"{base}/api/method/frappe.desk.desktop.get_desktop_page",
        headers=hdr,
        params={"page": json.dumps({"name": ws_name, "title": ws_name, "public": 1})})
    items = rv.json().get("message", {}).get("custom_blocks", {}).get("items", [])
    target = next((i for i in items if i.get("custom_block_name") == chb_name), None)
    results["chb in page_data"]     = target is not None
    results["label == chb_name"]    = target is not None and target.get("label") == chb_name

    # 3. Print
    all_pass = all(results.values())
    for check, ok in results.items():
        print(f"  {'✅' if ok else '❌'} {check}")
    print(f"\n{'✅ READY' if all_pass else '❌ BLOCKED — fix above before testing in browser'}")
    return all_pass
```

---

## 9. Debugging Protocol — Blank Screen Triage {#9-debug}

When the workspace shows the header but the CHB area is blank:

```
Step 1: Run verify_chb_deployment() above.
         → If "label == chb_name" is ❌ → fix the child table label (§2)
         → If "chb in page_data" is ❌ → workspace not wired correctly (§5)

Step 2: Deploy a 3-line minimal test CHB first.
         html:   '<div id="probe" style="padding:20px;background:#4ade80;font-size:20px">TEST</div>'
         script: 'root_element.querySelector("#probe").textContent = "CHB WORKS " + Date.now();'
         style:  '#probe { border-radius: 8px; }'
         Wire it to the workspace as the FIRST block.
         → If green box appears → CHB rendering works, issue is in your complex script
         → If still blank → workspace rendering itself is broken (check §2 and §5)

Step 3: If minimal CHB works but complex script doesn't:
         → Open browser console (F12) and look for JavaScript errors
         → Common errors:
             TypeError: root_element.getElementById is not a function  → use querySelector (§3)
             TypeError: Cannot read properties of null (reading '...')  → element not in DOM yet,
               or wrong selector — check your html field has the element
             frappe.call error → network/permissions issue, not CHB
         → Wrap script in try-catch to surface errors:
             try { /* your code */ } catch(e) { root_element.querySelector('#root').textContent = e; }

Step 4: Verify CDN is not blocking chart render (§6).
         → Replace CDN load with inline library or frappe.Chart
```

---

## Appendix: India Drill-down Map CHB (Geo Asset Contract) {#appendix-geo}

When the CHB is an India drill-down map (State → District → Block), use the unified
TopoJSON dataset that lives in this repo under `assets/india-admin-geo/topo/`.
Design tokens, ColorBrewer picker, hover-card field menu, and the full drop-in block
are in **`frappe-design/REFERENCE.md` §6.6**. Everything below is deployment-only.

### Two delivery modes

**Production — install-time copy into the app's public assets (recommended):**
```bash
mkdir -p apps/<app>/<app>/public/geo
cd apps/<app>/<app>/public/geo
for f in states districts blocks; do
  curl -sSL -o "${f}.topojson" \
    "https://cdn.jsdelivr.net/gh/Swapnilchesa/Frappe-Skills@main/assets/india-admin-geo/topo/${f}.topojson"
done
cd -
bench build --app <app>
```
Reference from the CHB as `/assets/<app>/geo/<layer>.topojson`. No runtime CDN dependency.

**Prototype — CDN runtime:**
Set `GEO = "https://cdn.jsdelivr.net/gh/Swapnilchesa/Frappe-Skills@main/assets/india-admin-geo/topo"` in the CHB. Pin `@v1.0.0` or a commit SHA for anything past a demo. Not production.

### Whitelisted data method

The CHB calls one method per level: `<app>.api.map_metrics(level, state_lgd?, district_lgd?)`.
Template at `assets/india-admin-geo/reference/api.py` — copy into `apps/<app>/<app>/api.py`,
edit the DocType/field constants at the top. Returns
`[{key, metric, grantees, portfolios:[{name,count}], aspirational, ...user-picked keys}]`.

### CHB wiring specifics (in addition to §6, §5, §2 of Part B)

- **Leaflet + topojson-client from CDN:** unpkg.com is allowed by the Frappe CDN policy
  (see §8 of Part A). If your instance blocks unpkg, vendor Leaflet into `/assets/<app>/geo/vendor/`.
- **Canvas rendering.** `L.map(el, { preferCanvas: true })` — required for 6,800 block polygons.
- **Shadow DOM.** The map mount element must be queried via `root_element.querySelector`
  (never `document.getElementById` — see §3 of Part B). Leaflet then mounts into that element
  normally; it does not need any shadow-DOM special handling beyond the root lookup.
- **Gzip.** If nginx is not sending `Content-Encoding: gzip` for `.topojson`, cold load of
  `blocks.topojson` is 5.6 MB instead of 1.5 MB. Add to nginx.conf:
  ```
  gzip_types application/json application/geo+json;
  ```
- **Label-match rule still applies** (§2 of Part B) — the CHB's `custom_block_name` must match
  the workspace child table `label` exactly.

### Verification additions to the standard checklist

In addition to `verify_chb_deployment()` (§8 of Part B):

```python
def verify_geo_assets(base, hdr, app):
    for f in ["states", "districts", "blocks"]:
        url = f"{base}/assets/{app}/geo/{f}.topojson"
        r = requests.head(url)
        print(f"  {'✅' if r.status_code == 200 else '❌'} {url} → {r.status_code}")
```

If any of the three returns 404 → user forgot `bench build --app <app>` after copying.

### Known failure modes specific to the geo CHB

1. **Diacritic join failure.** If the user's grant records key on `state_name` (e.g. "Bihar")
   but someone changed a row to "Bihār", the map silently drops those records. Force the API
   method to aggregate on `state_lgd` only.
2. **Delhi "Preet Vihar" block** has null `district_lgd`. Either override to `0174` (East Delhi)
   in the user's data OR filter it out of drill-down. Ask in Phase 1.
3. **Missing newly-created districts.** The unified dataset has 780 districts (as of Feb 2025).
   If the user's DB has a `district_lgd` not in `districts.topojson`, show a "map coverage pending"
   note in the info card instead of dropping the record.

---

## 10. Post-Mortem — Every Mistake Made {#10-postmortem}

Read `references/REFERENCE.md` for complete code templates.

| # | Mistake | Root Cause | Fix |
|---|---|---|---|
| 1 | Tried to deploy via Frappe Page | Page script is filesystem-only, not DB | Use CHB (script field IS in DB) |
| 2 | Workspace creation 409 NameError | `label` field missing from payload | Add `"label": ws_name` to workspace POST |
| 3 | Route conflict 409 | Probe page `resource-dashboard` was never deleted | DELETE `/api/resource/Page/<name>` before creating workspace with same title |
| 4 | CHB created but nothing renders | Script used `document.getElementById()` — returns null in shadow DOM | Use `root_element.querySelector('#id')` |
| 5 | Still blank after querySelector fix | `root_element.getElementById()` called in IIFE guard — throws `TypeError` on `ShadowRoot` | `ShadowRoot` has no `getElementById` — always use `querySelector` |
| 6 | Blank after getElementById fix | Chart.js CDN blocked by Safari tracking prevention | Inline Chart.js via npm install |
| 7 | Blank after inlining Chart.js | **Label mismatch** — child table had `label: "Resource Dashboard"` but `make()` searched for `label: "resource-dashboard-chb"` | Set `label = custom_block_name` in child table row |
| 8 | Used wrong verification API | `get_desktop_page_data` returns empty, not useful | Use `get_desktop_page` with `page` param |
| 9 | `for_user` / `parent_page` were `None` | New workspace missing fields that working workspaces have as empty string | Set `for_user: ""`, `parent_page: ""`, `sequence_id: <float>` |
| 10 | CSS not scoped | Put CSS in JS string and injected via `document.createElement` | Put CSS in `style` field — Frappe injects it natively into shadow `<style>` |

---

**Now read `references/REFERENCE.md`** for: complete working templates, the full
`verify_chb_deployment()` function, IIFE script pattern, frappe.Chart examples,
and the complete workspace creation + wiring script.
