---
name: frappe-custom-html-block
description: >
  Deploy, debug, and iterate on Custom HTML Blocks (CHBs) inside Frappe v15/v16 Workspaces
  via the REST API — without SSH or developer_mode. Use this skill whenever:
  building a dashboard inside a Frappe workspace, creating or updating a Custom HTML Block
  doctype, wiring a CHB into a workspace sidebar, debugging blank/empty CHB content,
  deploying charts or interactive UI to a Frappe desk workspace, or any task involving
  frappe.create_shadow_element, workspace content JSON, or custom_blocks child table.
  ALWAYS use this skill before writing any CHB code — the shadow DOM context, label-matching
  rules, and page_data lookup are non-obvious and have caused repeated failures without it.
---

# Frappe Custom HTML Block — Deploy & Debug Skill

**This skill is a binding contract born from a real deployment session.** Every rule below
maps to a real failure. Read it fully before writing a single line of CHB code.

Before starting, also read `references/REFERENCE.md` for complete code templates,
the full post-mortem table, and the verified deployment checklist.

> **Reference files in this skill:**
> - `references/REFERENCE.md` — complete IIFE template, frappeCallPromise, three-state boilerplate, full verify_chb_deployment(), workspace wiring script, frappe.Chart examples, memory leak cleanup
> - `evals/evals.json` — test cases for validating CHB generation quality

---

## Table of Contents

1. [How CHBs Actually Render — Shadow DOM](#1-shadow-dom)
2. [The Critical Label-Match Rule](#2-label-match) ← **Most common blank screen cause**
3. [DOM Querying — What Works vs What Silently Fails](#3-dom-querying)
4. [Three-Field Split — html / script / style](#4-three-fields)
5. [Workspace Wiring — content JSON + child table must sync](#5-workspace-wiring)
6. [Chart Libraries — CDN Will Fail, Inline Instead](#6-charts)
7. [page_data Discovery — How the Browser Loads CHBs](#7-page-data)
8. [Pre-Flight Deployment Checklist](#8-checklist)
9. [Debugging Protocol — Blank Screen Triage](#9-debug)
10. [Post-Mortem — Every Mistake Made](#10-postmortem)
11. [Scale & Performance NFRs — Every Dashboard Must Pass This](#11-scale) ← **Read before writing any data-fetching code**

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
    "module": MODULE_NAME,     # ← NEVER hardcode; query an existing workspace first:
                               #   r = requests.get(f"{BASE}/api/resource/Workspace?limit=1", headers=HDR)
                               #   MODULE_NAME = r.json()["data"][0]["module"]
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

---

## 11. Scale & Performance NFRs — Every Dashboard Must Pass This {#11-scale}

**This section is a binding contract for production dashboards.** A CHB that passes the
deployment checklist (§8) but violates rules here will work in dev and fail for real users.
Every rule below maps to a class of real dashboard failures.

---

### Rule 1 — No Hardcoded Data. Ever.

**Violation: any literal value in `datasets`, `labels`, `values`, or any DOM `textContent`
that is not derived from a `frappe.call()` response.**

The chart example in §6 shows hardcoded labels and values. That pattern is for illustration
only. In production:

```javascript
// ❌ BANNED — hardcoded data
new frappe.Chart(container, {
    data: { labels: ['Jan', 'Feb', 'Mar'], datasets: [{ values: [120, 85, 200] }] }
});

// ✅ REQUIRED — all data from API
frappe.call({
    method: 'frappe.client.get_list',
    args: { doctype: 'My DocType', fields: ['month', 'amount'], limit: 12 },
    callback: function(r) {
        new frappe.Chart(container, {
            data: {
                labels: r.message.map(d => d.month),
                datasets: [{ values: r.message.map(d => d.amount) }]
            }
        });
    }
});
```

The `verify_chb_deployment()` checklist in §8 must be extended to flag any script containing
literal array values (`[{`) that are not inside a `callback` or `.then()` block.

---

### Rule 2 — Parallel API Calls via Promise.all

**A dashboard with N data sections must fire all N calls simultaneously, not sequentially.**

Sequential calls are the #1 performance failure on multi-KPI dashboards. Each `frappe.call()`
adds 200–800ms latency. Four sequential calls = up to 3.2s blank screen.

```javascript
// ❌ BANNED — sequential calls, total time = sum of all latencies
frappe.call({ method: 'get_kpi_1', callback: r1 => {
    frappe.call({ method: 'get_kpi_2', callback: r2 => {
        frappe.call({ method: 'get_kpi_3', callback: r3 => {
            render(r1, r2, r3);
        }});
    }});
}});

// ✅ REQUIRED — parallel calls via Promise.all, total time = slowest single call
function frappeCallPromise(method, args) {
    return new Promise((resolve, reject) => {
        frappe.call({
            method: method,
            args: args || {},
            callback: r => resolve(r.message),
            error: e => reject(e)
        });
    });
}

Promise.all([
    frappeCallPromise('myapp.api.get_kpi_1'),
    frappeCallPromise('myapp.api.get_kpi_2'),
    frappeCallPromise('myapp.api.get_kpi_3')
]).then(([kpi1, kpi2, kpi3]) => {
    render(kpi1, kpi2, kpi3);
}).catch(err => {
    showError('Dashboard data failed to load. Refresh to retry.');
});
```

**Copy this `frappeCallPromise` helper into every CHB script that makes more than one call.**
It is the standard wrapper; do not reinvent it per dashboard.

---

### Rule 3 — Mandatory Loading State + Error Boundary

Every CHB must have three render states in its HTML: **loading**, **error**, and **content**.
A dashboard that shows blank on failure is indistinguishable from a broken CHB (§9).

```html
<!-- html field — three states, always present -->
<div id="root">
    <div id="state-loading">
        <div class="skeleton-bar"></div>
        <div class="skeleton-bar short"></div>
        <div class="skeleton-bar"></div>
    </div>
    <div id="state-error" style="display:none"></div>
    <div id="state-content" style="display:none">
        <!-- real dashboard markup goes here -->
    </div>
</div>
```

```css
/* style field — skeleton animation */
.skeleton-bar {
    height: 18px; background: var(--skeleton-bg, #e5e7eb);
    border-radius: 4px; margin: 10px 0;
    animation: shimmer 1.4s infinite;
    width: 100%;
}
.skeleton-bar.short { width: 60%; }
@keyframes shimmer {
    0%   { opacity: 1; }
    50%  { opacity: 0.4; }
    100% { opacity: 1; }
}
#state-error {
    padding: 16px; border-radius: 6px;
    background: #fef2f2; color: #991b1b;
    font-size: 13px; border: 1px solid #fecaca;
}
```

```javascript
// script field — state transition helpers, use in every CHB
function showLoading() {
    _el('state-loading').style.display = '';
    _el('state-error').style.display   = 'none';
    _el('state-content').style.display = 'none';
}
function showError(msg) {
    _el('state-loading').style.display = 'none';
    _el('state-error').style.display   = '';
    _el('state-content').style.display = 'none';
    _el('state-error').textContent = '⚠ ' + (msg || 'Failed to load. Refresh to retry.');
}
function showContent() {
    _el('state-loading').style.display = 'none';
    _el('state-error').style.display   = 'none';
    _el('state-content').style.display = '';
}

// Usage pattern — always wrap data fetch in this structure
showLoading();
Promise.all([...]).then(data => {
    renderDashboard(data);
    showContent();
}).catch(err => {
    console.error('CHB load error:', err);
    showError();
});
```

**The pre-flight checklist (§8) must reject any CHB that does not contain `showError` or
an equivalent pattern.**

---

### Rule 4 — Memory Leak Prevention

**Every timer, interval, or event listener created in a CHB script must be cleaned up.**

Shadow DOM components can be unmounted and remounted (workspace tab switch, page refresh).
Dangling `setInterval` calls accumulate silently — each workspace open adds another copy.

```javascript
// ❌ BANNED — dangling interval, multiplies on every workspace open
setInterval(() => refreshData(), 30000);

// ✅ REQUIRED — store handle, clear on disconnect
var _refreshTimer = null;

function startAutoRefresh() {
    if (_refreshTimer) clearInterval(_refreshTimer); // guard against double-start
    _refreshTimer = setInterval(() => loadDashboard(), 30000);
}

// Frappe does not provide a CHB unmount hook — use MutationObserver on the host element
var _hostEl = root_element.host;
var _observer = new MutationObserver(function() {
    if (!document.contains(_hostEl)) {
        clearInterval(_refreshTimer);
        _observer.disconnect();
    }
});
_observer.observe(document.body, { childList: true, subtree: true });

startAutoRefresh();
```

For CHBs that do not use timers, this rule still applies to any `addEventListener` calls
on `document` or `window` (not on `root_element`) — those cross the shadow boundary and
must be explicitly removed.

---

### Rule 5 — DOM Batching — One Write, Not N Writes

**Never update the DOM inside a loop. Build a complete HTML string, then assign once.**

Each `appendChild()` or `innerHTML =` inside a loop triggers a browser reflow. On dashboards
with tables or card grids this causes visible jank at 20+ rows.

```javascript
// ❌ BANNED — N reflows for N rows
data.forEach(row => {
    let tr = document.createElement('tr');
    tr.innerHTML = `<td>${row.name}</td><td>${row.amount}</td>`;
    _el('my-table-body').appendChild(tr);
});

// ✅ REQUIRED — one reflow regardless of row count
var html = data.map(row =>
    `<tr><td>${frappe.utils.escape_html(row.name)}</td>
         <td>${frappe.format(row.amount, { fieldtype: 'Currency' })}</td></tr>`
).join('');
_el('my-table-body').innerHTML = html;
```

**Always use `frappe.utils.escape_html()` on any user-supplied string rendered into
`innerHTML` — unescaped data is an XSS vector inside the shadow DOM.**

---

### Rule 6 — Large Dataset Guard (Hard Limit on Rows)

**Never render an unbounded query result into the DOM.**

`frappe.client.get_list` defaults to `limit: 20`. A developer removing that limit to "show
all records" will silently fetch tens of thousands of rows and lock the browser thread.

```javascript
// ❌ BANNED — no limit, unbounded fetch
frappe.call({ method: 'frappe.client.get_list',
    args: { doctype: 'Grant Application', fields: ['*'] } });

// ✅ REQUIRED — explicit limit always; declare in CHB_CONFIG (see Rule 7)
frappe.call({
    method: 'frappe.client.get_list',
    args: { doctype: CHB_CONFIG.doctype, fields: ['name', 'status', 'amount'],
            limit: CHB_CONFIG.max_rows, order_by: 'modified desc' },
    callback: r => {
        if (r.message.length === CHB_CONFIG.max_rows) {
            _el('row-count-note').textContent =
                `Showing top ${CHB_CONFIG.max_rows} records. Use filters to narrow.`;
        }
        renderTable(r.message);
    }
});
```

For dashboards showing aggregates (KPI cards, charts), use server-side aggregation via
a whitelisted Python method — never fetch raw rows and aggregate in JS.

```python
# ✅ Aggregate server-side in a whitelisted method
@frappe.whitelist()
def get_grant_summary(filters=None):
    return frappe.db.sql("""
        SELECT status, COUNT(*) as count, SUM(amount) as total
        FROM `tabGrant Application`
        WHERE docstatus < 2
        GROUP BY status
    """, as_dict=True)
```

---

### Rule 7 — No Hardcoded Config Values in the CHB Script

**Instance-specific values (doctype names, module names, site URLs, role names) must not
be literals scattered in the script.** They break on staging vs production and across
client deployments. Declare a single `CHB_CONFIG` object at the top of the script.

```javascript
// ❌ BANNED — hardcoded config scattered through the script
frappe.call({ method: 'frappe.client.get_list',
    args: { doctype: 'Dhwani Grant Application' } });

// ✅ REQUIRED — all config in one block at the top, referenced everywhere below
var CHB_CONFIG = {
    doctype:    'Grant Application',
    report:     'Monthly Grant Summary',
    max_rows:   500,
    date_field: 'submission_date'
};

frappe.call({ method: 'frappe.client.get_list',
    args: { doctype: CHB_CONFIG.doctype, limit: CHB_CONFIG.max_rows } });
```

---

### Rule 8 — Permission-Aware Rendering

**A CHB that renders data the current user cannot read will show blank or throw a 403.**
Do not assume admin-level access at build time.

```javascript
// ✅ Check role before rendering sensitive widgets
if (frappe.user.has_role(['System Manager', 'Grants Manager'])) {
    _el('finance-section').style.display = '';
    loadFinanceData();
} else {
    _el('finance-section').style.display = 'none';
}

// ✅ Handle 403 from frappe.call explicitly inside frappeCallPromise
function frappeCallPromise(method, args) {
    return new Promise((resolve, reject) => {
        frappe.call({
            method: method,
            args: args || {},
            callback: r => resolve(r.message),
            error: (xhr) => {
                if (xhr.status === 403) reject(new Error('permission'));
                else reject(new Error('network'));
            }
        });
    });
}

// Differentiate permission failures from network failures in .catch()
.catch(err => {
    if (err.message === 'permission') showError('You do not have access to this data.');
    else showError('Failed to load. Refresh to retry.');
});
```

---

### Rule 9 — Shared Dependencies Must Use `frappe.provide`, Never `window.*`

**If a CHB calls any function defined outside the CHB itself (shared formatters, API
wrappers, common filters), that function must be namespaced via `frappe.provide` in a
bundle — never attached to `window` directly.**

Claude and Cursor both default to `window.my_fn = function(){}` for shared logic. This
pattern works but pollutes the global namespace, triggers ESLint `"not defined"` warnings
in consuming files, and forces defensive guard checks everywhere.

```javascript
// ❌ BANNED — shared helper on window, requires guard checks in every CHB
window.formatGrantAmount = function(val) { ... };

// In CHB script — guard check required everywhere, fragile
window.formatGrantAmount && window.formatGrantAmount(val);
```

```javascript
// ✅ REQUIRED — declare shared logic in a bundle using frappe.provide

// shared/grant_utils.bundle.js  (in your app's public/ folder, included via hooks.py)
frappe.provide("dhwani.grant_utils");

dhwani.grant_utils.formatAmount = function(val) {
    return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(val);
};

dhwani.grant_utils.getStatusColor = function(status) {
    return { Approved: '#22c55e', Rejected: '#ef4444', Pending: '#f59e0b' }[status] || '#6b7280';
};
```

```javascript
// In CHB script — clean, no guards needed
var amt = dhwani.grant_utils.formatAmount(row.amount);
```

**How `frappe.provide` works — why it is safe:**

```javascript
// frappe.provide("dhwani.grant_utils") is equivalent to:
window.dhwani = window.dhwani || {};
dhwani.grant_utils = dhwani.grant_utils || {};
// Safe: never overwrites an existing namespace
```

**This rule applies only to functions defined OUTSIDE the CHB IIFE.** Helpers defined
inside the IIFE (`frappeCallPromise`, `showError`, `CHB_CONFIG`) are already scoped
correctly and do not need `frappe.provide`.

**Bundle inclusion checklist — before a CHB can depend on a shared namespace:**
1. Bundle file exists in `your_app/public/js/`
2. Bundle is listed in `hooks.py` under `app_include_js`
3. Namespace is verifiable in browser console: `typeof dhwani.grant_utils === 'object'`
4. CHB script does NOT contain `window.` prefix for any shared function call

---

### Scale NFR Additions to Pre-Flight Checklist (extend §8)

Add these checks to `verify_chb_deployment()`:

```python
import re

# Append to results dict in verify_chb_deployment():
results["no hardcoded array literals outside callback"] = not bool(
    re.search(r'datasets\s*:\s*\[\s*\{', script.split('callback')[0])
)
results["uses Promise.all or single frappe.call"] = (
    "Promise.all" in script or script.count("frappe.call(") <= 1
)
results["has error boundary (showError or state-error)"] = (
    "showError" in script or "state-error" in script
)
results["has explicit limit in get_list"] = (
    "get_list" not in script or "limit" in script
)
results["has CHB_CONFIG block"] = (
    "CHB_CONFIG" in script
)
results["no window.* shared function calls"] = (
    "window." not in script or
    all(ref in ["window.my_app", "window.dhwani"]  # known namespaces — extend as needed
        for ref in re.findall(r'window\.\w+', script))
)
```

---

### Scale NFR Summary

| # | Rule | Failure mode if skipped | Enforced by |
|---|---|---|---|
| 1 | No hardcoded data | Dashboard never reflects real data | Checklist regex |
| 2 | Parallel calls via `Promise.all` | 2–5s blank screen on load | Checklist call count |
| 3 | Loading state + error boundary | Blank = broken, indistinguishable | Checklist string check |
| 4 | Memory leak cleanup | Degrades on each workspace revisit | Code review |
| 5 | DOM batching | Visible jank at 20+ rows | Code review |
| 6 | Hard row limit on queries | Browser lock on production data | Checklist + `CHB_CONFIG.max_rows` |
| 7 | `CHB_CONFIG` block, no scattered literals | Breaks on staging/prod/client switch | Checklist |
| 8 | Permission-aware rendering | Silent 403 blank for restricted users | Code review |
| 9 | Shared deps via `frappe.provide`, not `window.*` | ESLint errors, guard checks everywhere, namespace collisions | Checklist regex |
