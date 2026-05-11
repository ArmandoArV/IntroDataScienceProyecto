# Phase 2 Report — LaTeX (APA 7)

## Compilation

```bash
# Requires: texlive-full or miktex with apa7 class
pdflatex main.tex
biber main
pdflatex main.tex
pdflatex main.tex
```

## Figure Export

Before compiling, export figures from the notebook:

```bash
cd Project-Phase2/Report
python export_figures.py
```

This executes the notebook and saves all 12 key figures as PNG to `figures/`.

## Structure

```
Report/
├── main.tex           # Main LaTeX document (APA 7)
├── references.bib     # Bibliography
├── export_figures.py  # Auto-export figures from notebook
├── figures/           # Exported PNGs (generated)
└── README.md          # This file
```
