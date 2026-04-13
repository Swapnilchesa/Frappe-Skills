---
name: frappe-reports
description: >
  Build, deploy, debug, and iterate on custom Script Reports in Frappe v15/v16 via the REST API
  — without SSH or bench access. Use this skill whenever: building a new Frappe report, deploying
  a Script Report to a Frappe instance, debugging a report that shows no filter bar or blank data,
  wiring a report into a workspace sidebar, writing Python scripts for Frappe's safe_exec sandbox,
  or troubleshooting any query_report.js issue. ALWAYS use this skill before writing any report
  code — the safe_exec contract, get_script disk-vs-DB behaviour, and filter storage rules are
  completely non-obvious and caused repeated failures without it. Apply to any request involving
  "build a report", "Frappe report", "Script Report", "query report", or "custom report".
  Cross-references: frappe-build (for general deployment), frappe-design (for DocType specs and visual design).
---

# Frappe Custom Script Reports — Build & Deploy Skill

**This skill is a binding contract built from a real deployment session on Frappe v16-dev.**
Every rule maps to a real failure. Read it fully before writing a single line of report code.

---

## Table of Contents

1. [Architecture — How Script Reports Actually Work](#1-architecture)
2. [safe_exec Contract — Python Sandbox Rules](#2-safe-exec) ← **Most common failure source**
3. [SQL Injection — Semgrep Blocking Rules](#3-sql-injection) ← **Pre-commit will block your PR**
4. [Translations — Wrap All User-Facing Text](#4-translations) ← **Required for i18n compliance**
5. [get_script — Disk File vs DB Field](#5-get-script) ← **Why your JS never loads**
6. [Filter Storage — Child Table, Not JS](#6-filters) ← **Why filter bar is blank**
7. [Column Storage — Child Table, Not Script](#7-columns)
8. [Workspace Wiring — Shortcut Block Rules](#8-workspace)
9. [Deployment Checklist — Step by Step](#9-checklist)
10. [Debugging Protocol — Blank Screen Triage](#10-debug)
11. [Post-Mortem — Every Mistake Made](#11-postmortem)
12. [Complete Working Templates](#12-templates)

---

## 1. Architecture — How Script Reports Actually Work {#1-architecture}

```
Browser
  │
  ├── GET /api/method/frappe.desk.query_report.get_script?report_name=X
  │     └── Returns: JS from DISK FILE (apps/app_name/.../report_name.js)
  │           Falls back to: DB report.javascript field ONLY if no disk file
  │
  ├── GET /api/resource/Report/X
  │     └── Returns: report.filters[] (child table) → drives filter bar
  │                  report.columns[] (child table) → drives column headers
  │
  └── POST /api/method/frappe.desk.query_report.run
        └── Runs: DB report.report_script via safe_exec sandbox
                  Reads: 'result' variable from sandbox locals
                  Reads: report.columns[] child table for column headers
```

**Key insight:** Three completely separate storage locations. Script = DB. JS = disk file. Columns/Filters = child tables. Confuse any of these and you get a blank report.

---

## 2. safe_exec Contract — Python Sandbox Rules {#2-safe-exec}

Frappe v16 runs `report_script` through **RestrictedPython**. This is not standard Python.
Violating any rule silently produces `result: null` or a `SyntaxError`/`ImportError` with 0 rows.

### ✅ ALLOWED

```python
# frappe is pre-injected — use it directly
season = (filters or {}).get("season_calendar") or ""

# frappe.db.sql — fully available
rows = frappe.db.sql("SELECT name FROM `tabFarmer Registration` LIMIT 5", as_dict=True)

# Plain dict literals and list comprehensions
result = [{"farmer_id": r.farmer_id} for r in rows]

# Dot access on SQL as_dict=True rows
name = rows[0].farmer_name

# String concatenation
full = first + " " + last

# Standard builtins: list, dict, str, int, len, set, sorted, enumerate, zip
farmer_links = list(set([r.farmer_link for r in crop_rows if r.farmer_link]))

# Conditional expressions
status = "Approved" if fr.get("docstatus") == 1 else "Pending"

# for loops, if/else, while
for cr in crop_rows:
    result.append({"key": cr.value})
```

### ❌ BLOCKED — will produce SyntaxError or silent failure

```python
import frappe          # ❌ ImportError: __import__ not found
import os              # ❌ same
from frappe import _   # ❌ same

frappe._dict()         # ❌ SyntaxError: "_dict" is invalid (underscore prefix)
frappe._dict           # ❌ same
_result = fn()         # ❌ SyntaxError: "_result" is invalid
__any_var__            # ❌ SyntaxError: double underscore

columns, data = fn()   # ❌ _unpack_sequence_ not defined
a, b = (1, 2)          # ❌ same — tuple unpacking blocked

return columns, data   # ❌ execute() return value is IGNORED by safe_exec

open("/path")          # ❌ open() not defined
os.path.join(...)      # ❌ no os module
frappe.utils           # ❌ AttributeError: module has no attribute 'utils'
frappe.get_app_path()  # ❌ AttributeError
frappe.cache()         # ❌ AttributeError
```

### The single most important safe_exec rule

**Rows must be assigned to `result` variable. Columns come from the child table. `execute()` return value is ignored.**

```python
# CORRECT safe_exec pattern
season = (filters or {}).get("season_calendar") or ""

if not season:
    result = []          # ← silent empty return, NOT frappe.throw()
else:
    rows = frappe.db.sql("...", {"s": season}, as_dict=True)
    result = []
    for r in rows:
        result.append({
            "farmer_id": r.farmer_id or "",
            "farmer_name": r.farmer_name or "",
        })
# No return statement needed. Frappe reads 'result' from locals.
```

### Why `frappe.throw()` is wrong for empty filter guard

`frappe.throw()` fires on **page load** before the user can interact with filters. Frappe runs the script immediately when the report page opens with empty filters. Always use a silent `result = []` instead.

---

## 3. SQL Injection — Semgrep Blocking Rules {#3-sql-injection}

**Pre-commit enforces `frappe-semgrep-rules.rules.security.frappe-sql-format-injection` — this is a blocking check. Any violation will stop your PR.**

The rule detects `.format()` or f-strings used inside a `frappe.db.sql()` call. This applies to the entire string passed, including concatenated parts.

### ❌ BLOCKED by semgrep — never do these

```python
# f-string in SQL — BLOCKED
frappe.db.sql(f"SELECT name FROM `tabFarmer Registration` WHERE state = '{state}'")

# .format() in SQL — BLOCKED
frappe.db.sql("SELECT name FROM `tabFarmer Registration` WHERE state = '{}'".format(state))
frappe.db.sql("SELECT name FROM `tabFarmer Registration` WHERE state = '{state}'".format(state=state))

# .format() on a variable then passed to sql — BLOCKED
query = "SELECT name FROM `tab{doctype}`".format(doctype=dt)
frappe.db.sql(query)  # semgrep traces the format() to the sql() call

# f-string assigned to variable then passed to sql — BLOCKED
query = f"SELECT name FROM `tabFarmer Registration` WHERE name = '{name}'"
frappe.db.sql(query)
```

### ✅ CORRECT — always use `%(key)s` parameterized queries

```python
# Named parameters — the only safe pattern
frappe.db.sql(
    "SELECT name, farmer_name FROM `tabFarmer Registration` WHERE state = %(state)s",
    {"state": state},
    as_dict=True
)

# Multiple parameters
frappe.db.sql(
    "SELECT name FROM `tabFarmer Registration` WHERE state = %(state)s AND district = %(district)s",
    {"state": state, "district": district},
    as_dict=True
)

# IN clause — pass a tuple/list directly
frappe.db.sql(
    "SELECT name, farmer_name FROM `tabFarmer Registration` WHERE name IN %(names)s",
    {"names": tuple(name_list)},   # ← tuple, not list
    as_dict=True
)
```

### Dynamic WHERE clauses — the only safe pattern

Reports often need to build WHERE clauses from optional filters. The correct pattern:
**condition strings are hardcoded, only VALUES are parameterized.**

```python
# ✅ CORRECT — condition strings are hardcoded constants, values go in params dict
conditions = ["cr.docstatus = 1"]      # hardcoded string, safe
values = {}

if (filters or {}).get("season_calendar"):
    conditions.append("cr.season_calendar = %(season)s")   # hardcoded field name
    values["season"] = filters["season_calendar"]           # value in params

if (filters or {}).get("district_agency"):
    conditions.append("cr.district_agency = %(da)s")
    values["da"] = filters["district_agency"]

where_clause = " AND ".join(conditions)   # safe: only hardcoded strings joined

# ✅ String concatenation of hardcoded WHERE clause is allowed
# (semgrep only blocks .format() and f-strings, not +)
frappe.db.sql(
    "SELECT name FROM `tabCrop Record` cr WHERE " + where_clause,
    values,
    as_dict=True
)

# ❌ WRONG — even if values are parameterized, .format() on any part is blocked
frappe.db.sql(
    "SELECT name FROM `tab{}` WHERE season = %(s)s".format(doctype),  # BLOCKED
    {"s": season}
)

# ❌ WRONG — f-string for table name is blocked even if it looks "safe"
frappe.db.sql(
    f"SELECT name FROM `tab{doctype}` WHERE season = %(s)s",  # BLOCKED
    {"s": season}
)
```

### Dynamic table names — use a whitelist

If you genuinely need a dynamic table name (rare in reports), use an explicit whitelist — never user input directly:

```python
# ✅ CORRECT — whitelist of allowed table names
ALLOWED_DOCTYPES = ["Farmer Registration", "Crop Record", "Procurement Center"]

def get_records(doctype, filters):
    if doctype not in ALLOWED_DOCTYPES:
        frappe.throw("Invalid doctype")
    # String concatenation of whitelisted value is safe
    # but avoid .format() or f-string to stay semgrep-clean
    table = "`tab" + doctype + "`"
    frappe.db.sql(
        "SELECT name FROM " + table + " WHERE name = %(name)s",
        {"name": filters.get("name")},
        as_dict=True
    )
```

### Quick mental check before every `frappe.db.sql()` call

```
1. Does any part of the SQL string use .format() or f"..."? → REMOVE IT
2. Are all user-supplied values going through %(key)s params? → GOOD
3. Are WHERE condition strings hardcoded (not built from user input)? → GOOD
4. Any dynamic table/column names? → Use whitelist + string concatenation (not .format/f-string)
```

---

## 4. Translations — Wrap All User-Facing Text {#4-translations}

**Every string a user reads must be wrapped in the translate function.** Untranslated strings block i18n and will be flagged in review. This applies to column labels, filter labels, status values, error messages, and any text in the JS formatter.

Ref: https://frappeframework.com/docs/user/en/guides/basics/translations

---

### Python — `_()` function

In the standard `execute()` file (bench/native execution):

```python
from frappe import _

def get_columns():
    return [
        {"label": _("Season Calendar Name"), "fieldname": "season_calendar_name", "fieldtype": "Data", "width": 150},
        {"label": _("Farmer ID"),            "fieldname": "farmer_id",            "fieldtype": "Data", "width": 160},
        {"label": _("Farmer Name"),          "fieldname": "farmer_name",          "fieldtype": "Data", "width": 150},
        {"label": _("KYC Status"),           "fieldname": "kyc_status",           "fieldtype": "Data", "width": 110},
        # ... all column labels wrapped in _()
    ]

# Status strings returned in data rows — also wrap
kyc_status = _("Verified") if fr.get("is_verified") else _("Pending")
reg_status = _("Approved") if fr.get("docstatus") == 1 else _("Pending")
```

### safe_exec context — `_()` availability

In the DB-stored `report_script` (RestrictedPython sandbox), `frappe._` is **blocked** (underscore attribute). However, Frappe pre-injects `_` as a standalone global in the safe_exec context.

```python
# ✅ safe_exec: use standalone _() — it is pre-injected by Frappe
kyc_status = _("Verified") if fr.get("is_verified") else _("Pending")

# ❌ safe_exec: frappe._() is BLOCKED (underscore attribute rule)
kyc_status = frappe._("Verified")   # SyntaxError
```

If `_` is not available in safe_exec on your Frappe version, use a fallback:

```python
# Fallback: define translate helper at the top of the script
def translate(s):
    return s   # passthrough — translations handled by report columns/JS layer

# Then use it for any derived strings in result rows
kyc_status = translate("Verified") if fr.get("is_verified") else translate("Pending")
```

### With context (disambiguation)

Use `context` when the same source string has different meanings:

```python
from frappe import _

# Same word, different meaning — context resolves ambiguity
label_a = _("Pending", context="KYC verification status")
label_b = _("Pending", context="Bank update status")
```

---

### JavaScript — `__()` function

All user-visible strings in the `.js` file must use `__()` — the Frappe JS translate function. This is already the standard for filter labels but must also cover formatter output.

```javascript
// ✅ Filter labels — always use __()
filters: [
    {
        fieldname: "season_calendar",
        label: __("Season Calendar"),      // ← __() required
        fieldtype: "Link",
        options: "Season Calendar",
        reqd: 1,
    },
    {
        fieldname: "state_agency",
        label: __("State Agency"),         // ← __() required
        fieldtype: "Link",
        options: "State Agency",
    },
],

// ✅ Formatter — wrap status strings in __()
formatter: function (value, row, column, data, default_formatter) {
    value = default_formatter(value, row, column, data);

    if (column.fieldname === "kyc_status") {
        if (data && data.kyc_status === __("Verified")) return green;  // compare translated
        if (data && data.kyc_status === __("Pending"))  return orange;
    }
    return value;
},
```

**Note on formatter comparisons:** If status values are already translated server-side (Python `_()`) before being stored in `result`, the JS comparisons must also use `__()` to match. If status values are stored as raw English strings in `result` and translated only for display, compare against the raw English and apply `__()` only to display output:

```javascript
// Pattern A — server returns translated strings, JS compares translated
if (data.kyc_status === __("Verified")) return green;

// Pattern B — server returns raw English, JS translates for display only
if (data.kyc_status === "Verified") {
    value = "<span>" + __("Verified") + "</span>";
    return green_wrap(value);
}
```

Pick one pattern and stick to it. Pattern B is simpler to test.

---

### Translation CSV files (for your app)

Create `apps/your_app/your_app/translations/` and add one CSV per language:

```
apps/bsebeam_agri/bsebeam_agri/translations/
├── hi.csv    ← Hindi
├── mr.csv    ← Marathi
└── en.csv    ← English (optional, for overrides)
```

CSV format — three columns, all quoted:

```csv
"source_string","translated_string","context"
"Season Calendar","मौसम कैलेंडर",""
"Farmer ID","किसान आईडी",""
"Verified","सत्यापित","KYC verification status"
"Verified","मंजूरी दी","Bank update status"
"Pending","लंबित",""
"Approved","अनुमोदित",""
"Completed","पूर्ण",""
"Aadhaar","आधार",""
```

**No bench build needed** — Frappe loads translations at runtime from the CSV. Only `bench build` if you changed `.js` files. Clear cache if new translations don't show immediately:

```bash
bench --site your-site clear-cache
```

---

### What counts as user-facing text in a Script Report

| Location | Examples | Wrap with |
|---|---|---|
| Column labels | `"Farmer ID"`, `"KYC Status"`, `"Crop Count"` | `_()` in Python |
| Filter labels | `"Season Calendar"`, `"State Agency"` | `__()` in JS |
| Derived status values | `"Verified"`, `"Pending"`, `"Approved"`, `"Completed"` | `_()` in Python (result rows) |
| Filter required error | `frappe.throw("Season Calendar is required")` | `frappe.throw(_("..."))` |
| Formatter display text | Status badge text, custom cell content | `__()` in JS |
| **Not user-facing** | Field names (`farmer_id`), SQL strings, internal keys | Do NOT wrap |

---

### Quick check before committing

```bash
# Grep for unwrapped string literals in column labels and throw calls
grep -n '"label":\s*"[A-Z]' your_report.py       # column labels not wrapped
grep -n "frappe\.throw(\"" your_report.py         # throw without _()
grep -n "label: \"[A-Z]" your_report.js           # JS filter labels not wrapped
```

All hits should use `_()` (Python) or `__()` (JS). Exception: fieldnames, options values, and SQL strings are intentionally not wrapped.

---

## 5. get_script — Disk File vs DB Field {#5-get-script}

This is the #1 cause of the filter bar never appearing.

### The Priority Order

```
Frappe calls get_script → looks for disk file first:
  apps/{app_name}/{module_folder}/report/{report_name}/{report_name}.js

  If disk file EXISTS → serves it. DB javascript field = IGNORED.
  If disk file MISSING → serves DB javascript field.
```

**Consequence:** If you deployed the app with the default stub `.js` file, the stub is what loads — forever — until the file on disk is updated. Updating `report.javascript` in the DB does nothing.

### Verify what get_script is actually serving

```bash
curl -s -H "Authorization: token KEY:SECRET" \
  "https://yoursite.com/api/method/frappe.desk.query_report.get_script?report_name=Your%20Report" | \
  python3 -c "import json,sys; print(json.load(sys.stdin)['message']['script'][:400])"
```

### The default stub

When you scaffold a new Frappe report, the auto-generated `.js` file looks like this:

```javascript
frappe.query_reports["Your Report"] = {
    filters: [
        // { "fieldname": "my_filter", ... }  ← ALL COMMENTED OUT
    ],
};
```

This registers an **empty filters array**. Result: filter bar never renders.

### Fix options (in order of preference)

1. **Deploy correct file via git + bench** — commit the real `.js` to the repo, then `bench get-app` + `bench build --app your_app` on the server
2. **Direct SSH** — write the file directly on disk, then `bench build --app your_app`
3. **Store filters in Report.filters child table** — works as fallback when `js_filters = []`, but only if the empty-array stub is what the disk file contains (see §5)

---

## 6. Filter Storage — Child Table, Not JS {#6-filters}

### The two-path fallback in Frappe v16

```javascript
// Inside query_report.js (Frappe source, line ~729):
let js_filters = frappe.query_reports[report_name]?.filters || [];
this.filters = js_filters.length ? js_filters : report.filters;
//                                                ↑ child table fallback
```

If `js_filters` = [] (empty, from stub), Frappe **falls back** to `report.filters` from the DB child table. This is the only way to get filters working without touching the disk file.

### How to store filters in the child table

```python
filters_payload = [
    {
        "doctype": "Report Filter",
        "fieldname": "season_calendar",
        "label": "Season Calendar",
        "fieldtype": "Link",
        "options": "Season Calendar",   # ← DocType name for Link fields
        "mandatory": 1,                 # ← NOT "reqd" — that's a different field
    },
    {
        "doctype": "Report Filter",
        "fieldname": "district_agency",
        "label": "District Agency",
        "fieldtype": "Link",
        "options": "District Agency",
        "mandatory": 0,
    },
]

# PUT to Report resource
payload = {"filters": filters_payload}
requests.put(f"{BASE}/api/resource/Report/{report_name}", json=payload, headers=HDR)
```

### ⚠️ Critical: the field is `mandatory`, not `reqd`

```python
# Report Filter DocType fields:
# label     | Data
# fieldtype | Select
# fieldname | Data
# mandatory | Check    ← USE THIS
# options   | Small Text
# default   | Small Text
```

`reqd` is the field name in DocType fields — `mandatory` is the field name in Report Filter.

### get_query for cascading filters

Cascading filters (`get_query`) **cannot** be stored in the child table — they require JavaScript functions. Store the base filters in the child table, add cascading logic to the disk `.js` file.

---

## 7. Column Storage — Child Table, Not Script {#7-columns}

In Frappe v16 safe_exec mode, `columns` returned from `execute()` is **ignored**. Column definitions must be stored in the `Report.columns` child table.

```python
columns_payload = [
    {"label": "Farmer ID", "fieldname": "farmer_id", "fieldtype": "Data", "width": 160},
    {"label": "Farmer Name", "fieldname": "farmer_name", "fieldtype": "Data", "width": 150},
    {"label": "KYC Status", "fieldname": "kyc_status", "fieldtype": "Data", "width": 110},
    # ... all 33 columns
]

# Add doctype to each row
for col in columns_payload:
    col["doctype"] = "Report Column"

requests.put(f"{BASE}/api/resource/Report/{report_name}", json={"columns": columns_payload}, headers=HDR)
```

Verify they're stored:
```bash
curl -s -H "Authorization: token KEY:SECRET" \
  "https://yoursite.com/api/resource/Report/Your%20Report" | \
  python3 -c "import json,sys; d=json.load(sys.stdin)['data']; print('cols:', len(d.get('columns',[])))"
```

---

## 8. Workspace Wiring — Shortcut Block Rules {#8-workspace}

### Content block must include `shortcut_name`

```python
# ❌ WRONG — shortcut card never renders
content = [{"id": "block1", "type": "shortcut", "data": {}}]

# ✅ CORRECT — shortcut_name must match the shortcut's label exactly
content = [{"id": "block1", "type": "shortcut", "data": {"shortcut_name": "Your Report Name", "col": 3}}]
```

### Full workspace + shortcut creation

```python
workspace_payload = {
    "doctype": "Workspace",
    "title": "Reports",
    "label": "Reports",
    "module": "BSE BeAM",
    "app": "your_app",
    "parent_page": "Main Dashboard",   # parent workspace name
    "public": 1,
    "type": "Workspace",
    "content": json.dumps([
        {"id": "rpt-1", "type": "shortcut", "data": {"shortcut_name": "Your Report Name", "col": 3}}
    ]),
    "shortcuts": [
        {
            "doctype": "Workspace Shortcut",
            "type": "Report",
            "link_to": "Your Report Name",
            "label": "Your Report Name",    # ← must match shortcut_name in content
            "icon": "es-line-users",
            "color": "#4CAF50",
            "report_ref_doctype": "Farmer Registration",
        }
    ],
}
```

### Verify via get_desktop_page (not get_desktop_page_data)

```python
import urllib.parse
params = urllib.parse.urlencode({
    "page": json.dumps({"name": "Reports", "title": "Reports", "public": 1})
})
r = requests.get(f"{BASE}/api/method/frappe.desk.desktop.get_desktop_page?{params}", headers=HDR)
shortcuts = r.json()["message"]["shortcuts"]["items"]
for s in shortcuts:
    print(s["label"], "→", s["link_to"])
```

---

## 9. Deployment Checklist — Step by Step {#9-checklist}

Run through this in order for every new report.

### Phase 1 — Schema discovery (do this first)

```python
# Before writing a single line of report logic, verify all fields exist
curl -s -H "Authorization: token KEY:SECRET" \
  "https://site.com/api/resource/DocType/Your%20Doctype" | \
  python3 -c "
import json,sys
d=json.load(sys.stdin)['data']
for f in d.get('fields',[]):
    if f['fieldtype'] not in ['Column Break','Section Break','Tab Break']:
        print(f['fieldname'], '|', f['fieldtype'], '|', f.get('label',''))
"
```

Check every source doctype for:
- Exact field names (not display labels)
- Link field options (what doctype they point to)
- Child table field names
- Whether the field even exists (many "obvious" fields don't)

### Phase 2 — Create the report record (is_standard: No)

```python
payload = {
    "doctype": "Report",
    "report_name": "Your Report Name",
    "ref_doctype": "Primary DocType",
    "report_type": "Script Report",
    "module": "Your Module",
    "is_standard": "No",
    "disabled": 0,
}
r = requests.post(f"{BASE}/api/resource/Report", json=payload, headers=HDR)
print("Created:", r.json()["data"]["name"])
```

### Phase 3 — Store columns in child table

See §7. Do this before testing the script.

### Phase 4 — Store filters in child table

See §6. Do this before testing the script.

### Phase 5 — Local validation before pushing (run all three, fix before deploying)

**Run these three checks against your `.py` file before pushing to the server. Catching here saves a debug cycle.**

```bash
# 1. SQL injection check — same rule pre-commit enforces
#    Blocks: .format() or f-strings in frappe.db.sql() calls
semgrep --config frappe-semgrep-rules/rules/security/sql.yml your_report.py

# Expected: "Findings: 0" — any finding must be fixed before proceeding
# If frappe-semgrep-rules not installed locally:
# pip install semgrep && git clone https://github.com/frappe/frappe-semgrep-rules

# 2. Style and lint check — catches unused vars, bad syntax, import issues
ruff check your_report.py

# Expected: no output (all clear)
# If ruff not installed: pip install ruff
# Common fixes:
#   F841 local variable assigned but never used → remove or use it
#   E501 line too long → break the SQL string across lines
#   F811 redefinition of unused name → deduplicate variable assignments

# 3. Syntax check — catches Python parse errors before they hit safe_exec
python3 -c "
import ast, sys
with open('your_report.py') as f:
    source = f.read()
try:
    ast.parse(source)
    print('✅ Syntax OK')
except SyntaxError as e:
    print(f'❌ SyntaxError: {e}')
    sys.exit(1)
"
# Expected: ✅ Syntax OK
# A SyntaxError here will silently produce result=null on the server
```

**All three must pass cleanly before Phase 6.** If any fail:

| Tool | Common failure | Fix |
|---|---|---|
| `semgrep` | `frappe-sql-format-injection` | Replace `.format()`/f-string with `%(key)s` params |
| `ruff` | `F841` unused variable | Remove variable or use it |
| `ruff` | `E501` line too long | Break SQL string across continuation lines |
| `ruff` | `W291` trailing whitespace | Strip trailing spaces |
| `ast.parse` | `SyntaxError` | Fix Python syntax — safe_exec will silently swallow this |

### Phase 6 — Push the report_script

Write the script following safe_exec rules (§2) and SQL injection rules (§3). Key rules recap:
- No `import`
- No `frappe._dict()`
- No underscore variable names
- No `.format()` or f-strings in `frappe.db.sql()` calls
- Assign rows to `result`, not return value
- Empty filter guard: `if not season: result = []\nelse:\n    ...`
- **Run the three local checks in Phase 5 before pushing**

```python
with open("your_report.py") as f:
    script = f.read()

# For 417 errors (large payloads via nginx proxy):
import requests
r = requests.put(
    f"{BASE}/api/resource/Report/Your%20Report%20Name",
    data=json.dumps({"report_script": script}),
    headers={**HDR, "Content-Type": "application/json", "Expect": ""},
)
print("Script len:", len(r.json()["data"]["report_script"] or ""))
```

### Phase 7 — Test execution

```python
params = urllib.parse.urlencode({
    "report_name": "Your Report Name",
    "filters": json.dumps({"your_filter": "filter_value"}),
    "ignore_prepared_report": 1,
})
r = requests.get(f"{BASE}/api/method/frappe.desk.query_report.run?{params}", headers=HDR)
msg = r.json().get("message", {})
print(f"Cols: {len(msg.get('columns') or [])} | Rows: {len(msg.get('result') or [])} | Time: {msg.get('execution_time',0):.3f}s")
```

Healthy response: execution_time > 0.001s (script is running), cols = your column count, rows = expected count.

### Phase 8 — Fix the disk .js file

```bash
# Check what get_script is currently serving
curl -s -H "Authorization: token KEY:SECRET" \
  "https://site.com/api/method/frappe.desk.query_report.get_script?report_name=Your%20Report%20Name" | \
  python3 -c "import json,sys; print(json.load(sys.stdin)['message']['script'])"
```

If it's the stub (empty `filters: []`), either:
1. Fix via bench: `git pull` + `bench build --app your_app`
2. Verify the child table filters (§6) are populated as fallback

### Phase 9 — Wire workspace

See §8. Verify with `get_desktop_page`.

### Phase 10 — Clear cache and test in incognito

```python
requests.post(f"{BASE}/api/method/frappe.sessions.clear", json={}, headers=HDR)
```

Then open an **incognito window** to avoid stale SPA asset cache.

---

## 10. Debugging Protocol — Blank Screen Triage {#10-debug}

### Console shows `[] 'js_filters'` at `query_report.js:72X`

Frappe logged the JS filters array and it's empty. Flow:

```
Step 1: Check get_script output
  → curl the endpoint (see §7 Phase 7)
  → If stub with empty filters: fix disk file OR ensure child table is populated

Step 2: Check Report.filters child table
  → curl /api/resource/Report/Name and count filters
  → If 0: store filters via API (see §4)
  → If populated but still blank: disk file has non-empty filters array that overrides

Step 3: Check filter field name
  → Report Filter uses "mandatory" not "reqd"
  → Wrong field = filter stored but required indicator not set
```

### Report shows `result: null` with execution_time ~0.001s

Script not running at all. Causes:

```
→ safe_exec disabled (server_script_enabled=false in frappe.conf)
   Fix: enable via bench or check if Server Scripts work on this instance
   Test: call an existing API-type Server Script to verify safe_exec works

→ is_standard: Yes set but no disk file → returns Frappe stub with hardcoded data
   Fix: set is_standard: No
```

### Report shows exception with execution_time ~0.002-0.020s

Script ran but crashed. Read the exception from the response:

```python
r = requests.get(f"{BASE}/api/method/frappe.desk.query_report.run?{params}", headers=HDR)
if r.status_code != 200:
    print(r.json().get("exception", "")[:500])
```

Common exceptions and fixes:

| Exception | Fix |
|---|---|
| `ImportError: __import__ not found` | Remove all `import` statements |
| `SyntaxError: "_dict" is invalid` | Replace `frappe._dict()` with `{}` |
| `SyntaxError: "_result" is invalid` | Rename variable — no underscore prefix |
| `_unpack_sequence_ not defined` | Replace `a, b = fn()` with indexed access |
| `KeyError: 0` | Frappe tried to index tuple return — remove return statement |
| `NameError: name 'open' is not defined` | Can't use open() in safe_exec — no file I/O |
| `AttributeError: module has no attribute 'utils'` | Can't use frappe.utils — use frappe.db.sql instead |
| `TypeError: '>' not supported between 'datetime.date' and 'str'` | `frappe.utils.today()` returns a **string** (`'2026-04-13'`), `frappe.utils.getdate()` returns a **date object**. Comparing them with `>` or `<` raises TypeError. Use `frappe.utils.getdate()` for both sides, or compare strings to strings. |

### Report runs but columns = 0

Column definitions not in child table. Push them (see §5).

### Report page loads but `Nothing to show` with no filter bar

Filter bar missing = `js_filters = []` and child table also empty or Frappe version quirk.
Check the two-path fallback (§4). Open **incognito window** to rule out stale SPA cache.

### 417 Expectation Failed on large PUT requests

nginx proxy rejects large bodies. Use `requests` library (not `urllib`) with `Expect: ""` header:

```python
import requests
r = requests.put(
    f"{BASE}/api/resource/Report/Name",
    data=json.dumps(large_payload),
    headers={**HDR, "Content-Type": "application/json", "Expect": ""},
)
```

---

## 11. Post-Mortem — Every Mistake Made {#11-postmortem}

These happened in the exact sequence below. Don't repeat them.

| # | Mistake | Root cause | Fix |
|---|---|---|---|
| 1 | `frappe.throw()` in empty filter guard | Frappe runs script on page load with empty filters — throws blocking modal | Replace with `if not season: result = []` |
| 2 | `import frappe` at top of script | safe_exec blocks `__import__` | Remove all import statements |
| 3 | Used `frappe._dict()` for row dicts | safe_exec blocks underscore-prefixed attributes | Use plain `{}` or `dict()` |
| 4 | Used `columns, data = execute(filters)` at module level | RestrictedPython blocks tuple unpacking (`_unpack_sequence_`) | Use indexed access: `r = fn(); columns = r[0]; data = r[1]` |
| 5 | Used `_result` as variable name | safe_exec blocks underscore-prefixed names | Use `result` (no prefix) |
| 6 | Returned `(columns, data)` from `execute()` | safe_exec doesn't capture return values — reads from locals | Assign rows to `result` variable at module level |
| 7 | Used template literals (backticks) in JS | Can cause silent parse failures in Frappe's eval context | Use string concatenation |
| 8 | Used tab indentation in JS | Same eval issue | Use 4-space indentation |
| 9 | Put filters in JS `frappe.query_reports[name].filters` via DB field | `get_script` serves disk file, not DB javascript field | Store filters in Report.filters child table |
| 10 | Used `reqd: 1` in Report Filter | Wrong field name — Report Filter uses `mandatory` | Use `mandatory: 1` |
| 11 | Content block `data: {}` in workspace | Frappe reads `shortcut_name` from data to resolve shortcut — empty means nothing renders | Use `data: {"shortcut_name": "Report Name", "col": 3}` |
| 12 | Workspace content was `[]` | No shortcut block = no render | Add `{"type": "shortcut", "data": {"shortcut_name": ...}}` block |
| 13 | Set `is_standard: Yes` to bypass safe_exec | Frappe loads disk file (stub) for is_standard=Yes, ignores DB script | Keep `is_standard: No`, ensure safe_exec is enabled |
| 14 | Tried to write disk file via Server Script `open()` | RestrictedPython blocks `open()` | Need bench/SSH for disk writes |
| 15 | Filter bar blank in browser after all fixes | Stale SPA cache of old stub JS | Open incognito window — clears asset cache |
| 16 | Used f-string in SQL: `f"WHERE state = '{state}'"` | `frappe-sql-format-injection` semgrep rule — blocks PR at pre-commit | Use `%(state)s` parameterized query: `"WHERE state = %(state)s", {"state": state}` |
| 17 | Used `.format()` in SQL: `"WHERE name = '{}'".format(name)` | Same semgrep rule — blocking | Same fix: `%(name)s` params dict |
| 18 | Built table name dynamically with f-string: `` f"SELECT * FROM `tab{doctype}`" `` | Same semgrep rule even for "safe" dynamic table names | Use whitelist + string concatenation: `"SELECT * FROM `tab" + allowed_dt + "`"` |
| 19 | Column labels hardcoded as raw strings: `{"label": "Farmer ID", ...}` | Untranslated strings break i18n — all user-facing text must use `_()` | `{"label": _("Farmer ID"), ...}` in Python; `label: __("Farmer ID")` in JS |
| 20 | Status values `"Verified"`, `"Pending"` returned raw without `_()` | Users on non-English locales see English status strings | Wrap: `_("Verified")` in Python result rows |
| 21 | Used `frappe._("string")` inside safe_exec script | Underscore attribute blocked by RestrictedPython | Use standalone `_("string")` — Frappe pre-injects `_` as a global in safe_exec |
| 22 | Compared `frappe.utils.today()` with a date object using `>` | `today()` returns a string, `getdate()` returns `datetime.date` — types don't compare | Use `frappe.utils.getdate()` consistently for date comparisons |
| 23 | Deployed Server Script but behavior didn't change | `bench build` and `bench migrate` don't reload Python into running workers | Restart the application server (`bench restart` or `supervisorctl restart all`) after Python-level changes |

---

## 12. Complete Working Templates {#12-templates}

Read `references/templates.md` for:
- Complete safe_exec-compatible Python script (multi-doctype join, bulk SQL, 33+ columns)
- Complete JS file (4 cascading filters, formatter, no backticks, 4-space indent)
- Complete deployment script (create report, push script, push columns, push filters, wire workspace)
- Complete diagnostic script (verify all components in one pass)

---

## Quick Reference

### Execution timeline on `is_standard: No` report

```
Page load
  ├── get_script() → disk .js file (NOT DB javascript field)
  │     → eval'd → frappe.query_reports[name] registered
  ├── query_report.js line ~729 reads js_filters from registration
  │     → if [] → reads report.filters child table as fallback
  ├── Filter bar renders from filters (child table or JS)
  ├── User selects filters → Run
  ├── frappe.desk.query_report.run() → executes report_script via safe_exec
  │     → reads 'result' variable from locals
  └── Columns from report.columns child table, rows from 'result'
```

### Minimum viable working report (API calls in order)

```
1. POST /api/resource/Report        → create record
2. PUT  /api/resource/Report/Name   → push report_script
3. PUT  /api/resource/Report/Name   → push columns[] child table
4. PUT  /api/resource/Report/Name   → push filters[] child table
5. Test via query_report.run        → verify rows + cols
6. Fix disk .js file via bench      → verify filter bar in incognito
7. POST /api/resource/Workspace     → create Reports workspace
8. Verify via get_desktop_page      → confirm shortcut resolves
```
