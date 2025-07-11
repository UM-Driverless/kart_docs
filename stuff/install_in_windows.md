# Windows Installation Guide for kart_docs

This guide provides instructions for setting up the `kart_docs` project on a Windows machine.

## 1. Install Poetry

The recommended way to install Poetry on Windows is by using `curl` to download the installer and then executing it with Python.

```bash
# Download the installer
curl -sSL https://install.python-poetry.org -o install-poetry.py

# Run the installer
python install-poetry.py
```

After installation, you may need to restart your terminal for the `poetry` command to be recognized. If you continue to have issues, you may need to add Poetry's scripts directory to your system's PATH environment variable manually. The path is typically: `C:\Users\<Your-Username>\AppData\Roaming\Python\Scripts`

## 2. Install Project Dependencies

Once Poetry is installed, you can install the project's dependencies using the following command:

```bash
poetry install
```

## 3. Install Headless Browser for PDF Export

To enable PDF export functionality, you need to install a headless Chrome browser using Playwright:

```bash
poetry run playwright install --force chrome
```

## 4. Previewing the Documentation

To preview the documentation locally, run the following command:

```bash
poetry run mkdocs serve
```

Then, open your web browser and navigate to `http://127.0.0.1:8000`.
