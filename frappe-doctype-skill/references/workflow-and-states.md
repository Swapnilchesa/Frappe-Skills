# Workflow & States Reference

> Complete workflow JSON, approval state patterns, list view config, and troubleshooting.
> Referenced from SKILL.md Parts 8–9 — read when designing approval flows or list views.

---

## DocStatus vs Workflow — When to Use Each

| Scenario | Use |
|---|---|
| One approval moment, one role, no routing | DocStatus only (`is_submittable: 1`) |
| Multiple roles, multiple stages, conditional routing | Frappe Workflow |
| Email alerts at each stage | Frappe Workflow |
| Audit trail of who approved what | Frappe Workflow + `update_field` |

---

## DocStatus Reference

| docstatus | State | Editable? |
|---|---|---|
| 0 | Draft | Yes |
| 1 | Submitted | No (locked) |
| 2 | Cancelled | No |

---

## Workflow State Field (required for every workflow DocType)

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

---

## Complete Workflow JSON Template

```json
{
  "doctype": "Workflow",
  "name": "Grant Application Approval",
  "document_type": "Grant Application",
  "is_active": 1,
  "workflow_state_field": "status",
  "send_email_alert": 1,
  "states": [
    {"state": "Draft",          "doc_status": "0", "color": "Gray"},
    {"state": "Pending Review", "doc_status": "0", "color": "Orange"},
    {"state": "Approved",       "doc_status": "1", "color": "Green",
     "update_field": "approved_by", "update_value": "{frappe.session.user}"},
    {"state": "Rejected",       "doc_status": "2", "color": "Red",
     "is_optional_state": 1}
  ],
  "transitions": [
    {"state": "Draft",          "action": "Submit for Review", "next_state": "Pending Review",
     "allowed": "Grant Applicant"},
    {"state": "Pending Review", "action": "Approve",           "next_state": "Approved",
     "allowed": "Grant Manager"},
    {"state": "Pending Review", "action": "Reject",            "next_state": "Rejected",
     "allowed": "Grant Manager"},
    {"state": "Pending Review", "action": "Request Changes",   "next_state": "Draft",
     "allowed": "Grant Manager"}
  ]
}
```

### Conditional Routing (amount-based escalation)

```json
{
  "state": "Pending Review",
  "action": "Escalate to CEO",
  "next_state": "Pending CEO Approval",
  "allowed": "Grant Manager",
  "condition": "doc.requested_amount > 5000000"
}
```

### Multi-Stage Example (3-tier)

```json
"transitions": [
  {"state": "Draft",                "action": "Submit",     "next_state": "Program Officer Review", "allowed": "Applicant"},
  {"state": "Program Officer Review","action": "Recommend", "next_state": "Manager Approval",       "allowed": "Program Officer"},
  {"state": "Program Officer Review","action": "Return",    "next_state": "Draft",                  "allowed": "Program Officer"},
  {"state": "Manager Approval",     "action": "Approve",   "next_state": "Approved",               "allowed": "Grant Manager"},
  {"state": "Manager Approval",     "action": "Escalate",  "next_state": "CEO Approval",           "allowed": "Grant Manager",
   "condition": "doc.requested_amount > 10000000"},
  {"state": "Manager Approval",     "action": "Reject",    "next_state": "Rejected",               "allowed": "Grant Manager"},
  {"state": "CEO Approval",         "action": "Approve",   "next_state": "Approved",               "allowed": "CEO"},
  {"state": "CEO Approval",         "action": "Reject",    "next_state": "Rejected",               "allowed": "CEO"}
]
```

---

## Workflow Python API

```python
# Apply a workflow action programmatically
from frappe.model.workflow import apply_workflow
apply_workflow(doc, "Approve")

# Get current workflow state
from frappe.model.workflow import get_doc_workflow_state
state = get_doc_workflow_state(doc)

# NEVER do this — bypasses workflow + audit trail:
frappe.db.set_value("Grant Application", name, "status", "Approved")  # ❌
```

---

## Workflow Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| Action buttons not showing | User's role not in any transition `allowed` | Add role to a transition |
| Workflow not applying | Another workflow is active on this DocType | Deactivate old workflow |
| State field not updating | Wrong `workflow_state_field` name | Set correct fieldname |
| Submit button missing | Workflow overrides docstatus submit | Model submit as a workflow transition |
| Email alerts not sending | `send_email_alert` off, or no template linked | Enable + add email template |
| `has_permission` silently blocking (v16) | Hook returns `None` | Change to explicit `return True` |
| Transition condition not evaluating | Syntax error in condition string | Test condition in console: `eval: doc.field > 0` |

---

## List View Configuration

### Field Properties for List View

| Property | Where Set | Effect |
|---|---|---|
| `in_list_view: 1` | On field | Shows as column in list |
| `in_standard_filter: 1` | On field | Adds quick filter at top |
| `in_filter: 1` | On field | Available in filter dropdown |
| `search_index: 1` | On field | Fast DB search |
| `bold: 1` | On field | Column rendered bold |
| `Title Field` | DocType setting | Field renders as document title |

### Recommended List View Spec (include in every spec output)

```
LIST VIEW COLUMNS:
  1. name          — auto-included, shows as document link
  2. status        — in_list_view:1, colour indicator
  3. [reference]   — e.g., ngo_name — in_list_view:1
  4. [key metric]  — e.g., amount — in_list_view:1
  5. modified      — in_list_view:1

DEFAULT SORT: creation DESC (v16 default)

STANDARD FILTERS: status, [date field], [key lookup field]

INDICATORS:
  Draft       → grey
  Pending     → orange
  Approved    → green
  Rejected    → red
```

### Status Indicator Controller Method

```python
def get_indicator(self):
    color_map = {
        "Draft": "grey",
        "Pending Review": "orange",
        "Approved": "green",
        "Rejected": "red"
    }
    return [self.status, color_map.get(self.status, "grey"), "status,=," + self.status]
```

---

## Form Layout Reference

### Layout Rules

- Fields render top-to-bottom inside sections
- `Section Break` = horizontal divider with optional heading
- `Column Break` inside a section = splits into equal-width columns (max 2 recommended)
- `Tab Break` = new tab (use when DocType has 6+ sections)
- v16: **form detail sidebar moved to RIGHT** — avoid dense data in rightmost column

### Layout Notation for Specs

```
SECTION: Basic Information | collapsible: No
  ROW:  title (full width)
  ROW:  ngo ─────────────── program
        (left col)          (right col)

SECTION: Financials | collapsible: No
  ROW:  requested_amount ── currency

SECTION: Approval Info | collapsible: Yes (default collapsed)
  ROW:  approved_by ─────── approval_date
```

### Section Break Properties

| Property | Description |
|---|---|
| `collapsible` | 1 = section is collapsible by user |
| `collapsible_depends_on` | Show collapse only when condition true |
| `description` | Help text for the whole section |

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
  {"fieldname": "approved_by", "fieldtype": "Link", "options": "User", "read_only": 1}
]
```
