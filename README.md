# kart_docs

Documentation for the autonomous KART project.

📘 Live site: <https://um-driverless.github.io/kart_docs/>  
🧠 Main source: [Notion Kart Documentation](https://www.notion.so/KART-1b378747314380acb23ee354a4a4c4c7)

Built with [MkDocs](https://www.mkdocs.org/) using the [Material theme](https://squidfunk.github.io/mkdocs-material/).

---

## (Beta) Automated Installation
Just run `install.sh` in Linux or macOS:

## 🔧 Setup (using Poetry)

Install Poetry:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

If you don’t have `curl`, check [Poetry’s install methods](https://python-poetry.org/docs/#installation).

---

Clone the repo and set up the project:

```bash
git clone git@github.com:UM-Driverless/kart_docs.git
cd kart_docs
poetry install
poetry run playwright install --force chrome
```

This:
- Creates a project-local virtual environment (uses `pyenv` Python if available)
- Installs MkDocs and plugins
- Downloads a headless Chrome browser for PDF export

---

## ✅ Preview locally

```bash
poetry run mkdocs serve
# Open http://127.0.0.1:8000 in your browser
```

To build the static site:

```bash
poetry run mkdocs build
# Output: site/
```

---

## 🚀 Deploy to GitHub Pages

```bash
poetry run mkdocs gh-deploy
```

> GitHub Pages must be enabled in the repo settings (branch: `gh-pages`).

---

## 📟 PDF Export (optional)

PDF export is disabled by default to speed up builds. To export PDFs explicitly:

```bash
EXPORT_PDF=true poetry run mkdocs build
# Outputs: site/pdf/kart-documentation.pdf
```

---


## 🗂 Branch structure

- `main` → Markdown source
- `gh-pages` → Auto-generated static site (read-only)

Do all edits on `main`.
