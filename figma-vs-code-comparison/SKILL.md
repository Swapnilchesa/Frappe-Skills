---
name: figma-vs-code-comparison
description: >
  ALWAYS use this skill whenever a Figma URL and a code repository (Angular, React, or any
  framework) are both present in the task — especially for pixel comparison, design audit, UI
  bug fixing, or implementing Figma designs into code. Triggers include: "compare Figma with
  code", "make the UI match Figma", "pixel-perfect fix", "design audit", "Figma vs code review",
  "implement Figma design", or any time a Figma link appears alongside a repo URL or token.
  Also triggers when the user says things like "fix the header/footer/map to match the design"
  even without explicitly mentioning Figma — if a Figma file is in the project context, assume
  it is the source of truth and apply this skill immediately. Do not wait for an explicit request.
  PREREQUISITE: Before any execution, read references/autoresearch-integration.md and run the
  three-phase autoresearch setup described there.
---

# Figma vs Code Comparison Skill

Eliminate errors when comparing a Figma design to a codebase, producing a discrepancy report,
and implementing fixes. This skill exists because of real, documented mistakes — read the
Post-Mortem before doing anything.

---

## ⚡ Autoresearch Prerequisite

**Before touching any file or calling any Figma tool, read and follow:**
→ `references/autoresearch-integration.md`

This is a BLOCKING step. It runs `/autoresearch:predict` to surface SCSS cascade chains and
component ownership before you call `get_design_context`, then wraps fixes in `/autoresearch:fix`
to auto-revert regressions, then gates commits with `/autoresearch:ship --checklist-only`.

Skipping it is the single fastest way to produce a fix that silently evaporates due to a global
override you didn't know existed.

---

## Post-Mortem: What Goes Wrong (and Why)

In the GPZL project, four incorrect values were committed in a single session:

| What was written | What Figma actually said | Root cause |
|---|---|---|
| `font-weight: 400` on hero title | `font-semibold` = **600** | Figma never consulted |
| Footer Topics: 5 invented items | Exactly **3 items**, specific text | Inferred from a comparison doc |
| Footer Explore: "Submit a Publication" | **"Research and Evidence"** | Paraphrased instead of reading |
| Global `h1/h2/h3 { font-weight: 400 }` | Not in Figma at all | Generalised a component-level value |

**Single root cause:** A secondary document was used as the spec instead of the live Figma.
One flawed intermediary plus blind execution compounded into hours of re-inspection and revert work.

**The rule:** The live Figma node is always the spec. Every other document — including this one —
is secondary. If there is any conflict, Figma wins.

---

## Protocol (Non-Negotiable)

### Step 1 — Extract Figma coordinates from the URL

```
https://www.figma.com/design/SREibQZ7QXnJ3YlZMVpq1d/GPZL?node-id=14-276
                             ↑ fileKey                          ↑ nodeId (replace - with :)
fileKey = SREibQZ7QXnJ3YlZMVpq1d
nodeId  = 14:276
```

If no `node-id` is in the URL, call `get_metadata` on the file first to locate the correct node ID.

---

### Step 2 — Call `get_design_context` before touching any file

```
Figma:get_design_context(
  fileKey: "...",
  nodeId:  "...",
  clientFrameworks: "angular",      ← or react, vue, etc.
  clientLanguages:  "typescript,scss"
)
```

**This is not optional even if you think you know the design.** Designs change. Memory is wrong.
Cached comparison documents are wrong. The live Figma call is the only valid source.

Extract and record these values explicitly before proceeding:

| Property | How it appears in Figma output | SCSS equivalent |
|---|---|---|
| Font weight | `font-semibold` / `font-bold` / `font-normal` / `font-extrabold` | 600 / 700 / 400 / 800 |
| Font size | `text-[56px]` | `font-size: 56px` |
| Color | `bg-[#007297]` or `var(--secondary/main, #007297)` | hex or SCSS token |
| Border radius | `rounded-[8px]` | `border-radius: 8px` |
| Spacing / gap | `gap-[58px]`, `px-[12px] py-[9px]` | `gap: 58px`, `padding: 9px 12px` |
| Exact text | String literals in the Figma output | Copy verbatim — never paraphrase |
| Border | `border-b-2` | `border-bottom: 2px solid` |

---

### Step 3 — State the delta explicitly before writing anything

1. Open the relevant component file.
2. Find the current value.
3. State the comparison out loud:

> "Figma says `font-weight: 600`. Code has `font-weight: 400`. Changing."

If there is no delta — code already matches Figma — **do not touch the file.**

---

### Step 4 — Write only what Figma confirms

- **Do not infer.** If Figma shows 3 footer links, write exactly 3.
- **Do not globalise.** Apply values to the specific selector, not to `h1 { }` globally — unless `get_variable_defs` confirms a global design system token.
- **Do not paraphrase content.** Copy nav labels, button text, and headings character-for-character.
- **Check SCSS tokens first.** Before hardcoding `#007297`, check `_theme.scss` / `styles.scss` for an existing variable.

---

### Step 5 — Verify and commit

Re-read the modified file. Confirm each changed value matches Figma output.

Commit message format:
```
fix(component): match Figma node {nodeId} — {exact values changed}

# Examples:
fix(footer): match Figma node 823:694 — 3 explore links, 3 topic items, exact text
fix(hero): revert font-weight to 600 per Figma node 225:1661 font-semibold
```

One logical concern per commit. Never batch unrelated visual changes.

---

## Comparison Report Format

When the task is a **design audit** (compare Figma vs code, produce a report):

```markdown
# {Project} — Figma vs Code Comparison Report

**Source:** Figma {version/page} (node `{id}`, section "{name}")
**Codebase:** `{repo}` ({framework})
**Date:** {date}

## Summary Verdict
[One paragraph: structural match, nature of gaps, estimated fix effort]

## Page-by-Page Discrepancies

### {Page Name}

| Area | Figma | Current Code | Severity |
|---|---|---|---|
| {component} | {what Figma shows} | {what code does} | 🔴/🟡/🟢 |

## Global / Cross-Cutting Issues

| Issue | Details | Severity |
|---|---|---|

## Priority Fix Order
1. {highest impact, lowest effort}

## Open Questions
1. {blockers requiring product/design decision}
```

**Severity:**

| Marker | Meaning |
|---|---|
| 🔴 Critical | Feature gap — functionality missing entirely |
| 🔴 High | Clearly wrong, visible on first load, affects usability |
| 🟡 Medium | Visual mismatch, noticeable but not broken |
| 🟢 Low | Minor polish, unlikely to be noticed without side-by-side |

---

## Tool Selection Guide

| Tool | When to use |
|---|---|
| `get_metadata` | Have page/section node ID, need to find child component node IDs |
| `get_design_context` | Have the specific node ID — use before implementing any section |
| `get_variable_defs` | Need to check if a global design token governs a style |
| `get_screenshot` | Need a visual reference alongside the code output |

Typical flow for a full page audit:
1. `get_metadata(pageNodeId)` → find child frame IDs
2. `get_design_context(sectionNodeId)` for each section
3. Audit code against extracted values → produce report

---

## Handling Large `get_design_context` Output

```bash
# Find all font-weight tokens
grep -E "font-semibold|font-bold|font-normal|font-extrabold" /path/to/output.json

# Find all colour values
grep -oE '#[0-9a-fA-F]{3,6}' /path/to/output.json | sort -u

# Extract border-radius values
grep -oE 'rounded-\[[^\]]+\]' /path/to/output.json
```

Never skip the Figma read because the output was large. Parse it.

---

## Red Flags — Stop and Re-Read Figma

Stop immediately and call `get_design_context` if you notice any of these:

- You are about to write link text, nav labels, or button copy from memory
- You are about to apply a style globally based on seeing it on one component
- You are about to add items to a list you didn't see explicitly in the design
- More than 20 minutes have passed since you last called `get_design_context`
- You are referencing a comparison document instead of the live Figma
- You are about to guess at a value because "it looks about right"

---

## Pre-Commit Checklist

```
□ Ran autoresearch prerequisite (references/autoresearch-integration.md)
□ Called get_design_context for this specific section's node ID
□ Extracted exact values: font-weight, colors, text content, border-radius, spacing
□ Checked for existing SCSS tokens before hardcoding hex values
□ Compared against current code — stated the delta explicitly
□ Changed only what Figma confirmed — nothing inferred, nothing generalised
□ Did not paraphrase any content strings
□ Re-read the modified file — every changed value matches Figma output
□ Commit message names the Figma node ID and exact values changed
□ /autoresearch:ship --checklist-only passed
```

---

## Reference: Common Angular/SCSS Token Mapping

| Figma token | SCSS |
|---|---|
| `font-semibold` | `font-weight: 600` |
| `font-bold` | `font-weight: 700` |
| `font-extrabold` | `font-weight: 800` |
| `font-normal` | `font-weight: 400` |
| `text-[14px]` | `font-size: 14px` |
| `leading-[1.5]` | `line-height: 1.5` |
| `rounded-[8px]` | `border-radius: 8px` |
| `gap-[58px]` | `gap: 58px` |
| `px-[12px] py-[9px]` | `padding: 9px 12px` |
| `bg-[#007297]` | `background: #007297` (or token) |
| `border-b-2` | `border-bottom: 2px solid` |
| `w-[63%]` | `width: 63%` |
| `opacity-[0.8]` | `opacity: 0.8` |
