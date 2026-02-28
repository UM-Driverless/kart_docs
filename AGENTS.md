# Agent Quick Reference

## Key Files (Read Before Working)
Before making any changes, consult:
1. **`.agents/error_log.md`** — Past errors and added preventions
2. **`.agents/definition_of_done.md`** — Pre-commit checklist

## Project Overview

Documentation repository for the UM Driverless autonomous kart project. Built with MkDocs Material theme, deployed to GitHub Pages.

**This repository is the single source of truth for kart documentation.** Previously managed in Notion, all documentation has been migrated to this MkDocs-based system.

**Live site:** https://um-driverless.github.io/kart_docs/

## Tech Stack

- **Documentation:** MkDocs with Material theme
- **Package Manager:** uv (migrated from Poetry)
- **Python:** >= 3.12
- **BOM Management:** YAML-based system in `docs/assembly/*/bom.yaml`
- **Deployment:** GitHub Actions → GitHub Pages

## Project Structure

```
kart_docs/
├── docs/
│   ├── bom/
│   │   ├── index.md          # BOM overview with dynamic parts table
│   │   └── README.md         # BOM management guide
│   ├── assembly/
│   │   ├── */bom.yaml        # Component data per assembly
│   │   ├── powertrain/
│   │   ├── steering/
│   │   ├── electronics/
│   │   └── sensors/
│   ├── tools/
│   │   ├── index.md          # Tools catalog documentation
│   │   └── tools.yaml        # Tool inventory
│   └── assets/
│       └── datasheets/       # PDF datasheets
├── scripts/
│   └── aggregate_bom.py      # BOM report generation
├── generate_bom_hook.py      # MkDocs hook for dynamic parts table
├── generate_bom_reports.sh   # Helper script for reports
└── pyproject.toml            # uv-compatible project config
```

## Key Commands
```bash
uv sync                        # Install dependencies
uv run mkdocs serve            # Local dev server
uv run mkdocs build --strict   # Build with strict warnings (CI uses this)
./generate_bom_reports.sh      # Generate BOM reports
```

## Key Features

### BOM Management System

**YAML-based part tracking:**
- Each assembly has `bom.yaml` with component specifications
- Fields: id, part_number, description, quantity, unit_cost, status, criticality, suppliers, specifications
- Hierarchical structure matches physical assembly

**Dynamic features:**
- `generate_bom_hook.py` auto-generates searchable HTML table on build
- Real-time search, filtering by assembly/status/category
- Sortable columns, color-coded badges
- Cost summaries injected into BOM index

**Report generation:**
- `scripts/aggregate_bom.py` creates JSON + CSV reports
- Outputs: cost summaries, supplier lists, status reports

### Tools Catalog

- `docs/tools/tools.yaml` - Workshop tool inventory
- Categories: hand tools, electronics, power tools, measuring equipment
- Tracks: location, status, calibration schedules, safety requirements

## Important Patterns

### Adding Components to BOM

1. Navigate to `docs/assembly/{assembly}/bom.yaml`
2. Add component in YAML format
3. Component auto-appears in searchable table on next build

### Documentation Philosophy

- **Consolidate, don't duplicate** - Keep docs in README.md files, avoid creating extra "guide" files
- **No authors in pyproject.toml** - Git history tracks contributors
- **Folder README convention** - Use `README.md` for folder documentation (e.g., `docs/bom/README.md`)

## Files to Ignore/Not Create

- Don't create FEATURES_ADDED.md, MIGRATION.md, or similar - keep current state in README
- Don't maintain author lists - Git already tracks this

## Build Pipeline

GitHub Actions workflow (`.github/workflows/deploy-docs.yml`):
1. Uses `astral-sh/setup-uv@v4`
2. Runs `uv sync` to install dependencies
3. Builds with `uv run mkdocs build --strict --verbose`
4. Deploys to GitHub Pages

## Commit Safety Protocol (Mandatory)
Before any `git commit`, you MUST:
1. Run `git status` to see which files will be included
2. Run `git diff --cached` to verify changes line by line
3. If build fails: document the error in `.agents/error_log.md`, fix it, and add prevention if recurring

**Never commit blindly.**
