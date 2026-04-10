# Frappe v16 Deployment — Working Code Templates

> Read this file when SKILL.md §17 directs you here.
> Contains: Template A (CHB + Workspace), Template B (Page, developer_mode ON),
> Template C (Web Page with frappe.call shim), Template D (shared bundle via frappe.provide).

---

## Table of Contents

1. [Template A — Custom HTML Block + Workspace (developer_mode OFF)](#template-a)
2. [Template B — Page Deployment (developer_mode ON)](#template-b)
3. [Template C — Web Page with frappe.call Shim](#template-c)
4. [Template D — Shared Bundle via frappe.provide](#template-d)

---

## Template A — Custom HTML Block + Workspace (developer_mode OFF) {#template-a}

**Safest deployment path when developer_mode is OFF.**
The CHB script, style, and html fields ARE stored in the database — no filesystem access needed.

```python
import requests, json

BASE = "https://your-site.example.com"
HDR  = {"Authorization": "token API_KEY:API_SECRET"}

# ── Step 1: Define three fields separately — NEVER put <style>/<script> in html field ──
dashboard_html = """
<div id="root">
    <div id="state-loading">
        <div class="skeleton-bar"></div>
        <div class="skeleton-bar short"></div>
    </div>
    <div id="state-error" style="display:none"></div>
    <div id="state-content" style="display:none">
        <div id="kpi-row" class="kpi-row"></div>
        <div id="chart-container"></div>
    </div>
</div>
"""

dashboard_style = """
:host { display: block; width: 100%; box-sizing: border-box; }
#root { padding: 20px; font-family: Inter, -apple-system, sans-serif; }
.skeleton-bar { height: 18px; background: #e5e7eb; border-radius: 4px;
    margin: 10px 0; animation: shimmer 1.4s infinite; width: 100%; }
.skeleton-bar.short { width: 60%; }
@keyframes shimmer { 0%,100%{opacity:1} 50%{opacity:0.4} }
#state-error { padding: 16px; border-radius: 6px; background: #fef2f2;
    color: #991b1b; font-size: 13px; border: 1px solid #fecaca; }
.kpi-row { display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 24px; }
.kpi-card { flex: 1; min-width: 160px; background: #fff;
    border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px; }
.kpi-label { font-size: 12px; color: #6b7280; text-transform: uppercase; }
.kpi-value { font-size: 28px; font-weight: 600; color: #111827; margin-top: 4px; }
"""

dashboard_script = """
(function() {
    // ── Shadow DOM helpers — root_element auto-injected by Frappe ──────────
    function _q(sel)  { return root_element.querySelector(sel); }
    function _el(id)  { return root_element.querySelector('#' + id); }

    // ── Config — all literals here only ────────────────────────────────────
    var CHB_CONFIG = {
        doctype:  'Your DocType',   // ← change
        max_rows: 500
    };

    // ── State helpers ───────────────────────────────────────────────────────
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

    // ── Parallel call helper ────────────────────────────────────────────────
    function frappeCallPromise(method, args) {
        return new Promise(function(resolve, reject) {
            frappe.call({
                method: method,
                args: args || {},
                callback: function(r) { resolve(r.message); },
                error: function(xhr) {
                    reject(new Error(xhr.status === 403 ? 'permission' : 'network'));
                }
            });
        });
    }

    // ── Main ────────────────────────────────────────────────────────────────
    showLoading();

    Promise.all([
        frappeCallPromise('frappe.client.get_list', {
            doctype: CHB_CONFIG.doctype,
            fields: ['name', 'status', 'amount'],
            limit: CHB_CONFIG.max_rows,
            order_by: 'modified desc'
        })
    ]).then(function(results) {
        var rows = results[0] || [];
        var kpiHtml = '<div class="kpi-card">'
            + '<div class="kpi-label">Total</div>'
            + '<div class="kpi-value">' + rows.length + '</div>'
            + '</div>';
        _el('kpi-row').innerHTML = kpiHtml;
        showContent();
    }).catch(function(err) {
        if (err.message === 'permission')
            showError('You do not have access to this data.');
        else
            showError();
    });
})();
"""

# ── Step 2: Create/Update the CHB ──────────────────────────────────────────
block_name = "my-dashboard-chb"   # ← change; must match workspace wiring below

resp = requests.put(f"{BASE}/api/resource/Custom HTML Block/{block_name}",
    headers={**HDR, "Content-Type": "application/json"},
    json={"html": dashboard_html, "style": dashboard_style, "script": dashboard_script})

if resp.status_code == 404:
    resp = requests.post(f"{BASE}/api/resource/Custom HTML Block",
        headers={**HDR, "Content-Type": "application/json"},
        json={"doctype": "Custom HTML Block", "name": block_name,
              "html": dashboard_html, "style": dashboard_style,
              "script": dashboard_script, "private": 0})

print(f"CHB: {resp.status_code}")

# ── Step 3: Verify all three fields persisted ───────────────────────────────
verify = requests.get(f"{BASE}/api/resource/Custom HTML Block/{block_name}", headers=HDR)
d = verify.json()['data']
assert d.get('script'), "WARNING: script field is empty!"
assert d.get('style'),  "WARNING: style field is empty!"
print(f"html={len(d['html'])} style={len(d['style'])} script={len(d['script'])} chars")

# ── Step 4: Wire to workspace — MUST sync content JSON + custom_blocks ──────
ws_name = "my-workspace"   # ← change

# Get current workspace to preserve existing blocks
rv = requests.get(f"{BASE}/api/resource/Workspace/{requests.utils.quote(ws_name)}", headers=HDR)
existing = rv.json().get("data", {})
existing_cb = existing.get("custom_blocks", [])

# Build content blocks (append to any existing blocks)
existing_content = json.loads(existing.get("content", "[]"))
new_block = {"id": ws_name[:8]+"-cb1", "type": "custom_block",
             "data": {"custom_block_name": block_name, "col": 12}}
# Avoid duplicates
existing_content = [b for b in existing_content
                    if b.get("data",{}).get("custom_block_name") != block_name]
existing_content.append(new_block)

# Reuse existing child row if present, else create new
target_cb = next((c for c in existing_cb if c.get("custom_block_name") == block_name), None)
if target_cb:
    cb_row = {**target_cb, "label": block_name}
else:
    cb_row = {"custom_block_name": block_name, "label": block_name,
              "parentfield": "custom_blocks", "parenttype": "Workspace",
              "doctype": "Workspace Custom Block"}

other_cbs = [c for c in existing_cb if c.get("custom_block_name") != block_name]

resp2 = requests.put(
    f"{BASE}/api/resource/Workspace/{requests.utils.quote(ws_name)}",
    headers={**HDR, "Content-Type": "application/json"},
    json={"content": json.dumps(existing_content),
          "custom_blocks": other_cbs + [cb_row]})
print(f"Workspace: {resp2.status_code}")

# ── Step 5: Verify content + child table in sync ────────────────────────────
rv2 = requests.get(f"{BASE}/api/resource/Workspace/{requests.utils.quote(ws_name)}", headers=HDR)
d2 = rv2.json()['data']
content_chbs = [b['data']['custom_block_name'] for b in json.loads(d2['content'])
                if b.get('type') == 'custom_block']
table_chbs   = [c['custom_block_name'] for c in d2.get('custom_blocks', [])]
print(f"Content: {content_chbs} | Table: {table_chbs}")
assert set(content_chbs) == set(table_chbs), "OUT OF SYNC — blank page will result!"
print(f"✅ Access at: {BASE}/app/{ws_name}")
```

---

## Template B — Page Deployment (developer_mode ON) {#template-b}

**Use only when `developer_mode = 1` on the target instance.**
Page JS/CSS is stored on the filesystem — without developer_mode it will appear to succeed
but the script will not persist (see §1 and §2 of SKILL.md).

```python
import requests

BASE = "https://your-site.example.com"
HDR  = {"Authorization": "token API_KEY:API_SECRET", "Content-Type": "application/json"}

page_name  = "my-dashboard"
page_title = "My Dashboard"

# ── Step 0: Confirm developer_mode is ON ───────────────────────────────────
conf = requests.get(f"{BASE}/api/method/frappe.client.get_value",
    headers=HDR,
    params={"doctype": "System Settings", "fieldname": "developer_mode"})
if not conf.json().get("message", {}).get("developer_mode"):
    raise RuntimeError("developer_mode is OFF — use Template A (CHB) instead")

# ── Step 1: Create Page ────────────────────────────────────────────────────
resp = requests.post(f"{BASE}/api/resource/Page",
    headers=HDR,
    json={"doctype": "Page", "page_name": page_name,
          "title": page_title, "module": "Custom", "standard": "No"})
print(f"Create: {resp.status_code}")

# ── Step 2: Set JS (frappe.Chart, frappe.call, jQuery all available) ───────
js_code = f"""
frappe.pages['{page_name}'].on_page_load = function(wrapper) {{
    var page = frappe.ui.make_app_page({{
        parent: wrapper,
        title: '{page_title}',
        single_column: true
    }});

    frappe.call({{
        method: 'frappe.client.get_list',
        args: {{ doctype: 'Your DocType', fields: ['name'], limit_page_length: 20 }},
        callback: function(r) {{
            $(page.body).html('<h2>' + (r.message || []).length + ' records</h2>');
        }}
    }});
}};
"""

resp2 = requests.put(f"{BASE}/api/resource/Page/{page_name}",
    headers=HDR,
    json={"script": js_code, "style": "/* styles here */"})
print(f"Deploy: {resp2.status_code}")

# ── Step 3: Verify JS persisted ────────────────────────────────────────────
verify = requests.get(f"{BASE}/api/resource/Page/{page_name}", headers=HDR)
stored = verify.json()['data'].get('script', '')
if len(stored) < 10:
    print("⚠ WARNING: Script did not persist — developer_mode may be OFF!")
else:
    print(f"✅ Script persisted ({len(stored)} chars)")
    print(f"Access at: {BASE}/app/{page_name}")
```

---

## Template C — Web Page with frappe.call Shim {#template-c}

**Use when developer_mode is OFF and desk context is NOT needed.**
Web Pages load `frappe-web.bundle.js` — `frappe.Chart` and `frappe.call` are NOT available
natively. The shim below recreates `frappe.call` as a fetch wrapper.

> **Note:** `window.frappe = {}` here is an intentional polyfill — NOT a `window.*`
> namespace violation. It recreates the object that desk.bundle.js would normally provide.

```python
import requests

BASE = "https://your-site.example.com"
HDR  = {"Authorization": "token API_KEY:API_SECRET"}

html_content = """
<style>
  body { margin: 0; font-family: Inter, sans-serif; background: #f8fafc; }
  .dash { max-width: 1200px; margin: 0 auto; padding: 24px; }
  .web-footer, footer, .page-header-wrapper { display: none !important; }
</style>
<div class="dash" id="app-root">
  <p>Loading...</p>
</div>
<script>
// ── frappe.call shim — web context only ────────────────────────────────────
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
        .catch(function(e) {
            console.error('API error:', e);
            if (opts.error) opts.error(e);
        });
    };
}

// ── Dashboard code — NO frappe.Chart here (use Chart.js or inline SVG) ─────
frappe.call({
    method: 'frappe.client.get_list',
    args: { doctype: 'Your DocType', fields: ['name', 'title'], limit_page_length: 20 },
    callback: function(r) {
        var root = document.getElementById('app-root');
        root.innerHTML = '<h2>' + (r.message ? r.message.length : 0) + ' records</h2>';
    }
});
</script>
"""

resp = requests.post(f"{BASE}/api/resource/Web Page",
    headers={**HDR, "Content-Type": "application/json"},
    json={
        "doctype": "Web Page",
        "title": "My Dashboard",
        "route": "my-dashboard-view",
        "content_type": "HTML",
        "main_section_html": html_content,   # v15+ field name
        "published": 1,
        "full_width": 1,
        "show_title": 0
    })
print(f"Web Page: {resp.status_code}")
print(f"Access at: {BASE}/my-dashboard-view")
```

---

## Template D — Shared Bundle via frappe.provide {#template-d}

**Use when logic is shared across two or more deployment targets.**
See §4 of SKILL.md for the full rationale on why `window.*` breaks cross-context.

```javascript
// ── File: your_app/public/js/shared_utils.bundle.js ──────────────────────
frappe.provide("myapp.utils");

myapp.utils.formatCurrency = function(val, currency) {
    currency = currency || 'INR';
    return new Intl.NumberFormat('en-IN', {
        style: 'currency', currency: currency
    }).format(val || 0);
};

myapp.utils.getStatusColor = function(status) {
    var map = {
        'Approved':  '#22c55e',
        'Rejected':  '#ef4444',
        'Pending':   '#f59e0b',
        'Draft':     '#6b7280'
    };
    return map[status] || '#6b7280';
};

myapp.utils.frappeCallPromise = function(method, args) {
    return new Promise(function(resolve, reject) {
        frappe.call({
            method: method,
            args: args || {},
            callback: function(r) { resolve(r.message); },
            error: function(xhr) {
                reject(new Error(xhr.status === 403 ? 'permission' : 'network'));
            }
        });
    });
};
```

```python
# ── hooks.py — load the bundle in every desk page ─────────────────────────
app_include_js = [
    "/assets/your_app/js/shared_utils.bundle.js"
]
```

```javascript
// ── Usage in any CHB script, Client Script, or Desk Page ─────────────────
// No guard checks needed. No window.* pollution.
var color = myapp.utils.getStatusColor(row.status);
var amt   = myapp.utils.formatCurrency(row.amount);

myapp.utils.frappeCallPromise('myapp.api.get_summary')
    .then(function(data) { renderDashboard(data); })
    .catch(function(err) { showError(err.message); });
```

```bash
# ── After adding the bundle file, run bench build ─────────────────────────
bench build --app your_app
# Then clear cache:
bench --site your-site.example.com clear-cache
```
