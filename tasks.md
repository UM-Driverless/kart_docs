<!-- consult-selectively: the project's task board (one per repo, at the root). Claim a task by setting status In progress + your id, commit, then Done. -->
# Task Board

## Ready

### Add the PCB sponsor to the Credits page
`docs/credits.md` → "Partners & sponsors" (TODO comment left in the file).
Confirm the actual PCB fabrication sponsor's company name — the repo only says
"JLCPCB-style" (a generic paid fab), never names a sponsor. Rubén to provide.
Kart sponsors already listed: Festo, Cytron, Henakart, RB Sistemas.

### Split the medulla's ground terminals between GND and GND_SIG
The harness now has two grounds: `GND` (power) and `GND_SIG` (sensors, black + white
stripe), tied only at the rear ground Wago block near the battery and the 12 V / 24 V
regulators. All three medulla ground terminals (CN1.3, CN9.3, CN10.3) are still on the
power `GND` net in `docs/assembly/electronics/wiring/wiring.yaml`, because which of them
the PCB routes to its analog ground is not recorded here. Check the authoritative KiCad
project (`dv-hardware/projects/kart-medulla`): if the board has separate analog and power
grounds, move the analog terminal to `GND_SIG`; if it has one ground plane, say so in
`wiring.md` so nobody assumes the split reaches the board.

### Redraw the wiring SVG for the two-ground split
`docs/assembly/electronics/wiring/images/wiring-global.svg` is hand-drawn and still shows
one common ground. It needs the `GND_SIG` return, the rear Wago star point, and the
striped-black convention, otherwise the diagram and the generated wire table disagree.
Background on the two-ground split: `docs/assembly/electronics/wiring.md`, section
"Why two grounds".

### Resolve how a classic-ESP32 firmware image runs on ESP32-S3 hardware
`docs/assembly/electronics/kart-medulla/firmware.md` states both that "the physical
kart-medulla board is an **ESP32-S3**" and that the `esp32dev` environment
(classic ESP32-WROOM-32E) is "the image that actually runs on the kart", with the S3 target
listed as a stub that does not link. Those cannot both be true as written: the classic ESP32
is Xtensa LX6 and the S3 is LX7, so an `esp32dev` binary will not boot on an S3 and esptool
refuses the chip-ID mismatch. One of three things is the case — the kart runs a build target
other than the two documented, the board in the kart is not what the page says, or the
`esp32dev` env has been repointed at the S3 in `platformio.ini`. Check `platformio.ini` in
the `kart-medulla` repo and the flashing output, then correct the page. Until this is settled,
`orin-setup.md`'s flashing snippet may be telling people to flash the wrong environment.

### Add the MCP4922 as its own component in bom.yaml
The Kart Medulla's DAC (**MCP4922-E/SL**, dual 12-bit SPI) is described in
`docs/assembly/electronics/kart-medulla/index.md` and now appears as a row in
`docs/bom/full.md`, but has no entry in `docs/assembly/electronics/bom.yaml`, so it is missing
from the generated reports and from any cost aggregation. It replaced the MCP4728 (quad
12-bit I²C) on 2026-04-17. Needs a real supplier link and unit cost — the `docs/bom/full.md`
row currently carries a placeholder "~3" that was inherited from the MCP4728 line.

## In progress

_(none)_

## Done

### llms.txt and llms-full.txt were 404 on the live site (2026-07-19)
`generate_llm_files.py` parsed `mkdocs.yml` with a custom `SafeLoader` that knew about
`!ENV` but not `!!python/name:`, which mkdocs-material uses for its emoji index and
superfences formatter. The script died on `mkdocs.yml:21` from commit `e0c057c`
(2026-07-10, the Build Journey section) onward, so both files were missing from every
deploy for nine days. Fixed with a multi-constructor for the `python/name` tag prefix.
The failure survived that long because `generate_llm_hook.py` printed only `result.stderr`
while the script reports errors on stdout — the warning always rendered with an empty
reason and read as cosmetic noise. The hook now prints both streams.

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
