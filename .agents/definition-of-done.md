# Definition of Done

Pre-commit checklist for kart-docs. Run through before every commit.

## Pre-Commit Checklist

### Build
- [ ] `uv run mkdocs build --strict` passes (no warnings)
- [ ] No broken links (strict mode catches these)

### Content Quality
- [ ] Pages state **current facts**, not the history of wrong turns. No "an earlier version was wrong", "that conclusion turned out mistaken", "we were confused about X" — write what is true now, plainly. The *why-we-changed-our-mind* narrative belongs in `~/dv/**/history.md`, never on a published page. (This is a prototype built from third-party parts; also avoid claiming the whole kart follows one internal standard when vendor parts don't.)
- [ ] SVGs are valid XML (no HTML-only entities like `&mdash;` — use `&#8212;` instead)
- [ ] No `file:///` URLs in SVGs or Markdown
- [ ] All referenced assets (images, PDFs) are tracked in git
- [ ] Diagrams are legible at page width (prefer vertical layout)
- [ ] Raw HTML tags (`<object>`, `<img>`, etc.) use paths relative to the **page URL**, not the source `.md` file (MkDocs only rewrites markdown `![](...)` syntax, not HTML tags)

### Error Prevention
- [ ] If error occurred: documented in `.agents/error-log.md` with prevention

## After Checklist

If all checks pass, proceed with commit following the safety protocol in `AGENTS.md`.
