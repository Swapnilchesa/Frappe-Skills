# CHB Reference — Complete Code Templates

> Read this file when SKILL.md directs you here.
> Contains: standard IIFE template, frappeCallPromise helper, full verify_chb_deployment(),
> workspace wiring script, frappe.Chart examples, and Scale NFR boilerplate.

---

## Table of Contents

1. [Standard CHB IIFE Template (production-ready)](#1-iife-template)
2. [frappeCallPromise — Standard Parallel Call Helper](#2-frappecallpromise)
3. [Three-State HTML Boilerplate (loading / error / content)](#3-three-state)
4. [Full verify_chb_deployment() Function](#4-verify)
5. [Complete Workspace Creation + Wiring Script](#5-wiring)
6. [frappe.Chart Examples](#6-charts)
7. [Memory Leak Cleanup Pattern](#7-memory-leak)

---

## 1. Standard CHB IIFE Template (production-ready) {#1-iife-template}

Copy this as the starting point for every new CHB. It satisfies all §8 checklist rules
and all §11 Scale NFRs out of the box.

```python
chb_doc = {
    "name": "my-dashboard-chb",        # ← change this
    "private": 0,

    # ── HTML — structural markup only, no <style> or <script> ──────────────
    "html": """
<div id="root">
    <div id="state-loading">
        <div class="skeleton-bar"></div>
        <div class="skeleton-bar short"></div>
        <div class="skeleton-bar"></div>
    </div>
    <div id="state-error" style="display:none"></div>
    <div id="state-content" style="display:none">
        <!-- dashboard markup here -->
        <div id="kpi-row" class="kpi-row"></div>
        <div id="chart-container"></div>
    </div>
</div>
""",

    # ── STYLE — scoped to shadow DOM via :host ──────────────────────────────
    "style": """
:host { display: block; width: 100%; box-sizing: border-box; }
#root  { padding: 20px; font-family: Inter, -apple-system, sans-serif; }

/* Skeleton loading */
.skeleton-bar {
    height: 18px; background: #e5e7eb; border-radius: 4px;
    margin: 10px 0; animation: shimmer 1.4s infinite; width: 100%;
}
.skeleton-bar.short { width: 60%; }
@keyframes shimmer { 0%,100%{opacity:1} 50%{opacity:0.4} }

/* Error state */
#state-error {
    padding: 16px; border-radius: 6px;
    background: #fef2f2; color: #991b1b;
    font-size: 13px; border: 1px solid #fecaca;
}

/* KPI row */
.kpi-row  { display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 24px; }
.kpi-card {
    flex: 1; min-width: 160px; background: #fff;
    border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px;
}
.kpi-label { font-size: 12px; color: #6b7280; text-transform: uppercase; }
.kpi-value { font-size: 28px; font-weight: 600; color: #111827; margin-top: 4px; }
""",

    # ── SCRIPT — wrapped in IIFE, root_element auto-injected by Frappe ──────
    "script": """
(function() {

// ── Config — all instance-specific values here, nowhere else ──────────────
var CHB_CONFIG = {
    doctype:    'Grant Application',        // ← change to your doctype
    report:     'Monthly Grant Summary',    // ← change or remove
    max_rows:   500,
    date_field: 'submission_date'
};

// ── Shadow DOM helpers ─────────────────────────────────────────────────────
function _q(sel)  { return root_element.querySelector(sel); }
function _el(id)  { return root_element.querySelector('#' + id); }

// ── State transitions ──────────────────────────────────────────────────────
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

// ── Parallel call helper (see §2 below) ───────────────────────────────────
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

// ── Main load ──────────────────────────────────────────────────────────────
function loadDashboard() {
    showLoading();

    Promise.all([
        frappeCallPromise('frappe.client.get_list', {
            doctype: CHB_CONFIG.doctype,
            fields: ['name', 'status', 'amount'],
            limit: CHB_CONFIG.max_rows,
            order_by: 'modified desc'
        })
        // add more parallel calls here
    ]).then(function(results) {
        var records = results[0] || [];
        renderKPIs(records);
        renderChart(records);
        if (records.length === CHB_CONFIG.max_rows) {
            _el('state-content').insertAdjacentHTML('beforeend',
                '<p style="font-size:12px;color:#6b7280">Showing top ' +
                CHB_CONFIG.max_rows + ' records</p>');
        }
        showContent();
    }).catch(function(err) {
        if (err.message === 'permission')
            showError('You do not have access to this data.');
        else
            showError();
        console.error('CHB load error:', err);
    });
}

function renderKPIs(records) {
    var total = records.reduce(function(s, r) { return s + (r.amount || 0); }, 0);
    var approved = records.filter(function(r) { return r.status === 'Approved'; }).length;
    var html = [
        kpiCard('Total Records', records.length),
        kpiCard('Approved', approved),
        kpiCard('Total Amount', frappe.format(total, { fieldtype: 'Currency' }))
    ].join('');
    _el('kpi-row').innerHTML = html;
}

function kpiCard(label, value) {
    return '<div class="kpi-card"><div class="kpi-label">' +
        frappe.utils.escape_html(String(label)) + '</div><div class="kpi-value">' +
        frappe.utils.escape_html(String(value)) + '</div></div>';
}

function renderChart(records) {
    var statusCounts = {};
    records.forEach(function(r) {
        statusCounts[r.status] = (statusCounts[r.status] || 0) + 1;
    });
    var labels = Object.keys(statusCounts);
    var values = labels.map(function(l) { return statusCounts[l]; });

    new frappe.Chart(_el('chart-container'), {
        type: 'donut',
        height: 240,
        data: { labels: labels, datasets: [{ values: values }] },
        colors: ['#66C2A5', '#FC8D62', '#8DA0CB', '#E78AC3'],
        tooltipOptions: {
            formatTooltipY: function(d) {
                return new Intl.NumberFormat('en-IN').format(d);
            }
        }
    });
}

// ── Boot ───────────────────────────────────────────────────────────────────
loadDashboard();

})();
"""
}
```

---

## 2. frappeCallPromise — Standard Parallel Call Helper {#2-frappecallpromise}

Copy verbatim. Do not rewrite per dashboard.

```javascript
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
```

Usage with Promise.all:

```javascript
Promise.all([
    frappeCallPromise('myapp.api.get_summary'),
    frappeCallPromise('frappe.client.get_list', {
        doctype: CHB_CONFIG.doctype,
        fields: ['name', 'status'],
        limit: CHB_CONFIG.max_rows
    })
]).then(function([summary, list]) {
    render(summary, list);
}).catch(function(err) {
    if (err.message === 'permission') showError('You do not have access.');
    else showError();
});
```

---

## 3. Three-State HTML Boilerplate {#3-three-state}

Minimum required HTML structure for every production CHB:

```html
<div id="root">
    <div id="state-loading">
        <div class="skeleton-bar"></div>
        <div class="skeleton-bar short"></div>
        <div class="skeleton-bar"></div>
    </div>
    <div id="state-error" style="display:none"></div>
    <div id="state-content" style="display:none">
        <!-- your actual dashboard markup here -->
    </div>
</div>
```

Matching CSS (paste into `style` field):

```css
.skeleton-bar {
    height: 18px; background: #e5e7eb; border-radius: 4px;
    margin: 10px 0; animation: shimmer 1.4s infinite; width: 100%;
}
.skeleton-bar.short { width: 60%; }
@keyframes shimmer { 0%,100%{opacity:1} 50%{opacity:0.4} }
#state-error {
    padding: 16px; border-radius: 6px;
    background: #fef2f2; color: #991b1b;
    font-size: 13px; border: 1px solid #fecaca;
}
```

---

## 4. Full verify_chb_deployment() Function {#4-verify}

Complete version including all §8 checklist + §11 Scale NFR extensions:

```python
import re, requests, json

def verify_chb_deployment(base, hdr, chb_name, ws_name):
    results = {}

    # ── 1. CHB field checks ────────────────────────────────────────────────
    r = requests.get(f"{base}/api/resource/Custom HTML Block/{chb_name}", headers=hdr)
    chb = r.json().get("data", {})
    script = chb.get("script", "") or ""
    style  = chb.get("style",  "") or ""
    html   = chb.get("html",   "") or ""

    # Deployment basics
    results["script_len > 100"]     = len(script) > 100
    results["style_len > 0"]        = len(style) > 0
    results["html has mount div"]   = len(html) > 10
    results["no document.getElementById"] = "document.getElementById(" not in script
    results["no root_element.getElementById"] = "root_element.getElementById" not in script
    results["root_element used"]    = "root_element" in script
    results["no external CDN"]      = "cdnjs" not in script and "jsdelivr" not in script
    results["wrapped in IIFE"]      = script.strip().startswith("(function()")

    # Scale NFRs (§11)
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
    results["has CHB_CONFIG block"] = "CHB_CONFIG" in script
    results["no window.* shared function calls"] = (
        "window." not in script or
        all(ref in ["window.my_app", "window.dhwani"]
            for ref in re.findall(r'window\.\w+', script))
    )

    # ── 2. Workspace label match ───────────────────────────────────────────
    rv = requests.get(f"{base}/api/method/frappe.desk.desktop.get_desktop_page",
        headers=hdr,
        params={"page": json.dumps({"name": ws_name, "title": ws_name, "public": 1})})
    items = rv.json().get("message", {}).get("custom_blocks", {}).get("items", [])
    target = next((i for i in items if i.get("custom_block_name") == chb_name), None)
    results["chb in page_data"]  = target is not None
    results["label == chb_name"] = target is not None and target.get("label") == chb_name

    # ── 3. Print results ───────────────────────────────────────────────────
    all_pass = all(results.values())
    for check, ok in results.items():
        print(f"  {'✅' if ok else '❌'} {check}")
    print(f"\n{'✅ READY' if all_pass else '❌ BLOCKED — fix above before testing in browser'}")
    return all_pass
```

---

## 5. Complete Workspace Creation + Wiring Script {#5-wiring}

```python
import json, requests

BASE = "https://your-site.example.com"     # ← change
HDR  = {"Authorization": "token KEY:SECRET", "Content-Type": "application/json"}

def get_module_name(base, hdr):
    """Never hardcode module — derive from an existing workspace."""
    r = requests.get(f"{base}/api/resource/Workspace?limit=1", headers=hdr)
    return r.json()["data"][0]["module"]

def create_chb(base, hdr, chb_name, html, style, script):
    """Create or overwrite a Custom HTML Block."""
    payload = {
        "doctype": "Custom HTML Block",
        "name": chb_name,
        "html": html,
        "style": style,
        "script": script,
        "private": 0
    }
    # Try PUT first (update), fall back to POST (create)
    r = requests.put(f"{base}/api/resource/Custom HTML Block/{chb_name}",
        headers=hdr, json=payload)
    if r.status_code == 404:
        r = requests.post(f"{base}/api/resource/Custom HTML Block",
            headers=hdr, json=payload)
    r.raise_for_status()
    print(f"✅ CHB saved: {chb_name}")
    return r.json()

def create_workspace(base, hdr, ws_name, chb_name):
    """Create workspace and wire CHB in one atomic PUT."""
    MODULE_NAME = get_module_name(base, hdr)

    content_blocks = [
        {"id": ws_name[:8] + "-h1", "type": "header",
         "data": {"text": f"<span class='h4'><b>{ws_name}</b></span>", "col": 12}},
        {"id": ws_name[:8] + "-cb1", "type": "custom_block",
         "data": {"custom_block_name": chb_name, "col": 12}}
    ]
    cb_row = {
        "custom_block_name": chb_name,
        "label": chb_name,          # ← MUST equal custom_block_name
        "parentfield": "custom_blocks",
        "parenttype": "Workspace",
        "doctype": "Workspace Custom Block"
    }
    ws_payload = {
        "name": ws_name, "label": ws_name, "title": ws_name,
        "module": MODULE_NAME,
        "for_user": "", "parent_page": "",
        "sequence_id": 57.0, "is_hidden": 0, "public": 1,
        "content": json.dumps(content_blocks),
        "custom_blocks": [cb_row]
    }
    r = requests.put(
        f"{base}/api/resource/Workspace/{requests.utils.quote(ws_name)}",
        headers=hdr, json=ws_payload)
    if r.status_code == 404:
        r = requests.post(f"{base}/api/resource/Workspace",
            headers=hdr, json=ws_payload)
    r.raise_for_status()

    # Verify label sync
    rv = requests.get(f"{base}/api/method/frappe.desk.desktop.get_desktop_page",
        headers=hdr,
        params={"page": json.dumps({"name": ws_name, "title": ws_name, "public": 1})})
    items = rv.json().get("message", {}).get("custom_blocks", {}).get("items", [])
    for item in items:
        assert item["label"] == item["custom_block_name"], \
            f"LABEL MISMATCH: {item['label']} != {item['custom_block_name']}"
    print(f"✅ Workspace wired and verified: {chb_name} → {ws_name}")
```

---

## 6. frappe.Chart Examples {#6-charts}

All examples use API-driven data (no hardcoded values). Pass DOM element directly.

```javascript
// Bar chart
new frappe.Chart(_el('chart-bar'), {
    type: 'bar', height: 280,
    data: { labels: data.map(d => d.label), datasets: [{ values: data.map(d => d.count) }] },
    colors: ['#66C2A5'],
    tooltipOptions: { formatTooltipY: d => new Intl.NumberFormat('en-IN').format(d) }
});

// Line chart (time series)
new frappe.Chart(_el('chart-line'), {
    type: 'line', height: 240,
    data: { labels: data.map(d => d.month), datasets: [{ values: data.map(d => d.total) }] },
    lineOptions: { regionFill: 1 },
    colors: ['#8DA0CB']
});

// Donut chart
new frappe.Chart(_el('chart-donut'), {
    type: 'donut', height: 200,
    data: { labels: data.map(d => d.status), datasets: [{ values: data.map(d => d.count) }] },
    colors: ['#66C2A5', '#FC8D62', '#8DA0CB', '#E78AC3']
});
```

**Note:** `frappe.Chart` does NOT support horizontal bar charts. For horizontal bars,
inline Chart.js UMD (see SKILL.md §6 Option B).

---

## 7. Memory Leak Cleanup Pattern {#7-memory-leak}

Use when the CHB has `setInterval` or `window`/`document` event listeners:

```javascript
// At top of IIFE — declare timer handle
var _refreshTimer = null;

function startAutoRefresh(intervalMs) {
    if (_refreshTimer) clearInterval(_refreshTimer);
    _refreshTimer = setInterval(loadDashboard, intervalMs || 30000);
}

// MutationObserver unmount guard (Frappe has no CHB destroy hook)
var _hostEl = root_element.host;
var _observer = new MutationObserver(function() {
    if (!document.contains(_hostEl)) {
        clearInterval(_refreshTimer);
        _observer.disconnect();
    }
});
_observer.observe(document.body, { childList: true, subtree: true });

// Boot with auto-refresh
loadDashboard();
startAutoRefresh(30000);
```
