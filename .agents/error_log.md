# Error Log

This file tracks mistakes made during development and the prevention mechanisms added to avoid recurrence. Every error should be documented here with:
- Date
- What happened (brief description)
- Prevention added (what changed to prevent it)

## Format
```markdown
## YYYY-MM-DD - Brief title
**What happened:** Description of the error
**Prevention added:**
- List of changes made (updated files, new checks, etc.)
```

---

## 2026-02-18 - HTML entities in SVG are invalid XML
**What happened:** Used `&mdash;`, `&rarr;`, `&times;` in hand-crafted SVGs. These are HTML-only named entities and are not valid in SVG (which is XML). Browsers may render them, but strict XML parsers and some build tools reject them.
**Prevention added:**
- Rule: Only use numeric character references (`&#NNN;` or `&#xHHHH;`) in SVG files, never HTML named entities.

## 2026-02-18 - drawio-export CI step overwrote hand-crafted SVGs
**What happened:** The CI `drawio-export` step auto-exported `.drawio` files to SVG, replacing interactive hand-crafted SVG versions with flat auto-generated ones.
**Prevention added:**
- Removed `.drawio` source files from the repo. If `.drawio` files are reintroduced, either exclude them from auto-export or backup/restore hand-crafted SVGs around the export step.

## 2026-02-18 - Wrong component specs from datasheet (configurable product)
**What happened:** D6 pressure regulator was stated as 0.5-10 bar range, but the specific subtype actually maxes out at 7 bar. Festo datasheets for configurable products show combined specs across all subtypes, not the specific ordered variant.
**Prevention added:**
- Rule: For configurable products (especially Festo), cross-reference physical labels and subtype-specific data, not just the main product page which shows the full range of all variants.

## 2026-02-18 - Forgot to commit asset files (images, PDFs)
**What happened:** Images and PDFs referenced in docs were not tracked in git, causing `mkdocs build --strict` to fail with 25 broken-link warnings.
**Prevention added:**
- Rule: Always run `uv run mkdocs build --strict` locally before pushing. Strict mode catches missing assets as broken links.
- Added to definition of done checklist.

## 2026-02-18 - Horizontal SVGs too wide for page
**What happened:** Circuit/flow diagrams laid out horizontally were scaled down to fit the page width, becoming unreadably small on standard screens.
**Prevention added:**
- Rule: Use vertical (top-to-bottom) layout for circuit and flow diagrams. This fits naturally in scrollable web pages and avoids forced shrinking.
