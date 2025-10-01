# Claude Memory - Kart Documentation

## Project Overview

This is the documentation repository for the UM Driverless autonomous kart project. Built with MkDocs Material theme, deployed to GitHub Pages.

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
- Run via `./generate_bom_reports.sh` or `uv run python scripts/aggregate_bom.py`

### Tools Catalog

- `docs/tools/tools.yaml` - Workshop tool inventory
- Categories: hand tools, electronics, power tools, measuring equipment
- Tracks: location, status, calibration schedules, safety requirements

## Common Commands

```bash
# Setup
uv sync
uv run playwright install --force chrome

# Development
uv run mkdocs serve

# Build
uv run mkdocs build --strict

# Generate BOM reports
./generate_bom_reports.sh
```

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

## ChatGPT Context

User asked ChatGPT about parts documentation. ChatGPT suggested creating a parts catalog system, but the project **already had an excellent YAML-based BOM system**. We enhanced it with:
- Dynamic searchable parts table (big UX improvement)
- Automated reporting tools
- Tools catalog (ChatGPT mentioned but didn't implement)

The existing system was already better than ChatGPT's suggestion.

## Build Pipeline

GitHub Actions workflow (`.github/workflows/deploy-docs.yml`):
1. Uses `astral-sh/setup-uv@v4`
2. Runs `uv sync` to install dependencies
3. Builds with `uv run mkdocs build --strict --verbose`
4. Deploys to GitHub Pages

## Recent Changes (2025-10-01)

- Migrated from Poetry to uv
- Renamed `docs/bom/BOM_MANAGEMENT.md` → `docs/bom/README.md`
- Added dynamic parts table via MkDocs hook
- Created tools catalog system
- Updated all documentation to use uv commands
