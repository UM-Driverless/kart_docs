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

### Fix the stale firmware-target claims inside the kart-medulla repo
Settled on 2026-07-30: the kart runs the `esp32-s3-devkitc-1` build. `kart-docs` is corrected,
but three statements **in the `kart-medulla` repo** are still wrong and will mislead the next
reader there:

1. `platformio.ini` — the comment above `[env:esp32-s3-devkitc-1]` says the env "does NOT link
   yet ... not because a working S3 image exists". It has built and uploaded from the Orin
   since 2026-07-26.
2. `.agents/esp32s3-pinmap.md` — "The S3 build does not exist. `platformio.ini` has only
   `esp32dev` and `native`." Both halves are false.
3. `README.md` — still carries classic-ESP32 pin tables (already filed in that repo's own
   task board on 2026-07-30 as "README's classic tables are a hazard").

**Safety-relevant and genuinely unresolved:** `AGENTS.md` says `components/km_gpio/km_gpio.h`
uses the `CONFIG_IDF_TARGET_ESP32S3` pin map; `.agents/esp32s3-pinmap.md` says that header
still holds the classic WROOM-32E map. Under the classic map `PIN_STEER_PWM` is GPIO 18, which
on the S3 board is the gate of Q3, the shutdown-circuit MOSFET — so getting this wrong means
the steering PWM drives the SDC. Read `km_gpio.h` and settle it.

### Verify the S3 upload speed of 921600 on hardware
`platformio.ini` sets `upload_speed = 921600` for `esp32-s3-devkitc-1`, annotated in-file as
"UNVERIFIED on hardware as of 2026-07-26 — raised from reading the datasheets, not from a
successful flash". The reasoning is sound (the 115200 cap was the *classic* board's CP2102;
this board's CH343 is rated to 6 Mbps), but it should be confirmed by an actual flash and the
in-file note either removed or downgraded. Fallbacks if it fails: 460800, then 115200.

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
