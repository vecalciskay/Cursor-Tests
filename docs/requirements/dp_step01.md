# Development Plan — Step 01: Read Excel and Write JSON Aggregates

## 1. Objective

Implement a Python script that reads sales data from `inputs/data.xlsx`, aggregates total sales value per sales representative, and writes the result to `outputs/results.json` in the required JSON format.

This is the first step in the broader Excel results reader project described in the README. Later steps will add chart generation and a web page; Step 01 focuses only on data ingestion and aggregation.

## 2. Requirements Summary

Source: [step01_read.md](./step01_read.md)

| Requirement | Detail |
|-------------|--------|
| Input file | `inputs/data.xlsx` |
| Output file | `outputs/results.json` |
| Aggregation | Total `Value` grouped by sales representative |
| Output key | `perSale` — array of objects with `salesRepName` and `totalValue` |

## 3. Input Data Specification

### 3.1 Excel columns

| Column | Type | Description |
|--------|------|-------------|
| `Postcode` | number | Postcode of the sale |
| `Sales_Rep_ID` | number | Sales rep identifier |
| `Sales_Rep_Name` | string | Sales rep name (aggregation key) |
| `Year` | number | Year of the sale |
| `Value` | number | Sale amount |

### 3.2 Known data characteristics (from `inputs/data.xlsx`)

- Sheet name: `Sheet1`
- Header row: row 1
- Data rows: 390 (391 rows total including header)
- Sales representatives: 3 (`Jane`, `Ashish`, `John`)
- `Value` contains floating-point amounts

For Step 01, only `Sales_Rep_Name` and `Value` are required for aggregation. The other columns are read but not used in the output.

## 4. Output Data Specification

### 4.1 JSON schema

```json
{
  "perSale": [
    { "salesRepName": "Jane", "totalValue": 6665269.38 },
    { "salesRepName": "Ashish", "totalValue": 6386039.23 },
    { "salesRepName": "John", "totalValue": 6148152.83 }
  ]
}
```

Notes:

- Property names must match exactly: `perSale`, `salesRepName`, `totalValue` (camelCase).
- `totalValue` is the sum of all `Value` entries for that rep.
- Array order is not specified in the requirements; a stable sort (e.g. descending by `totalValue`, or alphabetical by `salesRepName`) should be chosen and documented in the script.

## 5. Proposed Project Structure

```
Cursor-Tests/
├── inputs/
│   └── data.xlsx              # existing input (committed)
├── outputs/
│   ├── README.md              # committed — describes the folder; keeps outputs/ in git
│   └── results.json           # generated — gitignored
├── scripts/
│   └── read_excel.py          # main script for Step 01
├── requirements.txt           # openpyxl (or pandas + openpyxl)
├── .gitignore                 # ignore all outputs/ contents except README.md
└── docs/requirements/
    ├── step01_read.md
    └── dp_step01.md
```

Keep the script small and focused. Avoid premature abstraction until later steps (charting, web page) justify shared modules.

### 5.1 Version control for `outputs/`

Generated files under `outputs/` must not be committed. The folder itself should remain in the repository so scripts can write to a known path and later steps can add charts and HTML here.

Approach:

1. Add `outputs/README.md` — a short, committed file explaining that this folder holds generated results (JSON, and later PNG/HTML). This keeps the directory tracked in git without committing generated artifacts.
2. Update `.gitignore` so everything in `outputs/` is ignored except that README:

```gitignore
# Generated files in outputs/ (README.md is tracked)
outputs/*
!outputs/README.md
```

Effect:

- `outputs/results.json` and any other generated files are ignored.
- `outputs/README.md` is tracked and documents the folder purpose.
- The script may still create `outputs/` at runtime if missing, but the committed README ensures the directory exists after clone.

## 6. Technical Approach

### 6.1 Library choice

Use **openpyxl** to read `.xlsx` files directly. It is lightweight and sufficient for this step.

Alternative: **pandas** with `read_excel` and `groupby`. Prefer openpyxl alone unless later steps already require pandas.

### 6.2 Processing flow

```
inputs/data.xlsx
       │
       ▼
  Load workbook (Sheet1)
       │
       ▼
  Validate header row matches expected columns
       │
       ▼
  Iterate data rows → accumulate Value by Sales_Rep_Name
       │
       ▼
  Build { "perSale": [ { salesRepName, totalValue }, ... ] }
       │
       ▼
  Ensure outputs/ exists → write outputs/results.json
```

### 6.3 Aggregation logic

1. Read each data row (skip header).
2. Extract `Sales_Rep_Name` and `Value`.
3. Sum `Value` into a dictionary keyed by rep name.
4. Convert to the `perSale` list format.
5. Serialize to JSON with `json.dump` (indent optional for readability during development).

Edge cases to handle:

- Missing or blank `Sales_Rep_Name` — skip row or fail with a clear error (recommend fail-fast with row number).
- Non-numeric or missing `Value` — fail with a clear error.
- Duplicate rep names with different casing — treat as separate keys unless normalized (recommend no normalization; data uses consistent casing).

## 7. Implementation Tasks

### Task 1 — Project scaffolding

- [ ] Add `requirements.txt` with `openpyxl` (pin a recent stable version).
- [ ] Create `scripts/` directory.
- [ ] Create `outputs/README.md` describing that this folder holds generated results (JSON in Step 01; charts and web output in later steps).
- [ ] Add gitignore rules for `outputs/` — ignore all contents except `outputs/README.md` (see Section 5.1).
- [ ] Create `outputs/` at runtime in the script if missing (defensive; README already establishes the folder in git).

### Task 2 — Core script (`scripts/read_excel.py`)

- [ ] Define constants for input path (`inputs/data.xlsx`) and output path (`outputs/results.json`).
- [ ] Implement `load_sales_rows(path) -> list[dict]` or equivalent row iterator.
- [ ] Implement `aggregate_by_rep(rows) -> dict[str, float]`.
- [ ] Implement `build_result(aggregates) -> dict` matching the required JSON shape.
- [ ] Implement `write_json(data, path)` — create parent directory if missing.
- [ ] Add `if __name__ == "__main__":` entry point that runs the full pipeline.

### Task 3 — Validation and errors

- [ ] Verify Excel header row contains expected column names (order may vary; match by name).
- [ ] Raise informative errors for: missing input file, empty sheet, schema mismatch, invalid numeric values.
- [ ] Exit with non-zero status code on failure (for future CI use).

### Task 4 — Verification

- [ ] Run script locally: `python scripts/read_excel.py`.
- [ ] Confirm `outputs/results.json` exists and is valid JSON.
- [ ] Confirm three entries in `perSale`, one per rep.
- [ ] Confirm totals match manual spot-check (see Section 8).

### Task 5 — Documentation

- [ ] Add a short "Step 01" section to `README.md`: purpose, install, run command, output location.
- [ ] Document any sorting convention used for `perSale`.

## 8. Expected Results (acceptance reference)

After a correct run against the current `inputs/data.xlsx`, approximate totals are:

| Sales Rep | Expected totalValue (approx.) |
|-----------|-------------------------------|
| Jane | 6,665,269.38 |
| Ashish | 6,386,039.23 |
| John | 6,148,152.83 |

Acceptance tests should compare aggregated values within a small floating-point tolerance (e.g. `1e-6`) rather than exact string equality.

## 9. Acceptance Criteria

Step 01 is complete when:

1. Running the script from the repository root produces `outputs/results.json` without manual steps.
2. Output JSON has top-level key `perSale` only (plus its array contents as specified).
3. Each object in `perSale` has `salesRepName` (string) and `totalValue` (number).
4. Sums match the full dataset aggregation for each sales rep.
5. Script fails clearly if the input file is missing or columns do not match the schema.
6. Dependencies are declared in `requirements.txt` and installable via `pip install -r requirements.txt`.
7. `outputs/README.md` is committed; generated files under `outputs/` (including `results.json`) are listed in `.gitignore` and not tracked.

## 10. Out of Scope (Step 01)

- Bar chart PNG generation
- HTML web page output
- CLI arguments (hard-coded paths are acceptable for Step 01; argparse can be added later)
- Unit test suite (optional; manual verification is sufficient unless requested)
- Aggregation by year, postcode, or rep ID

## 11. Suggested Implementation Order

1. Scaffolding (`requirements.txt`, `outputs/README.md`, `.gitignore` rules for `outputs/`).
2. Minimal script: read file → print row count (smoke test).
3. Aggregation logic with console output.
4. JSON write to `outputs/results.json`.
5. Header validation and error handling.
6. README update and final verification against Section 8.

## 12. Run Instructions (target state)

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
python scripts/read_excel.py
```

Expected outcome: `outputs/results.json` created with aggregated sales per representative.
