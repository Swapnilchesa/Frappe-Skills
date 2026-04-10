---
name: frappe-doctype-skill
description: >
  Use this skill whenever designing, speccing, or reviewing Frappe DocTypes,
  fields, permissions, workflows, or approval states. Activates for: new
  feature specs, DocType design discussions, workflow planning, approval
  chain setup, migration planning, form layout, list view configuration,
  sidebar setup (v16), and any conversation where a team member is trying
  to describe a new concept or process they want to build in Frappe.
  The goal: produce complete, code-ready specs BEFORE any code is written.
  Covers Frappe v15 and v16. v16 sidebar and UI changes are handled explicitly.
---

# Frappe DocType & Workflow Skill
### Version: Frappe v16-aware | Last updated: April 2026

> **Who this is for:** Everyone — product leads, developers, business analysts, QA.
> This skill is the shared language for describing anything we want to build on Frappe.
> A complete spec means a developer can build it without a single clarifying question.
>
> **Why this exists:** Spec first, code never. This skill ensures every DocType,
> field, approval state, list view, and sidebar entry is fully thought through before
> a single line of Python or JavaScript is written.
>
> **Reference files — read when directed:**
> - `references/field-types.md` — complete field type tables, DocField properties, v16 field changes, common field JSON combinations
> - `references/workflow-and-states.md` — full workflow JSON, conditional routing, multi-stage templates, list view config, form layout JSON, troubleshooting table
> - `references/v16-sidebar.md` — complete v16 sidebar setup sequence, all 6 known bugs with fixes, verification checklist
> - `evals/evals.json` — test cases for validating spec quality

---

## PART 0: Skill Interaction Model

This skill operates in two modes. You choose which at the start.

---

### Mode A: API Key Mode

When the user provides API keys to an active Frappe/ERPNext instance:

1. **Explore first.** Use the REST API to pull:
   - Existing DocTypes, modules, roles, workspaces, workflows
   - `GET /api/resource/DocType?filters=[["module","=","YourModule"]]`
   - `GET /api/resource/Workspace`
   - `GET /api/resource/Role`
   - `GET /api/resource/Workflow?filters=[["document_type","=","DocType"]]`
2. **Surface gaps.** Map what exists against what the user wants to build.
3. **Give targeted suggestions.** Based on real data — no assumptions about what's already there.
4. **Diagnose sidebar issues.** Pull workspace + sidebar configs via API and cross-reference with known v16 bugs (see Part 12).
5. **Output a complete, pre-validated spec.** Fields you suggest won't duplicate existing fieldnames.

> **API pattern for read:**
> ```
> GET https://{site}/api/resource/{DocType}?limit_page_length=100
> Authorization: token {api_key}:{api_secret}
> ```

---

### Mode B: Manual Mode (no API key)

When no API key is provided:

1. Ask the user the **Approval Questions** (Part 0.1) before generating anything.
2. Use answers + reasonable assumptions (stated explicitly) to fill the spec.
3. Flag every assumption with `[ASSUMPTION — confirm]` so the user can override.
4. Generate all 5 deliverables (Part 0.2) once answers are locked.

---

### Part 0.1: Approval Questions (ask before generating)

Do not generate the full spec until these are answered. Ask all at once:

```
Before I generate the complete spec, I need 5 quick answers:

1. DOCTYPE NAME & PURPOSE
   What is this DocType called and what single problem does it solve?

2. TYPE
   [ ] Master (reference data, rarely changes — NGO, Donor)
   [ ] Transactional + Submittable (formal decision records — grants, applications)
   [ ] Child Table (lives inside another DocType)
   [ ] Single (global settings)

3. MODULE
   Which app module does this belong to? (e.g., "Grant Management", "mGrant CSR")

4. ROLES
   List the roles that will interact with this. For each: can they create / read-only / approve?

5. APPROVAL FLOW
   [ ] No approval — just save
   [ ] Simple submit (one approver, one moment)
   [ ] Multi-stage workflow (multiple roles, multiple states)
   If workflow — what are the stages and who approves each?
```

---

### Part 0.2: The Five Deliverables

After approval questions are answered, generate ALL of these in sequence:

| # | Deliverable | What it covers |
|---|---|---|
| 1 | **Complete DocType Schema** | Every field, fieldtype, options, validations, dependencies |
| 2 | **Form Layout** | Section breaks, column breaks, tabs — exactly as it will render |
| 3 | **List View Configuration** | Which columns show, default sort, filters, indicators |
| 4 | **User Roles & Permissions** | Role table with every permission action stated |
| 5 | **Sidebar Setup (v16)** | Full step-by-step, including all known v16 bugs and fixes |

---

## Part 1: Understanding DocTypes

### What is a DocType?

A DocType is **the single core building block** of every Frappe application.
It simultaneously defines:

- The **database table** (columns, types, indexes)
- The **form UI** (fields, layout, tabs, conditional visibility)
- The **list view** (which columns show, default filters)
- The **ORM model** (how you query, create, update, delete in Python)
- The **REST API** (auto-generated endpoints)
- The **permissions** (who can read, write, submit, cancel)

When you save a DocType in Frappe, a JSON file is generated. When `bench migrate`
runs, that JSON is applied to the database and UI simultaneously.

**Convention:** DocType names are always **singular**. The database table is
prefixed with `tab`. So `Grant Application` creates a table called `tabGrant Application`.

---

### Types of DocType

| Type | Flag | Use For |
|---|---|---|
| Regular (Master) | default | Reference/entity data. NGO, Donor, Employee |
| Regular (Transactional) | `is_submittable: 1` | Events/decisions. Grant Application, Leave Request |
| Child Table | `istable: 1` | One-to-many rows inside a parent. Milestones, Installments |
| Single | `issingle: 1` | Global settings. One record, no list view |
| Tree | `is_tree: 1` | Hierarchies. Department, Chart of Accounts |

---

### Standard System Fields (auto-generated — do NOT define manually)

| Fieldname | Type | Purpose |
|---|---|---|
| `name` | varchar(140) | Primary key |
| `owner` | Link(User) | Who created it |
| `creation` | Datetime | Created at |
| `modified` | Datetime | Last modified |
| `modified_by` | Link(User) | Who last modified |
| `docstatus` | Int | 0=Draft, 1=Submitted, 2=Cancelled |
| `idx` | Int | Row index in child tables |

---

## Part 2: DocType Fields — Complete Reference

### Key DocField Properties

| Property | Description |
|---|---|
| `label` | Human-readable UI label |
| `fieldname` | snake_case; becomes DB column and Python attribute |
| `fieldtype` | Type from the reference below |
| `reqd` | 1 = mandatory |
| `default` | Default on new document |
| `options` | Target DocType (Link) or newline-separated values (Select) |
| `depends_on` | Show/hide expression: `eval: doc.status == 'Approved'` |
| `mandatory_depends_on` | Make mandatory only when condition is true |
| `read_only` | 1 = non-editable in UI |
| `hidden` | 1 = hidden from UI (still in DB) |
| `in_list_view` | 1 = show as column in list view |
| `in_filter` | 1 = filterable in list view |
| `search_index` | 1 = add DB index |
| `description` | Help text below the field |
| `permlevel` | 0-9; controls field-level access by role |
| `fetch_from` | Auto-populate from a linked document: `link_field.field_on_linked_doc` |

---

### Field Type Reference

#### Data / Text
| Fieldtype | DB Type | Use When |
|---|---|---|
| `Data` | varchar(140) | Short text, names, codes |
| `Small Text` | text | Medium descriptions |
| `Text` | text | Long text |
| `Long Text` | longtext | Very long, unlimited |
| `Text Editor` | longtext | Rich text / WYSIWYG |
| `Markdown Editor` | longtext | Markdown with preview |
| `Code` | longtext | Code blocks |
| `Password` | text | Encrypted storage |
| `Read Only` | — | Display-only (no DB column) |

#### Numbers
| Fieldtype | DB Type | Use When |
|---|---|---|
| `Int` | int | Whole numbers |
| `Float` | decimal(21,9) | Decimal numbers |
| `Currency` | decimal(21,9) | Money (shows currency symbol) |
| `Percent` | decimal(21,9) | Percentage (0–100) |
| `Rating` | decimal(3,1) | Star rating (0–5) |
| `Duration` | int | Timespan in seconds |

#### Date / Time
| Fieldtype | DB Type | Use When |
|---|---|---|
| `Date` | date | Date only |
| `Time` | time | Time only |
| `Datetime` | datetime | Date + time |

#### Selection
| Fieldtype | DB Type | Use When |
|---|---|---|
| `Select` | varchar(140) | Fixed dropdown; options = newline-separated values |
| `Check` | int(1) | Boolean checkbox |
| `Autocomplete` | varchar(140) | Text with suggestions |

#### Relationships
| Fieldtype | DB Type | Use When |
|---|---|---|
| `Link` | varchar(140) | Link to another DocType |
| `Dynamic Link` | varchar(140) | Link to any DocType; type from another field |
| `Table` | — | Embed child DocType as rows |
| `Table MultiSelect` | — | Multi-select using a child DocType |

#### Layout / Structural (no DB column)
| Fieldtype | Purpose |
|---|---|
| `Section Break` | Horizontal divider; starts a new section |
| `Column Break` | Splits a section into columns |
| `Tab Break` | Creates a new tab in the form (v14+) |
| `Fold` | Collapses section by default |
| `HTML` | Raw HTML injection |
| `Heading` | Bold title text |

#### File / Media
| Fieldtype | DB Type | Use When |
|---|---|---|
| `Attach` | text | Any file attachment |
| `Attach Image` | text | Images only |
| `Image` | text | Renders image from Attach Image field |
| `Signature` | text | Digital signature capture |
| `Barcode` | text | Barcode display |

#### Special
| Fieldtype | DB Type | Use When |
|---|---|---|
| `JSON` | json | Store structured data |
| `Color` | varchar(140) | Color picker |
| `Phone` | varchar(140) | Phone number |
| `Geolocation` | text | Map/coordinates |

---

### v16 Field Changes

- **Data field now has preset `options`:** When you select fieldtype `Data`, the Options field becomes a dropdown with presets: Email, Name, Phone, URL, Barcode, IBAN. Choose one for validation and input hints.
- **Filter operators now plain-language in list view:** Operators like `!=` now show as "not equals" in the UI.
- **Default sort changed to `creation`:** All list views in v16 sort by `creation` by default (was `modified`). Explicitly set `sort_field` if you want different behaviour.
- **UUID naming rule added:** New option `autoname = "UUID"` for globally unique IDs.

---

## Part 3: DocType Naming

| Method | How to Set | Example Result |
|---|---|---|
| Naming Series | `autoname = "GA-.YYYY.-.####"` | `GA-2024-0001` |
| By Field | `autoname = "field:title"` | Uses field value as name |
| UUID | `autoname = "UUID"` | Random UUID (v16 addition) |
| Hash | `autoname = "hash"` | Random hash |
| Prompt | `autoname = "Prompt"` | User types the name |
| Expression | `autoname = "format:{ngo}-{YYYY}-{####}"` | `NGO-001-2024-0001` |

**Best practice:** Transactional DocTypes → always Naming Series. Human-readable + sortable.

---

## Part 4: Creating a DocType

### Via UI (recommended for first draft)
1. Desk → DocType → New
2. Fill: Name, Module, type flags
3. Add fields in Fields table
4. Add permissions in Permissions table
5. Save → Frappe creates DB table + JSON

### Via JSON (code-controlled)
```json
{
  "doctype": "DocType",
  "name": "Grant Application",
  "module": "Grant",
  "is_submittable": 1,
  "track_changes": 1,
  "fields": [ ... ],
  "permissions": [ ... ]
}
```
Place at: `apps/{app}/{app}/{module}/{doctype_folder}/{name}.json`
Run: `bench migrate`

### Via Python (fixtures/migrations)
```python
doc = frappe.get_doc({
    "doctype": "DocType",
    "name": "Grant Application",
    "module": "Grant",
    "fields": [{"fieldname": "title", "fieldtype": "Data", "label": "Title", "reqd": 1}]
})
doc.insert()
```

### Custom Fields (extend existing DocTypes without touching core)
```python
frappe.get_doc({
    "doctype": "Custom Field",
    "dt": "User",
    "fieldname": "employee_id",
    "fieldtype": "Data",
    "label": "Employee ID",
    "insert_after": "email"
}).insert()
```

---

## Part 5: Controllers (Python Behaviour)

```python
from frappe.model.document import Document

class GrantApplication(Document):

    def validate(self):
        """Every save. Put all validation logic here."""
        if self.requested_amount <= 0:
            frappe.throw("Requested Amount must be > 0")

    def before_insert(self):
        """First save only."""
        pass

    def on_submit(self):
        """docstatus 0 → 1"""
        self.notify_reviewers()

    def on_cancel(self):
        """docstatus 1 → 2"""
        self.revert_allocations()

    def on_update(self):
        """After every save."""
        pass
```

**Lifecycle order:**
`before_insert → validate → on_update → after_insert` (new docs)
`validate → on_update` (updates)
`on_submit` / `on_cancel` (state changes)

### Shared Controller Logic Across DocTypes

When the same validation or business rule applies to multiple DocTypes, extract it to a shared utility module — never copy-paste across controllers.

```python
# ✅ CORRECT — shared utility in myapp/utils/grant_utils.py
def validate_budget_not_exceeded(doc):
    allocated = frappe.db.sql("""
        SELECT SUM(amount) FROM `tabGrant Application`
        WHERE program = %s AND docstatus = 1
    """, doc.program)[0][0] or 0
    if allocated + doc.amount > doc.total_budget:
        frappe.throw(f"Budget exceeded for {doc.program}")

# In GrantApplication controller:
from myapp.utils.grant_utils import validate_budget_not_exceeded

class GrantApplication(Document):
    def validate(self):
        validate_budget_not_exceeded(self)

# In GrantAmendment controller — same import, no duplication:
class GrantAmendment(Document):
    def validate(self):
        validate_budget_not_exceeded(self)
```

```python
# ❌ BANNED — copy-pasted validation logic across controllers
# grant_application.py → def validate(self): ... 47 lines of budget logic ...
# grant_amendment.py  → def validate(self): ... same 47 lines ...
```

The spec's **Controller Logic** section must name the shared module when logic spans DocTypes:
```
- On validate: call grant_utils.validate_budget_not_exceeded(self)
               module: myapp/utils/grant_utils.py
```

---

## Part 6: Permissions

### Permission Actions

| Action | Key | Description |
|---|---|---|
| Read | `read` | View documents |
| Write | `write` | Edit and save |
| Create | `create` | Create new records |
| Delete | `delete` | Delete records |
| Submit | `submit` | docstatus 0→1 |
| Cancel | `cancel` | docstatus 1→2 |
| Amend | `amend` | Amended copy of cancelled doc |
| Report | `report` | Run reports |
| Export | `export` | Export data |
| Import | `import` | Import data |
| Print | `print` | Print documents |
| Email | `email` | Email documents |
| Share | `share` | Share with other users |

### Permission JSON Example
```json
"permissions": [
  {
    "role": "Grant Manager",
    "read": 1, "write": 1, "create": 1,
    "delete": 1, "submit": 1, "cancel": 1,
    "amend": 1, "report": 1, "export": 1, "print": 1
  },
  {
    "role": "Grant Applicant",
    "read": 1, "write": 1, "create": 1,
    "if_owner": 1
  }
]
```

`if_owner: 1` = user can only access documents they created.

### v16 Permission Changes
- `has_permission` hooks in Python must now **explicitly return True**. Returning `None` or a non-False value no longer grants access (breaking change from v15).
- State-changing methods now only accept **POST requests**. Any client GET calls to state-change endpoints must be updated to POST.

---

## Part 7: Form Layout — Section Breaks and Column Breaks

This is the most under-documented area. Get this right before handing off to a developer.

### How Layout Works

The form renders fields top-to-bottom. Layout is controlled by structural fields:

```
[Section Break: "Basic Info"]
  field_a (full width)
  field_b (full width)

[Section Break: "Financial Details"]
  field_c (left column)
[Column Break]
  field_d (right column)

[Section Break: "Approvals"] ← collapsed by default using 'collapsible'
  field_e
```

### Section Break Properties

| Property | Description |
|---|---|
| `label` | Section heading (leave blank for no heading) |
| `collapsible` | 1 = section is collapsible |
| `collapsible_depends_on` | Show collapse trigger only when condition true |
| `description` | Help text for the whole section |

### Column Break Rules

- A `Column Break` inside a section splits it into **equal-width columns**
- Maximum recommended: 2 columns per section (3 is possible but cramped on mobile)
- Fields before the first `Column Break` = left column
- Fields after = right column
- v16 note: **form sidebar moved to the RIGHT.** This means your right column is now visually adjacent to the sidebar — avoid putting dense data in the rightmost column on complex forms

### How to Document Layout (use this in every spec)

```
SECTION: [Section Name] | collapsible: No
  ROW:  field_a (Label: "X") ───── field_b (Label: "Y")
        └─ left column             └─ right column
  ROW:  field_c (full width)
  
SECTION: [Section Name 2] | collapsible: Yes, default collapsed
  ROW:  field_d ───── field_e
  ROW:  field_f (full width)
```

### JSON Layout Example
```json
[
  {"fieldtype": "Section Break", "label": "Basic Information"},
  {"fieldname": "title", "fieldtype": "Data", "label": "Title", "reqd": 1},
  {"fieldtype": "Section Break", "label": "Financial Details"},
  {"fieldname": "grant_amount", "fieldtype": "Currency", "label": "Grant Amount"},
  {"fieldtype": "Column Break"},
  {"fieldname": "currency", "fieldtype": "Link", "options": "Currency", "default": "INR"},
  {"fieldtype": "Section Break", "label": "Approval Info", "collapsible": 1},
  {"fieldname": "approved_by", "fieldtype": "Link", "options": "User", "read_only": 1},
  {"fieldname": "approval_date", "fieldtype": "Date", "read_only": 1}
]
```

### Tab Break (for complex DocTypes with many sections)

Use `Tab Break` when a DocType has more than ~6 sections. Each tab groups related sections.

```json
[
  {"fieldtype": "Tab Break", "label": "Overview"},
  {"fieldtype": "Section Break", "label": "Basic Info"},
  ...
  {"fieldtype": "Tab Break", "label": "Financials"},
  {"fieldtype": "Section Break", "label": "Budget"},
  ...
  {"fieldtype": "Tab Break", "label": "Approvals"},
  ...
]
```

> **Rule of thumb:** Tabs for complexity (many sections). Sections for grouping. Columns for related side-by-side fields (amounts + currency, start date + end date).

---

## Part 8: List View Configuration

The list view is what users see when they navigate to a DocType. Getting this right matters for day-to-day usability.

### What Controls List View Appearance

| Property | Where to Set | Effect |
|---|---|---|
| `in_list_view: 1` | On the field | Shows field as a column in list |
| `in_standard_filter: 1` | On the field | Adds quick filter at top of list |
| `in_filter: 1` | On the field | Available in the filter dropdown |
| `search_index: 1` | On the field | Fast DB search on this field |
| `bold: 1` | On the field | Column rendered bold in list |
| `Title Field` | DocType setting | Which field renders as the document title |

### Recommended List View Fields (include in every spec)

```
LIST VIEW COLUMNS:
  1. name (auto-included, shows as document link)
  2. [status field] — in_list_view: 1, with colour indicator
  3. [key reference field, e.g., NGO name] — in_list_view: 1
  4. [amount or key metric] — in_list_view: 1
  5. modified — in_list_view: 1 (shows last update)

DEFAULT SORT: creation DESC (v16 default — change only if business logic demands)

STANDARD FILTERS (quick filter bar):
  - status
  - [date range field]
  - [key lookup field]

INDICATORS (colour coding in list):
  - Draft → grey
  - Pending → orange
  - Approved → green
  - Rejected → red
```

### Status Indicators

Status indicators (coloured dots in the list view) are driven by the `indicator_fields`
setting on the DocType, or via the `get_indicator` method in the controller.

**Via controller (recommended):**
```python
@staticmethod
def get_list_data(data):
    pass  # Override for custom list logic

def get_indicator(self):
    color_map = {
        "Draft": "grey",
        "Pending Review": "orange",
        "Approved": "green",
        "Rejected": "red"
    }
    return [self.status, color_map.get(self.status, "grey"), "status,=," + self.status]
```

### v16 List View Changes
- **Default sort is now `creation` not `modified`** — set explicitly if you want otherwise
- **Filter operators shown in plain language** — no developer action needed, just UI change
- **Link field creation pre-populates form** — creating via a link field pre-fills filter values

---

## Part 9: Approval States — DocStatus vs Workflow

### DocStatus (simple)

| docstatus | State | Editable? |
|---|---|---|
| 0 | Draft | Yes |
| 1 | Submitted | No (locked) |
| 2 | Cancelled | No |

Use when: one approval moment, one role, no conditional routing.

### Frappe Workflow (multi-stage)

Use when: multiple roles, multiple states, conditional routing, email alerts.

**Required:** A `Select` field on the DocType for workflow state:
```json
{
  "fieldname": "status",
  "fieldtype": "Select",
  "options": "Draft\nPending Review\nApproved\nRejected",
  "default": "Draft",
  "read_only": 1,
  "in_list_view": 1
}
```

**Workflow JSON:**
```json
{
  "doctype": "Workflow",
  "name": "Grant Application Approval",
  "document_type": "Grant Application",
  "is_active": 1,
  "workflow_state_field": "status",
  "send_email_alert": 1,
  "states": [
    {"state": "Draft", "doc_status": "0", "color": "Gray"},
    {"state": "Pending Review", "doc_status": "0", "color": "Orange"},
    {"state": "Approved", "doc_status": "1", "color": "Green",
     "update_field": "approved_by", "update_value": "{frappe.session.user}"},
    {"state": "Rejected", "doc_status": "2", "color": "Red", "is_optional_state": 1}
  ],
  "transitions": [
    {"state": "Draft", "action": "Submit for Review", "next_state": "Pending Review", "allowed": "Grant Applicant"},
    {"state": "Pending Review", "action": "Approve", "next_state": "Approved", "allowed": "Grant Manager"},
    {"state": "Pending Review", "action": "Reject", "next_state": "Rejected", "allowed": "Grant Manager"},
    {"state": "Pending Review", "action": "Request Changes", "next_state": "Draft", "allowed": "Grant Manager"}
  ]
}
```

**Conditional routing:**
```json
{
  "state": "Pending Review",
  "action": "Escalate",
  "next_state": "Pending CEO Approval",
  "allowed": "Grant Manager",
  "condition": "doc.requested_amount > 5000000"
}
```

### Workflow Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| Action buttons not showing | User's role not in any transition `allowed` | Add role to a transition |
| Workflow not applying | Another workflow is active | Deactivate old workflow |
| State field not updating | Wrong `workflow_state_field` | Set correct field name |
| Submit button missing | Workflow overrides submit | Model submit as a workflow transition |
| Email alerts not sending | `send_email_alert` off, or no template | Enable + add email template |
| `has_permission` silently blocking (v16) | Hook returns None | Change to explicit `return True` |

---

## Part 10: DocType Naming (Autoname)

| Method | How to Set | Example |
|---|---|---|
| Naming Series | `autoname = "GA-.YYYY.-.####"` | `GA-2024-0001` |
| By Field | `autoname = "field:title"` | Field value |
| UUID | `autoname = "UUID"` | v16 addition |
| Hash | `autoname = "hash"` | Random hash |
| Prompt | `autoname = "Prompt"` | User types it |

---

## Part 11: V16 Sidebar — Complete Guide

### What Changed in v16

The v16 sidebar is a **complete architectural overhaul**. Understanding this is
essential because the old v15 workspace approach breaks silently in v16.

| Aspect | v15 | v16 |
|---|---|---|
| Navigation model | Module-based tabs | App-based persistent sidebar |
| Sidebar type | Left panel, auto-generated from module | Left panel, powered by `Workspace Sidebar` DocType |
| Form/List detail sidebar | Left side | **RIGHT side** (moved) |
| App switcher | Not present | Top-left icon, switches entire sidebar context |
| Workspace Sidebar DocType | Not present | New — must be created explicitly |
| Private workspaces | Mixed with shared | Moved to "My Workspaces" virtual app |

---

### The v16 Sidebar Architecture

```
┌─────────────────────────────────────────────────┐
│  [App Icon] [App Switcher]  ← top left           │
│  ┌──────────┐  ┌───────────────────────────────┐ │
│  │ Sidebar  │  │  Main Content Area            │ │
│  │          │  │                               │ │
│  │ Section  │  │  [Form fields here]           │ │
│  │  ├─ Link │  │                               │ │
│  │  ├─ Link │  │                ┌────────────┐ │ │
│  │  └─ Link │  │                │ Doc Sidebar│ │ │  ← moved RIGHT in v16
│  │          │  │                │ (attach,   │ │ │
│  │ Section  │  │                │  assign,   │ │ │
│  │  ├─ Link │  │                │  timeline) │ │ │
│  └──────────┘  └───────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

---

### Step-by-Step: Adding a DocType to the v16 Sidebar

Follow this **exact sequence**. Skipping steps or doing them out of order is the
primary cause of blank sidebars.

---

#### Step 1: hooks.py — Register the App

In your app's `hooks.py`, add `add_to_apps_screen`. This is **mandatory in v16**
for the app to appear in the app switcher sidebar.

```python
# apps/your_app/your_app/hooks.py

add_to_apps_screen = [
    {
        "name": "your_app",           # Must match app_name EXACTLY (case-sensitive — see Bug #1)
        "logo": "/assets/your_app/images/logo.png",
        "title": "Your App Title",
        "route": "/your_app",
        "has_permission": "your_app.api.permissions.check_app_permission",  # optional
    }
]
```

Then run:
```bash
bench --site {site} clear-cache
bench --site {site} build  # if assets changed
```

---

#### Step 2: Verify Module Definition

1. Go to **Desk → Module Def**
2. Confirm your module exists and `app_name` matches your app's folder name
3. Check: **Allow Modules** on the user's User record includes this module

---

#### Step 3: Create or Verify the Workspace

1. Go to **Desk → Workspace → New**
2. Set:
   - **Name**: Your workspace name (e.g., "Grant Management")
   - **Module**: Select your module
   - **Is Standard**: Check this for it to be version-controlled
   - **Restrict To Domain**: Leave blank unless domain-restricted
3. Add **Shortcuts** to your DocTypes and reports in the shortcuts table

> **v16 note:** The workspace alone is not enough for the sidebar. You also need
> a Workspace Sidebar (Step 4) and Desktop Icons (Step 5).

---

#### Step 4: Create Workspace Sidebar (NEW in v16)

This is the most commonly missed step. The `Workspace Sidebar` is a **separate DocType** from `Workspace`.

1. Go to **Desk → Workspace Sidebar → New**
2. Name it (e.g., "Grant Management Sidebar")
3. Add items in the **Items** table:

| Link To | Type | Label |
|---|---|---|
| Grant Application | DocType | Grant Applications |
| Grant Report | Report | Grant Report |
| Grant Settings | Page | Settings |

4. Save

The Workspace Sidebar does NOT auto-attach to a Workspace. You must link them via Desktop Icons (Step 5).

---

#### Step 5: Create Desktop Icons (the connector layer)

This is the v16 mechanism that connects everything. You need **two** Desktop Icon records.

**Icon A (Parent — the App entry):**
1. Desk → Desktop Icon → New
2. Set:
   - **Icon Type**: App
   - **Link Type**: External
   - **Logo URL**: `/assets/your_app/images/logo.png`
   - **Label**: Your App Name
   - **Link**: `/your_app` (or your workspace route)
3. Save → note the name of this record

**Icon B (Child — the Sidebar entry):**
1. Desk → Desktop Icon → New
2. Set:
   - **Icon Type**: Link
   - **Link Type**: Workspace Sidebar
   - **App**: frappe (or your app name)
   - **Parent Icon**: [name of Icon A above]
   - **Link To**: [name of your Workspace Sidebar from Step 4]
   - **Logo URL**: module icon URL
3. Save

---

#### Step 6: Set User/Role Permissions on Workspace

Workspaces are only visible to users whose roles have read access to at least one
DocType in the workspace. This is a core Frappe permission rule.

Confirm: every role that needs to see the sidebar has `read: 1` on at least one
of the DocTypes listed in the Workspace Sidebar.

If a role sees an empty/blank sidebar:
- Check: does the role have read permission on the DocTypes in the sidebar?
- Check: is the module listed in `Allow Modules` on the user's profile?

---

#### Step 7: Clear Cache and Reload

```bash
bench --site {site} clear-cache
# Then in browser: Ctrl+Shift+R (hard refresh)
```

---

### Known v16 Sidebar Bugs and Fixes

These are documented from the Frappe GitHub issues and community forum. Every one
has been reported multiple times. Know these before debugging any sidebar issue.

---

#### Bug #1: Case-Sensitivity in app_data_map (Most Common)

**Symptom:** Sidebar goes blank when opening a DocType. Console shows:
```
Uncaught TypeError: Cannot read properties of undefined (reading 'workspaces')
at Sidebar.make_sidebar
```

**Root Cause:** `frappe.boot.app_data_map` stores the app with its original casing
(from hooks.py app_name). But `frappe.current_app` returns lowercase. When these
don't match, `app_data_map[frappe.current_app]` returns `undefined`.

**Check:** In browser console, run:
```javascript
console.log(Object.keys(frappe.boot.app_data_map))
// vs
console.log(frappe.current_app)
```
If the casing differs — that's the bug.

**Fix Option A (correct — fix hooks.py):**
Ensure your `add_to_apps_screen["name"]` value is **exactly lowercase** to match
how `frappe.current_app` returns it. Use only lowercase + underscores.

**Fix Option B (hotpatch — for immediate unblocking):**
Patch `frappe/public/js/frappe/desk/sidebar.js`:
```javascript
// Find this line:
let app_workspaces = frappe.boot.app_data_map[frappe.current_app || "frappe"].workspaces;

// Replace with:
let current_app_key = frappe.current_app || "frappe";
let exact_key = Object.keys(frappe.boot.app_data_map).find(
    k => k.toLowerCase() === current_app_key.toLowerCase()
) || "frappe";
let app_workspaces = frappe.boot.app_data_map[exact_key].workspaces;
```
Run `bench build` after patching. Note: this patch will be overwritten on bench update.

---

#### Bug #2: Workspace Invisible Without DocType Permission

**Symptom:** Module/workspace does not show in sidebar for non-admin users, even
though the workspace exists and the module is enabled.

**Root Cause:** Frappe only marks a module as "allowed" if the current user has
read permission on at least one DocType in that module (GitHub issue #16025).
Modules with only reports or pages — no DocTypes — are invisible.

**Fix:**
- Ensure at least one DocType in the workspace has a read permission row for the user's role
- Or create a minimal DocType (even a settings DocType) in the module and give the role read access

---

#### Bug #3: Custom Workspace Only Visible to System Manager

**Symptom:** Workspace you created is only visible when logged in as System Manager or Administrator.

**Root Cause:** The Workspace DocType record has `Is Standard = 0` but no explicit
role sharing set. By default, non-standard workspaces are private/admin-only.

**Fix:**
- In the Workspace record, go to the **Roles** table
- Add roles that should see this workspace: e.g., "Grant Manager", "Grant Applicant"
- Save and clear cache

---

#### Bug #4: App Doesn't Load on First Click

**Symptom:** Clicking the app in the sidebar navigates to the wrong URL on first
click. Second click works correctly.

**Root Cause:** The app route defined in `hooks.py` `add_to_apps_screen["route"]`
doesn't match the workspace route, causing a redirect loop on the first hit.

**Fix:**
- Set `"route"` to the exact URL of the first workspace (e.g., `/app/grant-management`)
- Or point it to a dedicated landing page route

---

#### Bug #5: Sidebar Toggle Propagates to DocType Form

**Symptom:** If the user toggles sidebar off on the list view, the DocType form
view also loses its sidebar (Assign, Attach, Timeline disappear). Requires CMD+R to restore.

**Root Cause:** Known long-standing Frappe bug (issue #8956). The sidebar state
is stored in localStorage without scoping to view type.

**Fix/Workaround:**
- Instruct users to use CMD+R if this happens
- Or apply a custom JS override to reset sidebar state on form load

---

#### Bug #6: Workspace Sidebar Not Attached (zero-config trap)

**Symptom:** Workspace Sidebar was created and filled with items. The Workspace
exists. But the sidebar items don't appear in the left panel.

**Root Cause:** Creating a `Workspace Sidebar` DocType record does NOT automatically
link it to the Workspace. The connector is the Desktop Icon (Step 5 above). Most
developers/admins miss this entirely because it's non-intuitive.

**Fix:** Follow Step 5 — create the parent + child Desktop Icon pair that links
the Workspace Sidebar to the app's sidebar slot.

---

#### Bug #7: Workspace Missing from boot info

**Symptom:** `frappe.boot.app_data_map` exists but the workspaces array is empty
or missing even though Workspace records exist.

**Root Cause:** The workspace's `Is Standard` flag is unchecked, OR the workspace
is not set to `Public = 1`, OR the app's module is not in the site's installed apps.

**Fix checklist:**
```
[ ] Workspace.is_standard = 1  (if this should be part of the app)
[ ] Workspace.public = 1  (visible to all users with role access)
[ ] Module Def exists for the app's module
[ ] bench --site {site} clear-cache
[ ] bench --site {site} migrate  (if workspace JSON was changed on disk)
```

---

### Sidebar Verification Checklist (run after every setup)

```
[ ] hooks.py has add_to_apps_screen with correct lowercase name
[ ] bench clear-cache run after hooks.py change
[ ] Module Def exists
[ ] User's profile has the module in Allow Modules
[ ] Workspace exists, Is Standard checked, module set correctly
[ ] Workspace Sidebar DocType created with items
[ ] Desktop Icon (parent, type=App) created
[ ] Desktop Icon (child, type=Link, Link Type=Workspace Sidebar) created, Parent Icon set
[ ] User role has read permission on at least one DocType in the sidebar
[ ] Workspace has the correct roles set in its Roles table
[ ] Browser hard-refreshed after all changes
[ ] Browser console checked: frappe.boot.app_data_map casing verified
```

---

## Part 12: The Spec Template

Use this for every new DocType. Fill completely before any code is written.

---

```
## DocType Spec: [Name]

### Overview
What is this? What business problem does it solve?
Who uses it? When is it created? What happens after it's approved?

### Type
[ ] Regular (Master)
[ ] Regular (Transactional + Submittable)
[ ] Child Table (parent DocType: ___)
[ ] Single
[ ] Tree

### Module
Which module? Which app?

### Naming
[ ] Naming Series: ___________
[ ] By Field: ___________
[ ] UUID (v16)
[ ] Prompt

---

### Fields

| # | Label | Fieldname | Fieldtype | Options/Values | Mandatory | Default | Notes |
|---|-------|-----------|-----------|----------------|-----------|---------|-------|
| 1 | | | | | | | |

(Include Section Break, Column Break, Tab Break rows to document layout)

---

### Form Layout

SECTION: [Name] | collapsible: No
  ROW: field_a ──── field_b
  ROW: field_c (full width)

SECTION: [Name] | collapsible: Yes
  ROW: field_d ──── field_e

---

### List View

Columns (in_list_view):
- [field 1]
- [field 2]
- [status]

Standard Filters: [field], [field]
Default Sort: creation DESC
Status Indicators: Draft=grey, Approved=green, Rejected=red

---

### Permissions

| Role | Read | Write | Create | Delete | Submit | Cancel | If Owner | Notes |
|------|------|-------|--------|--------|--------|--------|----------|-------|
| | | | | | | | | |

---

### Approval / Workflow

[ ] No approval (plain save)
[ ] Simple submit/cancel (DocStatus only)
[ ] Multi-stage workflow

Workflow State Field: _____________

States:
| State | Doc Status | Color | Is Optional | Updates Field | With Value |
|-------|-----------|-------|-------------|---------------|------------|

Transitions:
| From State | Action | To State | Who Can Do It | Condition |
|-----------|--------|----------|---------------|-----------|

---

### Controller Logic

- On validate: ___________
- On submit: ___________
- On cancel: ___________

---

### Links to Other DocTypes

| Field | Links To | Fetch Fields |
|-------|----------|--------------|

---

### Child Tables

| Child Table DocType | Fieldname | Purpose |
|--------------------|-----------|---------|

---

### Sidebar Setup (v16)

App name in hooks.py: ___________
Workspace name: ___________
Workspace Sidebar name: ___________
Desktop Icon (parent) name: ___________
Roles that need sidebar access: ___________

---

### Open Questions

List anything not yet decided.
```

---

## Part 13: Golden Rules

1. **Spec first, code never.** No developer starts without a completed spec.

2. **One workflow per DocType.** Only one workflow can be active. Two workflows = two DocTypes.

3. **Workflow state field is always `status`.** Unless there's a strong reason otherwise.

4. **Never `db_set` the status field.** Use `apply_workflow(doc, action)` instead.

5. **All transactional DocTypes are submittable.** If it represents a decision or transaction, it needs docstatus.

6. **Name states like a person would say them.** "Pending CEO Approval" not "STATE_4".

7. **Optional states for terminal non-approval paths.** Rejected, Withdrawn, Expired → `is_optional_state: 1`.

8. **Permissions must match the workflow.** If a role triggers "Approve", they need `write: 1` on the DocType. Workflow transitions fail silently without it.

9. **In v16, `has_permission` hooks must explicitly return True.** Not None. Not a truthy object. Literally `return True`.

10. **The Workspace Sidebar DocType ≠ the Workspace.** Creating one does not link to the other. Desktop Icons are the connector. Don't skip them.

11. **app_data_map is case-sensitive.** Your `add_to_apps_screen["name"]` must be all-lowercase to match `frappe.current_app`. Verify in browser console before debugging anything else.

12. **A workspace is invisible unless a role has read permission on at least one DocType in it.** Reports and pages alone don't count.

13. **Shared client-side logic across DocTypes must use `frappe.provide`, never `window.*`.** If a spec calls for a helper function reused across multiple DocType JS files (formatters, validation helpers, common API wrappers), the spec must explicitly state: "implement as `frappe.provide('myapp.utils')` in a shared bundle loaded via `app_include_js` in `hooks.py`." Do not leave this implicit — Claude and Cursor will default to `window.my_fn` otherwise, causing ESLint errors and namespace pollution across every DocType that consumes it. Shared Python utilities follow the same principle: extract to a module (e.g., `myapp/utils/grant_utils.py`) and import explicitly — never monkey-patch `frappe` globals.

---

## Part 14: Quick Reference

### Most Common Field Combinations

**Status (workflow-driven):**
```json
{"fieldname":"status","fieldtype":"Select","options":"Draft\nPending Review\nApproved\nRejected","default":"Draft","read_only":1,"in_list_view":1}
```

**Link with fetch:**
```json
[
  {"fieldname":"ngo","fieldtype":"Link","options":"NGO","reqd":1},
  {"fieldname":"ngo_name","fieldtype":"Data","fetch_from":"ngo.ngo_name","read_only":1}
]
```

**Conditional field:**
```json
{"fieldname":"rejection_reason","fieldtype":"Small Text","depends_on":"eval: doc.status == 'Rejected'","mandatory_depends_on":"eval: doc.status == 'Rejected'"}
```

**Section with two columns:**
```json
[
  {"fieldtype":"Section Break","label":"Financials"},
  {"fieldname":"amount","fieldtype":"Currency","reqd":1},
  {"fieldtype":"Column Break"},
  {"fieldname":"currency","fieldtype":"Link","options":"Currency","default":"INR"}
]
```

---

### Python API Quick Reference

```python
# Get a document
doc = frappe.get_doc("Grant Application", "GA-2024-0001")

# Create new
doc = frappe.get_doc({"doctype": "Grant Application", "title": "Water Project"})
doc.insert()

# Query
results = frappe.get_list("Grant Application",
    filters={"status": "Approved"},
    fields=["name", "title", "grant_amount"],
    order_by="creation desc",
    limit=20
)

# Update field (bypass validation — use carefully)
frappe.db.set_value("Grant Application", "GA-2024-0001", "status", "Approved")

# Apply workflow action
from frappe.model.workflow import apply_workflow
apply_workflow(doc, "Approve")

# Get workflow state
from frappe.model.workflow import get_doc_workflow_state
state = get_doc_workflow_state(doc)
```
