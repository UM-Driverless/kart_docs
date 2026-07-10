<!-- consult-selectively: agent task board. Claim a task by setting status In progress + your id, commit, then Done. -->
# Task Board

## Ready

### Complete the sponsor list on the Credits page
`docs/credits.md` → "Partners & sponsors". Two open items (left as TODO comments in the file):
- **PCB fabrication sponsor** — confirm the actual company name. The repo only says
  "JLCPCB-style" (a generic paid fab), never names a sponsor. Rubén to provide.
- **Team-wide sponsors** — the live sponsor list is on Monday.com (Notion "Sponsors 2025-26"
  is empty). Check which Formula-Student sponsors also apply to the kart before adding — do
  NOT dump every FS-car sponsor here (over-claims). Kart-confirmed so far: Festo, Cytron,
  Henakart, RB Sistemas.

## In progress

_(none)_

## Done

### Build Journey section (2026-07-10)
Ported the portfolio's build-journey into kart-docs as a team-shareable section:
`docs/build-journey/index.md` + images/videos under `docs/build-journey/{images,videos}/`,
nav entry, `attr_list`/`md_in_html`/`pymdownx.emoji` extensions, and a primary
"Read the Build Journey" button at the bottom of the home page. Added the 2026-07-10
"first autonomous drive" post (latest LinkedIn). NOTE: the 2026-07-08 "steering gear
materials" (PPA) post is published but intentionally not added yet.

### Credits page (2026-07-10)
`docs/credits.md` — contributors (subsystem-tagged, one list, append-only) + partners &
sponsors. Full names resolved from the Notion workspace member list. Team members add their
own LinkedIn/GitHub via the GitHub "Edit" pencil (git-practice on-ramp); how-to is a source
comment, not shown on the page. Lead entry kept modest — shared work (ROS 2, dashboard)
credited to the people who did it, not the lead.
