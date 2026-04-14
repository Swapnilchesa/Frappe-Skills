# Frappe whitelisted server method — data for mGrant drill-down map.
# Copy into: apps/<app>/<app>/api.py
# The CHB calls: frappe.call({method:"<app>.api.map_metrics", args:{level, state_lgd?, district_lgd?}})
#
# Edit the CONFIG block below to match your DocType schema.
# The return shape MUST match the HOVER_FIELDS picked in the skill's Phase 1 clarify step —
# every key the CHB's hover card references must appear in each row.

import frappe
from frappe import _

# ============ CONFIG — edit these ============
GRANT_DOCTYPE        = "Grant"              # name of the DocType carrying records
STATE_LGD_FIELD      = "state_lgd"          # string, zero-padded ("23")
DISTRICT_LGD_FIELD   = "district_lgd"       # string
BLOCK_KEY_FIELD      = "block_shape_id"     # matches block_shape_id in blocks.topojson
METRIC_FIELD         = "sanctioned_amount"  # numeric field to aggregate
METRIC_AGG           = "sum"                # sum | count | count_distinct | avg
GRANTEE_FIELD        = "grantee"            # link/data field — used for DISTINCT grantee count
PORTFOLIO_FIELD      = "programme_area"     # categorical — feeds the chips row
DISBURSED_FIELD      = "disbursed_amount"   # optional secondary metric; set None to skip
LAST_DISBURSED_FIELD = "last_disbursed_on"  # optional Date; set None to skip
ASPIRATIONAL_DOCTYPE = "Aspirational District"  # has district_lgd field; None to skip
# =============================================


def _agg(field, alias):
    if METRIC_AGG == "sum":            return f"COALESCE(SUM(`{field}`),0) AS {alias}"
    if METRIC_AGG == "count":          return f"COUNT(*) AS {alias}"
    if METRIC_AGG == "count_distinct": return f"COUNT(DISTINCT `{field}`) AS {alias}"
    if METRIC_AGG == "avg":            return f"COALESCE(AVG(`{field}`),0) AS {alias}"
    raise ValueError("bad METRIC_AGG")


@frappe.whitelist()
def map_metrics(level, state_lgd=None, district_lgd=None):
    """
    Returns: list of dicts, one per geography at the requested level:
        { key, metric, disbursed?, grantees, grants_count, portfolios:[{name,count}],
          aspirational, last_disbursed_on? }
    `key` is the LGD code (or block_shape_id at block level) that the CHB uses to
    join the row onto the topojson feature.
    """
    tbl = f"`tab{GRANT_DOCTYPE}`"
    conds = ["1=1"]
    params = {}

    if level == "country":
        group_field = STATE_LGD_FIELD
    elif level == "state":
        group_field = DISTRICT_LGD_FIELD
        conds.append(f"`{STATE_LGD_FIELD}` = %(state_lgd)s")
        params["state_lgd"] = state_lgd
    elif level == "district":
        group_field = BLOCK_KEY_FIELD
        conds.append(f"`{STATE_LGD_FIELD}` = %(state_lgd)s")
        conds.append(f"`{DISTRICT_LGD_FIELD}` = %(district_lgd)s")
        params["state_lgd"] = state_lgd
        params["district_lgd"] = district_lgd
    else:
        frappe.throw(_("Bad level"))

    where = " AND ".join(conds)

    extra_cols = ""
    if DISBURSED_FIELD:
        extra_cols += f", {_agg(DISBURSED_FIELD, 'disbursed')}"
    if LAST_DISBURSED_FIELD:
        extra_cols += f", MAX(`{LAST_DISBURSED_FIELD}`) AS last_disbursed_on"

    rows = frappe.db.sql(f"""
        SELECT `{group_field}` AS `key`,
               {_agg(METRIC_FIELD, 'metric')},
               COUNT(DISTINCT `{GRANTEE_FIELD}`) AS grantees,
               COUNT(*) AS grants_count
               {extra_cols}
        FROM {tbl}
        WHERE {where} AND `{group_field}` IS NOT NULL
        GROUP BY `{group_field}`
    """, params, as_dict=True)

    portfolios = frappe.db.sql(f"""
        SELECT `{group_field}` AS `key`, `{PORTFOLIO_FIELD}` AS name, COUNT(*) AS count
        FROM {tbl}
        WHERE {where} AND `{group_field}` IS NOT NULL AND `{PORTFOLIO_FIELD}` IS NOT NULL
        GROUP BY `{group_field}`, `{PORTFOLIO_FIELD}`
        ORDER BY count DESC
    """, params, as_dict=True)

    asp_set = set()
    if ASPIRATIONAL_DOCTYPE and level in ("state", "district"):
        try:
            asp_set = {r.district_lgd for r in frappe.get_all(
                ASPIRATIONAL_DOCTYPE, fields=["district_lgd"])}
        except Exception:
            pass

    by_key = {r["key"]: {**r, "portfolios": [], "aspirational": False} for r in rows}
    for p in portfolios:
        if p["key"] in by_key:
            by_key[p["key"]]["portfolios"].append({"name": p["name"], "count": p["count"]})

    if level == "state":
        for k, v in by_key.items():
            v["aspirational"] = k in asp_set

    return list(by_key.values())
