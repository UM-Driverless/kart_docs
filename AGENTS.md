# Agent Quick Reference

## Key Files (Read Before Working)
Before making any changes, consult:
1. **`.agents/error_log.md`** — Past errors and added preventions
2. **`.agents/definition_of_done.md`** — Pre-commit checklist

## Commit Safety Protocol (Mandatory)
Before any `git commit`, you MUST:
1. Run `git status` to see which files will be included
2. Run `git diff --cached` to verify changes line by line
3. If build fails: document the error in `.agents/error_log.md`, fix it, and add prevention if recurring

**Never commit blindly.**

## Key Commands
```bash
uv run mkdocs serve          # Local dev server
uv run mkdocs build --strict  # Build with strict warnings (CI uses this)
```

## Key Paths
- Live site: https://um-driverless.github.io/kart_docs/
- CI workflow: `.github/workflows/deploy-docs.yml`
- MkDocs config: `mkdocs.yml`
- Documentation root: `docs/`

## Workflow
1. **Before starting:** Read the key files listed above
2. **During work:** Follow project patterns in `CLAUDE.md`
3. **Before committing:** Run through `.agents/definition_of_done.md` checklist
4. **Commit:** Follow the safety protocol (git status + git diff --cached)
5. **If build fails:** Fix, document in `.agents/error_log.md` if recurring
