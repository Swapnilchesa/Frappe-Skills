# India Unified Admin Hierarchy — TopoJSON

Canonical, web-optimised GeoJSON/TopoJSON for India's three-level admin hierarchy (State → District → CD Block), LGD-keyed throughout. Built for Frappe / mGrant drill-down dashboards but usable anywhere.

## Files

| File | Features | Size | jsDelivr URL |
|---|---:|---:|---|
| `topo/states.json` | 36 | 198 KB | `https://cdn.jsdelivr.net/gh/Swapnilchesa/Frappe-Skills@main/assets/india-admin-geo/topo/states.json` |
| `topo/districts.json` | 780 | 1.66 MB | `https://cdn.jsdelivr.net/gh/Swapnilchesa/Frappe-Skills@main/assets/india-admin-geo/topo/districts.json` |
| `topo/blocks.json` | 6,803 | 5.59 MB | `https://cdn.jsdelivr.net/gh/Swapnilchesa/Frappe-Skills@main/assets/india-admin-geo/topo/blocks.json` |

Pin a specific commit/tag for production: replace `@main` with `@v1.0.0` (or the short SHA).

jsDelivr auto-serves gzipped (~230 KB / ~540 KB / ~1.5 MB over wire).

## Attribute schema

```jsonc
// states
{ "state_name": "Madhya Pradesh", "state_lgd": "23" }

// districts
{ "state_name": "Madhya Pradesh", "state_lgd": "23",
  "district_name": "Bhopal",     "district_lgd": "433" }

// blocks
{ "block_name": "Phanda", "block_shape_id": "7132399B...",
  "state_name": "Madhya Pradesh", "state_lgd": "23",
  "district_name": "Bhopal",      "district_lgd": "433" }
```

Every block carries its full LGD parent chain. Client-side drill-down is one `.filter()` per level.

TopoJSON object names: `topo.objects.states`, `topo.objects.districts`, `topo.objects.blocks`.

## Download & install (Frappe app)

```bash
mkdir -p apps/<app>/<app>/public/geo
cd apps/<app>/<app>/public/geo
for f in states districts blocks; do
  curl -sSL -o "${f}.json" \
    "https://cdn.jsdelivr.net/gh/Swapnilchesa/Frappe-Skills@main/assets/india-admin-geo/topo/${f}.json"
done
cd -
bench build --app <app>
```

Then reference as `/assets/<app>/geo/states.json` etc. inside the Custom HTML Block. No runtime CDN dependency.

## Runtime / CDN mode (prototypes only)

Set `GEO = "https://cdn.jsdelivr.net/gh/Swapnilchesa/Frappe-Skills@main/assets/india-admin-geo/topo"` in the CHB. One-line switch. Not recommended for production (third-party uptime, no version control over the data pipeline).

## Provenance

- **State + district geometry + LGD codes:** Survey of India-style shapefiles, reprojected from Lambert Conformal Conic to EPSG:4326, disputed polygons removed, state-LGD dictionary applied.
- **Block geometry:** geoBoundaries-style GeoJSON, re-parented onto the above districts via centroid-in-polygon spatial join (EPSG:6933 equal-area centroids → EPSG:4326 → `sjoin` within, fallback `sjoin_nearest`).
- **Simplification:** states at ~0.01° (~1 km), districts at ~0.003° (~300 m), blocks at source resolution.

## Known residual gaps

1. `Preet Vihar` block in Delhi has null `district_lgd`. Either hardcode override to East Delhi (`0174`) or filter out.
2. Newly-created districts (MP's Mauganj/Pandhurna/Maihar, Rajasthan 2023 splits) — covered (780 districts vs geoBoundaries' 735).
3. `block_shape_id` preserved for traceability; LGD is the canonical join key.

## License

Data is a derivative of geoBoundaries (ODbL-1.0) and Survey of India (open). Redistribution under **ODbL-1.0**. Credit: geoBoundaries + Survey of India + dhwaniris/Frappe-Skills.

## Versioning

See `version.json`. Bump on any upstream data refresh or schema change.
