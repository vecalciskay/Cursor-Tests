"""Read Step 01 JSON results and write a bar chart PNG."""

from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt

REPO_ROOT = Path(__file__).resolve().parent.parent
INPUT_PATH = REPO_ROOT / "outputs" / "results.json"
OUTPUT_PATH = REPO_ROOT / "outputs" / "barchart.png"

CHART_TITLE = "Total Sales by Sales Representative"
X_AXIS_LABEL = "Sales Representative"
Y_AXIS_LABEL = "Total Sales Value"
FIGURE_WIDTH = 10
FIGURE_HEIGHT = 6
FIGURE_DPI = 100

logger = logging.getLogger(__name__)


def configure_logging() -> None:
    level_name = os.environ.get("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, None)
    if not isinstance(level, int):
        level = logging.INFO

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s %(levelname)s %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)

    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)


def load_results(path: Path) -> dict[str, object]:
    logger.info("Loading results from %s", path)

    if not path.is_file():
        raise FileNotFoundError(
            f"Input file not found: {path} (run python scripts/read_excel.py first)"
        )

    file_size = path.stat().st_size
    logger.debug("Input file size: %d bytes", file_size)

    with path.open(encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")

    per_sale = data.get("perSale")
    if not isinstance(per_sale, list):
        raise ValueError(f"Missing or invalid 'perSale' array in {path}")
    if not per_sale:
        raise ValueError(f"'perSale' array is empty in {path}")

    logger.debug("Parsed JSON keys: %s", list(data.keys()))

    for index, entry in enumerate(per_sale):
        if not isinstance(entry, dict):
            raise ValueError(f"Invalid perSale entry at index {index}: expected object")
        if "salesRepName" not in entry:
            raise ValueError(f"Invalid perSale entry at index {index}: missing salesRepName")
        if "totalValue" not in entry:
            raise ValueError(f"Invalid perSale entry at index {index}: missing totalValue")

        rep_name = entry["salesRepName"]
        total_value = entry["totalValue"]

        if rep_name is None or str(rep_name).strip() == "":
            raise ValueError(
                f"Invalid perSale entry at index {index}: blank salesRepName"
            )
        if not isinstance(total_value, (int, float)):
            raise ValueError(
                f"Invalid perSale entry at index {index}: totalValue must be numeric"
            )

        logger.debug(
            "Validated perSale[%d]: salesRepName=%r totalValue=%s",
            index,
            str(rep_name).strip(),
            total_value,
        )

    logger.info("Loaded JSON with %d perSale entries", len(per_sale))
    return data


def extract_chart_data(results: dict[str, object]) -> tuple[list[str], list[float]]:
    per_sale = results["perSale"]
    names: list[str] = []
    values: list[float] = []

    for entry in per_sale:
        name = str(entry["salesRepName"]).strip()
        value = float(entry["totalValue"])
        names.append(name)
        values.append(value)

    logger.info("Extracted chart data for %d sales representatives", len(names))
    for name, value in zip(names, values):
        logger.info("Rep %r: totalValue=%s", name, value)

    return names, values


def create_bar_chart(
    names: list[str], values: list[float], output_path: Path
) -> None:
    logger.info("Creating bar chart (%d bars)", len(names))

    if output_path.is_file():
        logger.warning("Overwriting existing chart at %s", output_path)

    logger.debug(
        "Figure size: %sx%s inches, DPI: %s",
        FIGURE_WIDTH,
        FIGURE_HEIGHT,
        FIGURE_DPI,
    )
    logger.debug(
        "Chart title: %r, x-label: %r, y-label: %r",
        CHART_TITLE,
        X_AXIS_LABEL,
        Y_AXIS_LABEL,
    )

    figure, axes = plt.subplots(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))
    try:
        axes.bar(names, values)
        axes.set_title(CHART_TITLE)
        axes.set_xlabel(X_AXIS_LABEL)
        axes.set_ylabel(Y_AXIS_LABEL)
        axes.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda value, _pos: f"{value:,.0f}")
        )
        plt.xticks(rotation=0)
        plt.tight_layout()

        logger.info("Saving chart to %s", output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(output_path, dpi=FIGURE_DPI, bbox_inches="tight")

        png_size = output_path.stat().st_size
        logger.info("Wrote PNG (%d bytes) to %s", png_size, output_path)
    finally:
        plt.close(figure)


def main() -> int:
    configure_logging()

    logger.info("Starting Step 02 chart generation")
    logger.info("Input: %s", INPUT_PATH.resolve())
    logger.info("Output: %s", OUTPUT_PATH.resolve())

    results = load_results(INPUT_PATH)
    names, values = extract_chart_data(results)
    create_bar_chart(names, values, OUTPUT_PATH)

    logger.info("Step 02 completed successfully")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, ValueError, OSError, json.JSONDecodeError) as error:
        logger.error("%s", error)
        raise SystemExit(1) from error
    except Exception:
        logger.exception("Unexpected error during chart generation")
        raise SystemExit(1)
