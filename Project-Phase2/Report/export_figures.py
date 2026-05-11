"""
Export all figures from Combustible.ipynb to PNG files for the LaTeX report.

Usage:
    python export_figures.py

This script executes the notebook and saves every matplotlib figure to
Project-Phase2/Report/figures/ with standardized names matching the LaTeX report.
"""
import json
import os
import sys

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
NOTEBOOK_PATH = os.path.join(os.path.dirname(__file__), "..", "Notebooks", "Combustible.ipynb")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "figures")

# Mapping: cell indices that produce plots -> output filenames
# Based on the notebook structure analysis
FIGURE_MAP = {
    49: "fig_01_histograms_log.png",         # Histograms original vs log
    37: "fig_02_outliers_temporal.png",       # Outliers temporal distribution
    69: "fig_03_boxplots_groups.png",         # Boxplots by income/subsidy
    73: "fig_04_temporal_regions.png",        # Price by region over time
    59: "fig_05_correlation_matrix.png",      # Correlation matrix
    61: "fig_06_temporal_global.png",         # Global temporal + regime bands
    75: "fig_07_volatility_subsidy.png",      # Volatility by subsidy level
    104: "fig_08_passthrough_countries.png",  # Pass-through by country bars
    123: "fig_09_covid_vs_ukraine_series.png",  # COVID vs Ukraine time series
    125: "fig_10_covid_vs_ukraine_boxplots.png", # COVID vs Ukraine boxplots
    130: "fig_11_scatter_passthrough_periods.png", # Scatter pass-through by period
    110: "fig_12_chile_sudamerica.png",       # Chile vs South America
}

def patch_notebook_for_export(nb_data, output_dir):
    """
    Insert savefig calls into plot cells and return modified notebook data.
    Does NOT modify the original file.
    """
    import copy
    nb = copy.deepcopy(nb_data)
    cells = nb["cells"]

    for cell_idx, filename in FIGURE_MAP.items():
        if cell_idx >= len(cells):
            print(f"  WARNING: Cell {cell_idx} does not exist, skipping {filename}")
            continue

        cell = cells[cell_idx]
        if cell["cell_type"] != "code":
            print(f"  WARNING: Cell {cell_idx} is not code, skipping {filename}")
            continue

        src = "".join(cell["source"])

        # Add savefig before plt.show()
        save_path = os.path.join(output_dir, filename).replace("\\", "/")
        save_cmd = f"\nplt.savefig(r'{save_path}', dpi=150, bbox_inches='tight', facecolor='white')\n"

        if "plt.show()" in src:
            src = src.replace("plt.show()", save_cmd + "plt.show()", 1)
        else:
            # Append savefig at the end
            src += save_cmd

        cell["source"] = [src]

    return nb


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"Loading notebook: {NOTEBOOK_PATH}")
    with open(NOTEBOOK_PATH, "r", encoding="utf-8") as f:
        nb_data = json.load(f)

    print(f"Patching {len(FIGURE_MAP)} cells for figure export...")
    patched_nb = patch_notebook_for_export(nb_data, OUTPUT_DIR)

    # Save patched notebook to temp file
    temp_nb = os.path.join(OUTPUT_DIR, "_temp_export.ipynb")
    with open(temp_nb, "w", encoding="utf-8") as f:
        json.dump(patched_nb, f, ensure_ascii=False)

    print(f"Executing patched notebook (this may take a few minutes)...")
    print(f"Output directory: {OUTPUT_DIR}")

    try:
        import nbformat
        from nbconvert.preprocessors import ExecutePreprocessor

        with open(temp_nb, "r", encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=4)

        ep = ExecutePreprocessor(timeout=600, kernel_name="python3")
        # Set working directory to notebook location for relative paths
        nb_dir = os.path.dirname(os.path.abspath(NOTEBOOK_PATH))
        ep.preprocess(nb, {"metadata": {"path": nb_dir}})

        print("\n=== Export complete ===")
        exported = [f for f in os.listdir(OUTPUT_DIR) if f.startswith("fig_")]
        print(f"Exported {len(exported)} figures:")
        for f in sorted(exported):
            print(f"  ✓ {f}")

    except ImportError:
        print("\nERROR: nbformat/nbconvert not installed.")
        print("Install with: pip install nbformat nbconvert jupyter")
        print(f"\nAlternatively, run the patched notebook manually:")
        print(f"  jupyter nbconvert --to notebook --execute {temp_nb}")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR during execution: {e}")
        print("You can also export figures manually by running the notebook")
        print("and saving figures from within Jupyter.")
        sys.exit(1)
    finally:
        # Clean up temp file
        if os.path.exists(temp_nb):
            os.remove(temp_nb)


if __name__ == "__main__":
    main()
