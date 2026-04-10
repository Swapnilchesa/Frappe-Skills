---
name: frappe-v16-deployment
description: >
  Comprehensive knowledge base for deploying custom HTML dashboards, Pages, Workspaces,
  and Custom HTML Blocks on Frappe Framework v15/v16 instances â€” especially when accessed
  via API without bench/SSH access. Covers the critical differences between Page doctype,
  Web Page, Custom HTML Block, and Workspace content; the developer_mode dependency;
  JS bundle availability per context; CDN restrictions; and working deployment patterns.
  MUST READ before any Frappe deployment task to avoid repeated errors.
---

# Frappe v15/v16 Deployment Knowledge Base

> **Purpose**: This skill prevents Claude from making repeated errors when deploying custom
> dashboards and UI to Frappe instances. Every section documents a real mistake and the
> correct approach. Read this ENTIRELY before writing any deployment code.
>
> **Reference files — read when directed:**
> - `references/deployment-targets.md` — detailed §4–14: JS bundle availability, CDN restrictions, sidebar/navigation, bundle hash discovery, iframe pitfalls, custom themes, Server Script limits, API virtual fields
> - `references/working-templates.md` — complete copy-paste deployment scripts for Page, CHB, Web Page, and shared bundle targets
> - `evals/evals.json` — test cases for validating deployment guidance quality

---

## Table of Contents

1. [Frappe Page Architecture â€” How It Actually Works](#1-frappe-page-architecture)
2. [The developer_mode Gate](#2-the-developer_mode-gate)
3. [Four Deployment Targets Compared](#3-four-deployment-targets)
4. [JS Bundle Availability by Context](#4-js-bundle-availability)
5. [Workspace Content JSON Structure](#5-workspace-content-json)
6. [Custom HTML Block â€” Correct Usage](#6-custom-html-block)
7. [Web Page â€” Limitations and Workarounds](#7-web-page)
8. [CDN and External Script Restrictions](#8-cdn-restrictions)
9. [Sidebar and Navigation in v16](#9-sidebar-and-navigation)
10. [Bundle Hash Discovery](#10-bundle-hash-discovery)
11. [iframe Embedding Pitfalls](#11-iframe-embedding)
12. [Custom Workspace Themes (e.g., SVA)](#12-custom-workspace-themes)
13. [Server Script Limitations](#13-server-script-limitations)
14. [API Field Names â€” What's Real vs Virtual](#14-api-field-names)
15. [Decision Tree â€” Which Deployment Path?](#15-decision-tree)
16. [Pre-Flight Checklist](#16-pre-flight-checklist)
17. [Working Code Templates](#17-working-code-templates)

---

## 1. Frappe Page Architecture â€” How It Actually Works {#1-frappe-page-architecture}

### âŒ WRONG ASSUMPTION (Claude kept making this error)

> "I'll create a Page via API and set the `script` and `style` fields â€” they'll persist in the database."

### âœ… REALITY

The **Page doctype** in Frappe stores `script`, `style`, and `content` fields **on the filesystem**, NOT in the database.

```
apps/<app_name>/<app_name>/<module>/page/<page_name>/
â”œâ”€â”€ <page_name>.json     # Page metadata (stored in DB + exported to file)
â”œâ”€â”€ <page_name>.js       # JavaScript (FILESYSTEM ONLY)
â”œâ”€â”€ <page_name>.css      # Styles (FILESYSTEM ONLY)
â””â”€â”€ <page_name>.html     # HTML template (FILESYSTEM ONLY)
```

**Key behaviors:**
- When you call `frappe.db.set_value('Page', 'my-page', 'script', js_code)`, it does NOT create a DB column â€” the `script` field is a **virtual property** loaded from the `.js` file.
- The Page API's `as_dict()` method includes `script`, `style`, `content` by reading from the filesystem â€” but you CANNOT write to them via the API unless `developer_mode` is ON and the page belongs to a custom app.
- Without `developer_mode`, the API will accept the POST/PUT silently but the values won't persist â€” the page will be **blank**.

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
| Create Page with JS/CSS that persists | âœ… | âŒ Blank page |
| Create non-custom DocType | âœ… | âŒ |
| Delete standard Pages | âœ… | âŒ |
| Export module JSON | âœ… | âŒ |
| Create Web Page via API | âœ… | âœ… |
| Create Custom HTML Block via API | âœ… | âœ… |
| Create Workspace via API | âœ… | âœ… |
| Create Server Script via API | âœ… | âœ… |
| `frappe.call()` works in Desk context | âœ… | âœ… |

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
| Requires developer_mode | âœ… YES | âŒ No | âŒ No | âŒ No |
| Runs inside Frappe Desk | âœ… Full desk context | âŒ Portal context | âœ… Inside workspace | âœ… On form/list |
| Has jQuery | âœ… | âŒ Only if desk bundle loaded | âœ… | âœ… |
| Has `frappe.call()` | âœ… | âŒ Not natively | âœ… | âœ… |
| Has `frappe.Chart` | âœ… | âŒ Not natively | âœ… | âœ… |
| Has Frappe sidebar | âœ… | âŒ | âœ… Workspace sidebar | âœ… |
| Supports inline `<script>` | âœ… | âš ï¸ Depends on version | âš ï¸ Depends on theme | N/A |
| URL pattern | `/app/<page-name>` | `/<route>` | `/app/<workspace-name>` | N/A |
| Max content size | Unlimited (filesystem) | ~5MB (DB field) | ~2MB (DB field) | ~64KB |
| Deployment via API (no SSH) | âŒ Without dev mode | âœ… | âœ… | âœ… |

### When to Use Each

- **Page**: Best option IF developer_mode is ON. Full desk context, all JS libraries available, proper URL routing.
- **Web Page**: Fallback when developer_mode is OFF. But you lose desk context (no sidebar, no frappe.Chart unless you load desk.bundle).
- **Custom HTML Block**: Best for embedding content inside an existing Workspace. But limited by workspace theme and block rendering logic.
- **Client Script**: Best for small UI augmentations on existing forms/lists. Not suitable for full dashboards.

---

## 4. JS Bundle Availability by Context {#4-js-bundle-availability}

### âŒ WRONG ASSUMPTION (Claude kept making this error)

> "Web Pages have jQuery and frappe.Chart available since they're served from the same Frappe instance."

### âœ… REALITY

Frappe loads DIFFERENT JavaScript bundles depending on the page context:

| Bundle | Desk Pages (`/app/*`) | Web Pages (`/route`) | What It Contains |
|--------|:-:|:-:|---|
| `libs.bundle.js` | âœ… | âœ… | jQuery, Moment.js, Socket.io client |
| `desk.bundle.js` | âœ… | âŒ | `frappe.call()`, `frappe.Chart`, `frappe.ui.*`, full Frappe desk framework |
| `frappe-web.bundle.js` | âŒ | âœ… | Minimal web context (no Chart, no desk UI) |
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
1. Discover the correct bundle hash first (see Â§10)
2. Poll-wait for dependencies before initializing your code
3. Accept that this loads ~2MB of extra JS and may cause conflicts

### Better Workaround

If you need charts on a Web Page without loading desk.bundle, use:
- **Chart.js** (from same-origin if CDN is blocked)
- **Apache ECharts** (lighter than desk.bundle)
- Inline SVG generation for simple charts
- `frappe-charts` standalone IIFE from same-origin upload

### Shared JS Logic Across Deployment Targets

**If any function is used by more than one deployment target (CHB + Desk Page, or two CHBs, or a Client Script + a CHB), it must be declared in a shared bundle via `frappe.provide` — never on `window` directly.**

Claude and Cursor default to `window.my_fn = function(){}` for shared helpers. This causes ESLint `"not defined"` warnings, requires defensive guard checks (`window.fn && window.fn()`), and breaks silently when the `window` state differs between Web Page and Desk Page contexts.

```javascript
// ❌ BANNED — shared helper on window
window.formatGrantAmount = function(val) { ... };
// Consuming file needs guard check — fragile:
window.formatGrantAmount && window.formatGrantAmount(val);
```

```javascript
// ✅ REQUIRED — shared bundle using frappe.provide
// File: myapp/public/js/grant_utils.bundle.js
frappe.provide("myapp.grant_utils");

myapp.grant_utils.formatAmount = function(val) {
    return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(val);
};

myapp.grant_utils.getStatusColor = function(status) {
    return { Approved: '#22c55e', Rejected: '#ef4444', Pending: '#f59e0b' }[status] || '#6b7280';
};
```

```python
# hooks.py — expose bundle to entire desk context
app_include_js = [
    "/assets/myapp/js/grant_utils.bundle.js"
]
```

```javascript
// Any CHB script, Client Script, or Desk Page — no guards needed
var color = myapp.grant_utils.getStatusColor(row.status);
```

**Why `window.*` breaks across deployment targets specifically:**
Web Pages load `frappe-web.bundle.js`, not `desk.bundle.js`. The `window` object is shared, but any function defined on `window` in a Desk Page script will NOT be present when a Web Page loads — the execution context is different and the desk scripts don't run. `frappe.provide` + `app_include_js` is the only pattern that reliably spans both contexts (for desk-context targets — Web Pages still need the bundle loaded manually via §4's workaround above).

**The exception — Template C's `window.frappe = {}` shim:**
The shim in §17 Template C (`if (typeof frappe === 'undefined') window.frappe = {}`) is intentional and correct — it recreates the `frappe` object in Web Page context where `desk.bundle.js` is absent. This is not a `window.*` violation; it is a polyfill. Do not apply the `frappe.provide` rule to it.

---

## 5. Workspace Content JSON Structure {#5-workspace-content-json}

### âŒ WRONG ASSUMPTION (Claude kept making this error)

> "I'll set workspace content to `[{"type": "custom_block", "data": {"custom_block_name": "My Block", "col": 12}}]`"

### âœ… REALITY

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
- `id` â€” **REQUIRED**. Every block needs a unique ID string. Without it, the workspace rendering may fail silently.
- `type` â€” Must match exactly: `"header"`, `"paragraph"`, `"chart"`, `"shortcut"`, `"card"`, `"custom_block"`, `"number_card"`, `"onboarding"`, `"spacer"`

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


## 7. Web Page â€” Limitations and Workarounds {#7-web-page}

### What It Is

A `Web Page` creates a publicly routable page at `/<route>`. It's part of Frappe's portal/website system, NOT the Desk.

### Key Fields

| Field | Type | Notes |
|-------|------|-------|
| `name` | Data | Internal name |
| `title` | Data | Page title |
| `route` | Data | URL route (e.g., `my-dashboard` â†’ `/my-dashboard`) |
| `content_type` | Select | "Rich Text", "Markdown", "HTML" |
| `main_section` | Code | **v14**: Main HTML content field |
| `main_section_html` | Code | **v15+**: Main HTML content field when content_type is HTML |
| `published` | Check | Must be 1 to be accessible |
| `full_width` | Check | Set to 1 to remove page margins |
| `show_title` | Check | Set to 0 to hide the page title |

### âš ï¸ Field Name Confusion (Claude made this error)

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
// Minimal shim â€” NOT full frappe.call
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

### âœ… REALITY

Many browsers (especially Safari, Brave, Firefox with Enhanced Tracking Protection) **block third-party scripts** from CDN domains like:
- `cdn.jsdelivr.net`
- `cdnjs.cloudflare.com`
- `unpkg.com`

This is NOT a Frappe issue â€” it's browser Tracking Prevention. The scripts are silently blocked with no console error in some browsers.

### Rules

1. **NEVER rely on external CDNs** for critical dashboard functionality.
2. **Always use same-origin scripts** â€” load from `/assets/` on the same Frappe instance.
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
has_chart = 'frappe.Chart' in resp.text  # Usually NO â€” it's in desk.bundle
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

### âœ… CORRECT APPROACH

1. **Use Frappe's native Workspace sidebar** â€” don't fight it
2. Create a **Workspace** for your dashboard (appears in the sidebar automatically)
3. Use **horizontal top tabs** within the workspace content area for sub-navigation
4. If embedding a full-page dashboard, the dashboard should NOT have its own sidebar

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
| No Frappe sidebar | Web Page doesn't have desk chrome | Expected â€” use workspace for sidebar |
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

Study how existing dashboards are deployed on that instance and replicate the exact pattern â€” don't try to invent a new deployment approach.

---

## 13. Server Script Limitations {#13-server-script-limitations}

### âŒ WRONG ASSUMPTION (Claude made this error)

> "I'll use a Server Script with `frappe.db.set_value('Page', 'my-page', 'script', js_code)` to deploy JS."

### âœ… REALITY

- The `script` field of a Page doctype **has NO database column** â€” it's a virtual property
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

## 14. API Field Names â€” What's Real vs Virtual {#14-api-field-names}

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

This makes it LOOK like these are database fields you can write to. They're NOT â€” they're loaded from the filesystem by `as_dict()`.

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

## 15. Decision Tree â€” Which Deployment Path? {#15-decision-tree}

```
START: Need to deploy a custom dashboard to Frappe
â”‚
â”œâ”€ Q1: Do you have developer_mode ON?
â”‚  â”œâ”€ YES â†’ Use Page doctype (best option)
â”‚  â”‚        â”œâ”€ Full desk context (jQuery, frappe.Chart, frappe.call)
â”‚  â”‚        â”œâ”€ Proper URL: /app/my-dashboard
â”‚  â”‚        â”œâ”€ Deploy JS/CSS via API
â”‚  â”‚        â””â”€ Add to Workspace sidebar for navigation
â”‚  â”‚
â”‚  â””â”€ NO â†’ Continue to Q2
â”‚
â”œâ”€ Q2: Does the instance have a custom workspace theme?
â”‚  â”œâ”€ YES â†’ Study the existing theme's deployment pattern
â”‚  â”‚        â”œâ”€ Check for theme-specific configuration doctypes
â”‚  â”‚        â”œâ”€ Replicate how existing dashboards are deployed
â”‚  â”‚        â””â”€ May need iframe embedding in Custom HTML Block
â”‚  â”‚
â”‚  â””â”€ NO or UNKNOWN â†’ Continue to Q3
â”‚
â”œâ”€ Q3: Does your dashboard need frappe.Chart or frappe.call?
â”‚  â”œâ”€ YES â†’ Use Custom HTML Block in Workspace
â”‚  â”‚        â”œâ”€ Runs inside Desk context (all JS available)
â”‚  â”‚        â”œâ”€ Create block â†’ Add to workspace content JSON
â”‚  â”‚        â”œâ”€ Appears in sidebar via workspace
â”‚  â”‚        â””â”€ âš ï¸ Content limit ~2MB
â”‚  â”‚
â”‚  â””â”€ NO (plain HTML/CSS or uses its own chart lib) â†’
â”‚     Use Web Page
â”‚     â”œâ”€ No desk context needed
â”‚     â”œâ”€ Route: /my-dashboard
â”‚     â”œâ”€ full_width: 1, show_title: 0
â”‚     â””â”€ Optionally embed in workspace via iframe
â”‚
â””â”€ FALLBACK: If nothing works â†’
   â”œâ”€ Ask user to enable developer_mode (even temporarily)
   â”œâ”€ Deploy Page, then disable developer_mode
   â””â”€ The Page will continue to work after disabling
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

> **Read `references/working-templates.md` for all complete, copy-paste-ready templates.**
> Choose based on your situation:

| Template | When to use |
|---|---|
| **A — CHB + Workspace** | developer_mode OFF (most common). Safest path. |
| **B — Page** | developer_mode ON confirmed. Full desk context. |
| **C — Web Page + shim** | developer_mode OFF, portal context, no desk sidebar needed. |
| **D — Shared bundle** | Logic shared across two or more deployment targets. |

Each template in the reference file includes the full Python deployment script, field-by-field
verification steps, and the workspace sync pattern (content JSON + custom_blocks child table).

**Quick decision:**
- No SSH, developer_mode unknown → check §2 first, then use Template A
- Need frappe.Chart in a workspace tab → Template A (CHB)
- Need full desk page at `/app/my-page` → Template B (verify developer_mode first)
- Need portal URL, no sidebar → Template C
- Sharing helpers across pages/CHBs → Template D (`frappe.provide`)

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

