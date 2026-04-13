# v16 Sidebar — Complete Guide

> Step-by-step sidebar setup for Frappe v16 + all known bugs and fixes.
> Referenced from SKILL.md Part 11 — read before any sidebar spec or debugging.

---

## What Changed in v16

| Aspect | v15 | v16 |
|---|---|---|
| Navigation model | Module-based tabs | App-based persistent sidebar |
| Sidebar type | Left panel, auto from module | Left panel, powered by `Workspace Sidebar` DocType |
| Form/List detail sidebar | Left side | **RIGHT side (moved)** |
| App switcher | Not present | Top-left icon, switches entire sidebar context |
| `Workspace Sidebar` DocType | Not present | New — must be created explicitly |
| Private workspaces | Mixed with shared | Moved to "My Workspaces" virtual app |

---

## Step-by-Step Setup Sequence

Follow this **exact order**. Doing steps out of order is the primary cause of blank sidebars.

---

### Step 1: hooks.py — Register the App

```python
# apps/your_app/your_app/hooks.py
add_to_apps_screen = [
    {
        "name": "your_app",     # MUST be all-lowercase — see Bug #1
        "logo": "/assets/your_app/images/logo.png",
        "title": "Your App Title",
        "route": "/app/your-workspace-name",
    }
]
```

```bash
bench --site {site} clear-cache
bench --site {site} build  # if assets changed
```

---

### Step 2: Verify Module Definition

1. Desk → Module Def → confirm your module exists, `app_name` matches folder
2. On the target user's User record → Allow Modules → add your module

---

### Step 3: Create/Verify Workspace

1. Desk → Workspace → New (or open existing)
2. Set: Name, Module, **Is Standard: checked**, Restrict To Domain: blank
3. Add Shortcuts to your DocTypes/reports
4. Save

> The workspace alone is not enough for the sidebar. Steps 4 and 5 are required.

---

### Step 4: Create Workspace Sidebar (NEW in v16 — most missed step)

`Workspace Sidebar` is a **separate DocType** from `Workspace`.

1. Desk → Workspace Sidebar → New
2. Name it (e.g., "Grant Management Sidebar")
3. Add items in the Items table:

| Link To | Type | Label |
|---|---|---|
| Grant Application | DocType | Grant Applications |
| Grant Report | Report | Monthly Report |
| Grant Settings | Page | Settings |

4. Save

> This record does NOT auto-link to the Workspace. Desktop Icons (Step 5) are the connector.

---

### Step 5: Create Desktop Icons — Two Required

**Icon A (Parent — App entry):**

| Field | Value |
|---|---|
| Icon Type | App |
| Link Type | External |
| Logo URL | `/assets/your_app/images/logo.png` |
| Label | Your App Name |
| Link | `/app/your-workspace-name` |

Save → note the record name.

**Icon B (Child — Sidebar entry):**

| Field | Value |
|---|---|
| Icon Type | Link |
| Link Type | Workspace Sidebar |
| App | your_app (lowercase) |
| Parent Icon | [name of Icon A] |
| Link To | [name of Workspace Sidebar from Step 4] |
| Logo URL | module icon URL |

---

### Step 6: Role Permissions on Workspace

- Each role that needs sidebar access must have `read: 1` on at least one DocType in the sidebar
- In Workspace record → Roles table → add the roles that should see this workspace
- Check: module is in Allow Modules on the user's profile

---

### Step 7: Clear Cache

```bash
bench --site {site} clear-cache
# Browser: Ctrl+Shift+R
```

---

## Verification Checklist

```
[ ] hooks.py has add_to_apps_screen with lowercase name
[ ] bench clear-cache run after hooks.py change
[ ] Module Def exists and app_name is correct
[ ] User's Allow Modules includes the module
[ ] Workspace exists, Is Standard checked, module set correctly
[ ] Workspace Sidebar DocType created with items
[ ] Desktop Icon (parent, type=App) created
[ ] Desktop Icon (child, type=Link, Link Type=Workspace Sidebar) created, Parent Icon set
[ ] User role has read permission on at least one DocType in the sidebar
[ ] Workspace Roles table has the correct roles
[ ] Browser hard-refreshed after all changes
[ ] Browser console checked: frappe.boot.app_data_map casing verified
```

---

## Known Bugs and Fixes

### Bug #1: Case-Sensitivity in app_data_map (Most Common)

**Symptom:** Sidebar goes blank when opening a DocType. Console:
```
Uncaught TypeError: Cannot read properties of undefined (reading 'workspaces')
at Sidebar.make_sidebar
```

**Root Cause:** `frappe.boot.app_data_map` uses original casing from hooks.py, but `frappe.current_app` returns lowercase. Mismatch → `undefined`.

**Diagnose:**
```javascript
console.log(Object.keys(frappe.boot.app_data_map))
console.log(frappe.current_app)
```

**Fix A (correct):** Set `add_to_apps_screen["name"]` to all-lowercase in hooks.py.

**Fix B (hotpatch):** In `frappe/public/js/frappe/desk/sidebar.js`:
```javascript
// Replace:
let app_workspaces = frappe.boot.app_data_map[frappe.current_app || "frappe"].workspaces;
// With:
let current_app_key = frappe.current_app || "frappe";
let exact_key = Object.keys(frappe.boot.app_data_map)
    .find(k => k.toLowerCase() === current_app_key.toLowerCase()) || "frappe";
let app_workspaces = frappe.boot.app_data_map[exact_key].workspaces;
```
Run `bench build` after. Note: overwritten on bench update.

---

### Bug #2: Workspace Invisible to Non-Admin Users

**Symptom:** Workspace doesn't appear for non-admin roles despite module being enabled.

**Root Cause:** Frappe only marks a module as "allowed" if the user has read permission on at least one DocType in that module. Reports/pages alone don't count.

**Fix:** Add a read permission row for the user's role on at least one DocType in the workspace.

---

### Bug #3: Custom Workspace Only Visible to System Manager

**Symptom:** Workspace created by admin is admin-only.

**Root Cause:** `Is Standard = 0` workspace with no explicit role sharing.

**Fix:** Workspace record → Roles table → add roles that should see it.

---

### Bug #4: App Doesn't Load on First Click

**Symptom:** First click navigates to wrong URL. Second click works.

**Root Cause:** `hooks.py` `route` doesn't match the workspace route → redirect loop.

**Fix:** Set `"route"` to exact workspace URL: `/app/grant-management`.

---

### Bug #5: Sidebar Toggle Affects Form Sidebar

**Symptom:** Toggling sidebar off on list view removes Assign/Attach/Timeline from form.

**Root Cause:** Known Frappe bug (issue #8956). localStorage sidebar state not scoped to view type.

**Fix/Workaround:** Instruct users to use Ctrl+Shift+R. Or apply custom JS to reset sidebar state on form load.

---

### Bug #6: Workspace Sidebar Not Attached (zero-config trap)

**Symptom:** Workspace Sidebar created with items, workspace exists, but sidebar items don't appear.

**Root Cause:** `Workspace Sidebar` DocType does NOT auto-link to Workspace. The connector is Desktop Icons. Most developers miss this entirely.

**Fix:** Follow Step 5 — create both Desktop Icons (parent App + child Link).
