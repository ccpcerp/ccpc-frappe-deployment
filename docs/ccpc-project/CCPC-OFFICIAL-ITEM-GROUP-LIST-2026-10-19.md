# CCPC ERPNext — Official Item Group naming standard (v1.2)

**Owner-approved business classification decision:** 2026-10-19 (Asia/Manila).

**Approved target:** exactly **131** distinct Item Group names, each a **leaf Item Group** (ERPNext `is_group=0`) directly below the existing **`All Item Groups`** root (`parent_item_group="All Item Groups"`). **No new/intermediate Parent Item Groups.** The previous "Discussion family" review column is not an ERPNext master field or approved parent.

**Approval scope:** CCPC Item Group names and flat intended hierarchy only. This is **not** verification that any of the 131 names exist on DEVELOPMENT or PRODUCTION, and **does not authorize a bulk import, renaming/merging existing groups, Item reclassification, application code change, Account mapping, site migration or stock/GL operation**. Other business Companies (RMC/GSL/WFC) require their own scope review. Existing names, links, group flags and dependencies must be reconciled read-only in verified DEVELOPMENT first.

**Naming source:** owner's previously corrected 131-name working workbook `CCPC_131_Item_Groups_Spelling_Reviewed_2026-10-19.xlsx`. Final clear spelling correction at officialization: `Canvass & Textile Materials` → `Canvas & Textile Materials`. No other spelling/wording changes, category mergers, deletions or additions; the official list is alphabetized. This master decision supersedes the provisional 42-name and 131-name **review** proposals, but does not change or validate any previously observed 147 Item Group field labels in pasted Item data.

**Manifest SHA256:** `e0c4c3c5f225f60ac2601c838c24f2510462c9d9914daff1cb3cb050b60a19d1` over UTF-8 official names joined by LF with a final LF (no numbering or header).

## Official names — all are planned leaf groups under `All Item Groups`

| No. | Exact official Item Group name | `parent_item_group` | `is_group` |
| ---: | --- | --- | ---: |
| 1 | Abrasives & Grinding Materials | All Item Groups | 0 |
| 2 | Adhesive & Sealants | All Item Groups | 0 |
| 3 | Adhesive & Tapes | All Item Groups | 0 |
| 4 | Automotive Chemicals | All Item Groups | 0 |
| 5 | Automotive Components | All Item Groups | 0 |
| 6 | Automotive Supplies | All Item Groups | 0 |
| 7 | Automotive Wires | All Item Groups | 0 |
| 8 | Batteries | All Item Groups | 0 |
| 9 | Bearings | All Item Groups | 0 |
| 10 | Bearings & Bearing Accessories | All Item Groups | 0 |
| 11 | Beddings & Bedding Fixtures | All Item Groups | 0 |
| 12 | Belts | All Item Groups | 0 |
| 13 | Bolts & Nuts | All Item Groups | 0 |
| 14 | Cabinet & Drawer Accessories | All Item Groups | 0 |
| 15 | Cables & Wires | All Item Groups | 0 |
| 16 | Canvas & Textile Materials | All Item Groups | 0 |
| 17 | Ceiling & Drywall Materials | All Item Groups | 0 |
| 18 | Chains | All Item Groups | 0 |
| 19 | Chains & Fasteners | All Item Groups | 0 |
| 20 | Chemicals | All Item Groups | 0 |
| 21 | Chemicals & Process Materials | All Item Groups | 0 |
| 22 | Cleaning Tools & Supplies | All Item Groups | 0 |
| 23 | Construction Materials | All Item Groups | 0 |
| 24 | Consumables | All Item Groups | 0 |
| 25 | Conveyor Belts Accessories & Components | All Item Groups | 0 |
| 26 | Coupling & Components | All Item Groups | 0 |
| 27 | Couplings | All Item Groups | 0 |
| 28 | Cutting & Drilling Tools | All Item Groups | 0 |
| 29 | Doors & Accessories | All Item Groups | 0 |
| 30 | Electrical | All Item Groups | 0 |
| 31 | Electrical Components | All Item Groups | 0 |
| 32 | Equipment | All Item Groups | 0 |
| 33 | Equipment Components | All Item Groups | 0 |
| 34 | Fasteners | All Item Groups | 0 |
| 35 | Fiber Glass & Composite Materials | All Item Groups | 0 |
| 36 | Filters | All Item Groups | 0 |
| 37 | Filtration Supplies | All Item Groups | 0 |
| 38 | Fire Safety Equipment | All Item Groups | 0 |
| 39 | Fuel System Components | All Item Groups | 0 |
| 40 | Fuels & Petroleum Products | All Item Groups | 0 |
| 41 | Gas Weld & Components | All Item Groups | 0 |
| 42 | Gaskets | All Item Groups | 0 |
| 43 | Gauges & Indicators | All Item Groups | 0 |
| 44 | Glass & Acrylic Materials | All Item Groups | 0 |
| 45 | Glass & Glazing Materials | All Item Groups | 0 |
| 46 | Hand Tools | All Item Groups | 0 |
| 47 | Heavy Equipment Components | All Item Groups | 0 |
| 48 | Hose & Fittings | All Item Groups | 0 |
| 49 | Industrial Gases | All Item Groups | 0 |
| 50 | Instrument | All Item Groups | 0 |
| 51 | Instrument Cables | All Item Groups | 0 |
| 52 | Instrumentation Components | All Item Groups | 0 |
| 53 | Insulation Materials | All Item Groups | 0 |
| 54 | Laboratory Chemicals | All Item Groups | 0 |
| 55 | Laboratory Equipment & Supplies | All Item Groups | 0 |
| 56 | Laboratory Supplies | All Item Groups | 0 |
| 57 | LPG | All Item Groups | 0 |
| 58 | Lube Filters | All Item Groups | 0 |
| 59 | Lubricants | All Item Groups | 0 |
| 60 | Lubricants & Fluids | All Item Groups | 0 |
| 61 | Lubricants & Maintenance Consumables | All Item Groups | 0 |
| 62 | Lubricants & Oil | All Item Groups | 0 |
| 63 | Lubrication Equipment & Accessories | All Item Groups | 0 |
| 64 | Measuring Tools | All Item Groups | 0 |
| 65 | Mechanical Components | All Item Groups | 0 |
| 66 | Mechanical Seals | All Item Groups | 0 |
| 67 | Mechanical Seals & Gaskets | All Item Groups | 0 |
| 68 | Metal Sheets & Plates | All Item Groups | 0 |
| 69 | Motors | All Item Groups | 0 |
| 70 | Nets & Mesh Materials | All Item Groups | 0 |
| 71 | Nylon & Ropes | All Item Groups | 0 |
| 72 | Office Supplies | All Item Groups | 0 |
| 73 | Oil Seals | All Item Groups | 0 |
| 74 | Packaging Materials & Supplies | All Item Groups | 0 |
| 75 | Packaging Supplies | All Item Groups | 0 |
| 76 | Painting Tools & Accessories | All Item Groups | 0 |
| 77 | Paints & Coatings | All Item Groups | 0 |
| 78 | Paints, Coatings & Solvents | All Item Groups | 0 |
| 79 | Pest Control Components | All Item Groups | 0 |
| 80 | Pipes & Fittings | All Item Groups | 0 |
| 81 | Plastic Hoses & Fittings | All Item Groups | 0 |
| 82 | Plastic Sheets | All Item Groups | 0 |
| 83 | Power Transmission | All Item Groups | 0 |
| 84 | PPE | All Item Groups | 0 |
| 85 | Printer Parts & Components | All Item Groups | 0 |
| 86 | Products | All Item Groups | 0 |
| 87 | Pumps | All Item Groups | 0 |
| 88 | R.O. Components | All Item Groups | 0 |
| 89 | Raw Materials | All Item Groups | 0 |
| 90 | Refractory Materials | All Item Groups | 0 |
| 91 | Refrigerants | All Item Groups | 0 |
| 92 | Reinforcing Materials | All Item Groups | 0 |
| 93 | Road & Pavement Materials | All Item Groups | 0 |
| 94 | Roller Chains & Fasteners | All Item Groups | 0 |
| 95 | Roller Chains & Links | All Item Groups | 0 |
| 96 | Rollers & Links | All Item Groups | 0 |
| 97 | Roofing & Accessories | All Item Groups | 0 |
| 98 | Roofing Materials & Components | All Item Groups | 0 |
| 99 | Rope & Cords | All Item Groups | 0 |
| 100 | Ropes & Cables | All Item Groups | 0 |
| 101 | Safety & Facility Supplies | All Item Groups | 0 |
| 102 | Safety Components | All Item Groups | 0 |
| 103 | Safety Equipment | All Item Groups | 0 |
| 104 | Safety Equipment & Components | All Item Groups | 0 |
| 105 | Safety Seals | All Item Groups | 0 |
| 106 | Safety Signs & Labels | All Item Groups | 0 |
| 107 | Sanitary Fixtures | All Item Groups | 0 |
| 108 | Sanitary Ware & Fixtures | All Item Groups | 0 |
| 109 | Seals | All Item Groups | 0 |
| 110 | Seals & Gaskets | All Item Groups | 0 |
| 111 | Seals & O-Rings | All Item Groups | 0 |
| 112 | Security Hardware | All Item Groups | 0 |
| 113 | Shafting | All Item Groups | 0 |
| 114 | Steel Shafting | All Item Groups | 0 |
| 115 | Steel Valves & Fittings | All Item Groups | 0 |
| 116 | Structural Steel Materials | All Item Groups | 0 |
| 117 | Tables & Chairs | All Item Groups | 0 |
| 118 | Tiles & Flooring Materials | All Item Groups | 0 |
| 119 | Tires & Accessories | All Item Groups | 0 |
| 120 | Tool Consumables | All Item Groups | 0 |
| 121 | Tool Storage | All Item Groups | 0 |
| 122 | Tools | All Item Groups | 0 |
| 123 | Valves | All Item Groups | 0 |
| 124 | Valves & Fittings | All Item Groups | 0 |
| 125 | Welding Consumables | All Item Groups | 0 |
| 126 | Welding Equipment & Accessories | All Item Groups | 0 |
| 127 | Wheels & Casters | All Item Groups | 0 |
| 128 | Windows & Accessories | All Item Groups | 0 |
| 129 | Wood & Bamboo Materials | All Item Groups | 0 |
| 130 | Wood & Panel Materials | All Item Groups | 0 |
| 131 | Wood Coatings | All Item Groups | 0 |

## v1.2 correction — Shafting remains the official label (2026-10-19)

**Owner clarified:** the question whether `Shafting` or `Shaft` was correct was **not a request or authorization to rename**. The assistant incorrectly inferred approval and generated v1.1 with `Shafts`. **That inference and amendment are withdrawn.** Restore the originally owner-approved exact label **`Shafting`**, retaining **`Steel Shafting`** as a separate Item Group. No other name, quantity or hierarchy changes are authorized.

This **v1.2** version is authoritative and supersedes v1.1. The chat-only corrected files are `CCPC_Official_Item_Groups_v1.2_2026-10-19.xlsx`, `CCPC_Official_Item_Group_Names_v1.2_2026-10-19.csv` and `CCPC_Item_Group_DEV_Staging_Not_For_Import_v1.2_2026-10-19.csv`. The list is identical to the original v1.0 approved naming manifest, SHA256 `e0c4c3c5f225f60ac2601c838c24f2510462c9d9914daff1cb3cb050b60a19d1` over all 131 LF-separated UTF-8 names with final LF.

**This corrects project documentation and attached review files only.** It does not perform a live ERPNext rename/import/reclassification, or change DEV/PRODUCTION, Item defaults, financial mappings or stock/GL.

## Implementation boundary and next verified step

1. On a **verified DEVELOPMENT** site, obtain **read-only** exact `Item Group.name`, `item_group_name`, `parent_item_group`, `is_group` and relevant linked-Item dependencies. The site origin, branch and pending work must first be verified, preserving local changes and site backups.
2. Compare with this 131-name standard: reuse exact existing matches; flag mismatches and existing default groups (especially `Products`) rather than creating duplicates, and separately review any necessary rename/reparent/create and implications for existing transactions, reports and defaults.
3. Test any specifically approved master-data operations in DEVELOPMENT with a safe recoverable procedure. PRODUCTION requires a separate explicit user deployment/backup/rollback approval. **No live master change was performed when recording this decision.**
4. **Accounting Decision B remains separate:** zero approved Company + exact leaf Item Group → Expense Account assignments; the CCPC Withdrawal Slip/Material Issue posting release remains **POSTING_NO_GO** pending Issue #25 (G1–G4) independent maker/checker signoff. No parent inheritance or automatic Stock Adjustment fallback.

**Status:** Official target taxonomy approved; DEVELOPMENT master reconciliation and financial mapping **not yet completed**. **PRODUCTION NO-GO / DEV_TARGET_ORIGIN_UNKNOWN_STOP**.
