# Excel results reader

This folder is a set of scripts that will take an Excel file and read its contents and present the results
as a PNG file showing a barchart. Additionally, the scripts will produce a web page that will be in the
output folder and will display the PNG file along with an analysis of the results.

## Step 01 — Read Excel and write JSON aggregates

Reads `inputs/data.xlsx`, sums sales `Value` by `Sales_Rep_Name`, and writes `outputs/results.json`.

### Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
```

### Run

```bash
python scripts/read_excel.py
```

### Output

- File: `outputs/results.json`
- Format: `{ "perSale": [ { "salesRepName": "...", "totalValue": ... }, ... ] }`
- Sort order: `perSale` entries are sorted alphabetically by `salesRepName`.

Generated files under `outputs/` are gitignored; see `outputs/README.md`.

## Step 02 — Bar chart from JSON results

Reads `outputs/results.json` (from Step 01) and writes `outputs/barchart.png`.

**Prerequisite:** run Step 01 first so `outputs/results.json` exists.

### Run

```bash
python scripts/chart_results.py
```

### Output

- File: `outputs/barchart.png`
- Chart: vertical bar chart — x-axis = sales rep name, y-axis = total sales value
- Bar order: same order as the `perSale` array in `results.json` (alphabetical by rep name from Step 01)
- Title: `Total Sales by Sales Representative`

### Logging

Logs are written to stderr at INFO by default. Each pipeline step (load, validate, extract, plot, save) is logged.

Optional verbose logging:

```bash
set LOG_LEVEL=DEBUG          # Windows cmd
# export LOG_LEVEL=DEBUG     # macOS/Linux
python scripts/chart_results.py
```
