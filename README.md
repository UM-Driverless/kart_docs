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
poetry config virtualenvs.in-project true
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
```
You can then access the documentation in your web browser, usually at `http://127.0.0.1:8000`.

To test the build before pushing (recommended):

```bash
poetry run mkdocs build --strict
# Output: site/
```

The `--strict` flag will catch errors like broken links, missing files, and invalid configuration - the same checks that run in CI.

---

## 🚀 Deployment

Deployment to GitHub Pages happens automatically via GitHub Actions when you push to the `main` branch.

The workflow will:
1. Build the documentation with `--strict` flag
2. Deploy to GitHub Pages if the build succeeds
3. Site will be available at: https://um-driverless.github.io/kart_docs/

### Manual deployment (alternative)

If needed, you can still deploy manually:

```bash
poetry run mkdocs gh-deploy
```

---

## 🤖 LLM-Friendly Documentation

This documentation includes LLM-optimized formats following the [llms.txt standard](https://llmstxt.org/):

- **llms.txt**: Sitemap-style overview of all documentation pages
- **llms-full.txt**: Complete documentation content in one consumable file

These files are automatically generated during the build process and are available at:
- Live site: https://um-driverless.github.io/kart_docs/llms.txt
- Live site: https://um-driverless.github.io/kart_docs/llms-full.txt

### Manual Generation

To manually generate the LLM files:

```bash
poetry run python generate_llm_files.py
```

---

## 📟 PDF Export (optional)

PDF export is disabled by default to speed up builds. To export PDFs explicitly:

```bash
EXPORT_PDF=true poetry run mkdocs build
# Outputs: site/pdf/kart-documentation.pdf
```

---


## 🗂 Branch structure

- `main` → Markdown source (all edits go here)
- `gh-pages` → Legacy deployment branch (can be deleted if using GitHub Actions)
