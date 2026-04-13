# Field Type Reference

> Full field type tables for Frappe DocType design.
> Referenced from SKILL.md Part 2 — read when speccing fields.

---

## Data / Text Fields

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

## Number Fields

| Fieldtype | DB Type | Use When |
|---|---|---|
| `Int` | int | Whole numbers |
| `Float` | decimal(21,9) | Decimal numbers |
| `Currency` | decimal(21,9) | Money (shows currency symbol) |
| `Percent` | decimal(21,9) | Percentage (0–100) |
| `Rating` | decimal(3,1) | Star rating (0–5) |
| `Duration` | int | Timespan in seconds |

## Date / Time Fields

| Fieldtype | DB Type | Use When |
|---|---|---|
| `Date` | date | Date only |
| `Time` | time | Time only |
| `Datetime` | datetime | Date + time |

## Selection Fields

| Fieldtype | DB Type | Use When |
|---|---|---|
| `Select` | varchar(140) | Fixed dropdown; options = newline-separated values |
| `Check` | int(1) | Boolean checkbox |
| `Autocomplete` | varchar(140) | Text with suggestions |

## Relationship Fields

| Fieldtype | DB Type | Use When |
|---|---|---|
| `Link` | varchar(140) | Link to another DocType |
| `Dynamic Link` | varchar(140) | Link to any DocType; type from another field |
| `Table` | — | Embed child DocType as rows |
| `Table MultiSelect` | — | Multi-select using a child DocType |

## Layout / Structural (no DB column)

| Fieldtype | Purpose |
|---|---|
| `Section Break` | Horizontal divider; starts a new section |
| `Column Break` | Splits a section into columns |
| `Tab Break` | Creates a new tab in the form (v14+) |
| `Fold` | Collapses section by default |
| `HTML` | Raw HTML injection |
| `Heading` | Bold title text |

## File / Media Fields

| Fieldtype | DB Type | Use When |
|---|---|---|
| `Attach` | text | Any file attachment |
| `Attach Image` | text | Images only |
| `Image` | text | Renders image from Attach Image field |
| `Signature` | text | Digital signature capture |
| `Barcode` | text | Barcode display |

## Special Fields

| Fieldtype | DB Type | Use When |
|---|---|---|
| `JSON` | json | Store structured data |
| `Color` | varchar(140) | Color picker |
| `Phone` | varchar(140) | Phone number |
| `Geolocation` | text | Map/coordinates |

---

## Key DocField Properties

| Property | Description |
|---|---|
| `label` | Human-readable UI label |
| `fieldname` | snake_case; becomes DB column and Python attribute |
| `fieldtype` | Type from tables above |
| `reqd` | 1 = mandatory |
| `default` | Default value on new document |
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
| `fetch_from` | Auto-populate from linked doc: `link_field.field_on_linked_doc` |

---

## v16 Field Changes

- **Data field preset options:** fieldtype `Data` Options becomes a dropdown: Email, Name, Phone, URL, Barcode, IBAN.
- **Filter operators in plain language:** `!=` shows as "not equals" in list UI.
- **Default sort changed to `creation`:** All list views sort by `creation` in v16 (was `modified`).
- **UUID naming rule added:** `autoname = "UUID"` for globally unique IDs.

---

## Most Common Field Combinations

**Status field (workflow-driven):**
```json
{"fieldname":"status","fieldtype":"Select","options":"Draft\nPending Review\nApproved\nRejected","default":"Draft","read_only":1,"in_list_view":1}
```

**Link with auto-fetch:**
```json
[
  {"fieldname":"ngo","fieldtype":"Link","options":"NGO","reqd":1},
  {"fieldname":"ngo_name","fieldtype":"Data","fetch_from":"ngo.ngo_name","read_only":1}
]
```

**Conditional mandatory field:**
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
