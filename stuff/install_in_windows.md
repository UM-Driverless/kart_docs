# Windows Installation Guide for kart_docs

This guide provides instructions for setting up the `kart_docs` project on a Windows machine.

## 1. Install uv

Install uv using PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

After installation, restart your terminal for the `uv` command to be recognized.

## 2. Install Project Dependencies

Once uv is installed, install the project's dependencies:

```bash
uv sync
```

## 3. Install Headless Browser for PDF Export

To enable PDF export functionality, install a headless Chrome browser using Playwright:

```bash
uv run playwright install --force chrome
```

## 4. Previewing the Documentation

To preview the documentation locally:

```bash
uv run mkdocs serve
```

Then, open your web browser and navigate to `http://127.0.0.1:8000`.
