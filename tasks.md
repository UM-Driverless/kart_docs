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

4. `.agents/esp32s3-pinmap.md` — "**This is NOT the pin map the firmware currently uses.**
   `components/km_gpio/km_gpio.h` still holds the classic-ESP32 (WROOM-32E) map". Checked
   2026-07-30: the header carries *both* maps behind `#if defined(CONFIG_IDF_TARGET_ESP32S3)`,
   and the S3 branch is the one that compiles for the `esp32-s3-devkitc-1` build
   (`PIN_STEER_PWM` = GPIO 40, `PIN_STEER_DIR` = GPIO 17, `PIN_SDC_NOT_EMERGENCY` = GPIO 18).
   `AGENTS.md` is right and this file is wrong.
5. `km_gpio.h:108` — the `#else` branch is labelled `/* CONFIG_IDF_TARGET_ESP32 — classic
   ESP32-WROOM-32E (current build) */`. It is no longer the current build.

### Verify the S3 upload speed of 921600 on hardware
`platformio.ini` sets `upload_speed = 921600` for `esp32-s3-devkitc-1`, annotated in-file as
"UNVERIFIED on hardware as of 2026-07-26 — raised from reading the datasheets, not from a
successful flash". The reasoning is sound (the 115200 cap was the *classic* board's CP2102;
this board's CH343 is rated to 6 Mbps), but it should be confirmed by an actual flash and the
in-file note either removed or downgraded. Fallbacks if it fails: 460800, then 115200.

### The dv-hardware netlist's CN designators do not match the board silkscreen
Settled 2026-07-30: on the board, **CN4.3 is REVERSE and CN8.1 is `SDC_IN_LOW_SIDE`**, as
kart-docs has always said. But `dv-hardware/projects/kart-medulla/output/netlist.net`
(exported 2026-05-07) puts `/REVERSE_WIRE` on **CN8 pin 1** and `/SDC_IN_LOW_SIDE` on **CN5** —
so its `CN` reference designators are not the silkscreen `CN` numbers, and it is not a simple
pairwise swap either. Anyone wiring from that netlist would land the reverse command on the
shutdown-circuit terminal.

The KiCad project is a ConvertEDA import of the EasyEDA original, which is the likely place the
designators were reassigned. Work out the real mapping, then either renumber the connectors in
the KiCad schematic to match the silkscreen or put a loud warning at the top of the netlist and
in `projects/kart-medulla/README.md`. Until that is done, **do not treat the netlist as
authoritative for terminal numbers** — only for nets and part designators.

### Upstream pinout doc disagrees with itself on CMD_STEER_DIR
`dv-hardware/projects/kart-medulla/docs/pinout-esp32-s3.md` has `CMD_STEER_DIR__3V3` on
**GPIO 17** in its pin table (Pin 32, "Moved here from GPIO 0 on 2026-05-08") but its own prose
at the end of the file says "`CMD_STEER_PWM` (GPIO 40) and `CMD_STEER_DIR` (GPIO 0) —
unchanged". kart-docs follows the table (GPIO 17). Fix the prose upstream so the file stops
contradicting itself; the schematic decides.

### Refresh the two rows dv-hardware has not caught up on
`dv-hardware`'s pinout table still lists GPIO 1 as `PRESSURE_3` and GPIO 3 as `BUZZER` in its
`Signal` column, even though the same file's notes describe both reassignments (steering-angle
PWM capture and `CMD_COMPRESSOR_PWM`). kart-docs is ahead on these two rows and now says so
explicitly, but the right fix is upstream — update the `Signal` cells there so the
"dv-hardware wins" rule can go back to being unconditional.

### Settle what powers the Cytron H-bridge — 12 V rail or the 48 V pack
`kart-medulla/index.md` ("powered **permanently from kart 12 V**") and
`electronics/power/battery.md` ("Everything on 12 V hangs off it: ... the steering H-bridge")
both say 12 V. `steering/index.md` says the opposite in three places — "driven from the battery
through the Cytron MD25HV", "The 13S pack (~48 V) through the Cytron driver", and an
"Available voltage" table listing the 13S pack for this actuator — and specs stall as
47 V × 43 A ≈ 2 kW, which is not a 12 V figure. The motor is a 24 V geared unit, so the answer
also changes what speed and torque to expect. Measure at the Cytron's supply terminals and fix
whichever pages are wrong.

### Rewrite the YOLOv5 walkthrough on the camera page for YOLOv11
`assembly/sensors/camera.md` carries a full "Exporting and Using a Custom YOLOv5 Model"
section. The kart runs **YOLOv11n** at `imgsz` 320 (`kart_perception/yolo_detector_node.py`
defaults; weights `ruben_yolov11n_2026_03_320`). A warning banner now sits at the top of the
page, but the export steps and config keys below it are still v5-specific and need redoing.

### Decide whether the kart is presented as a competition entry
`docs/index.md` says "This prototype is not intended to compete, so no specific racing
regulations apply." `docs/rules/as_state_machine.md` calls the kart an "APC entry", tracks
compliance gaps against FS rules ("NOT currently implemented but are required for competition
compliance"), and the repo ships `FS-AI_2026_APC_Technical_Rules_v1.pdf`. `docs/about.md` also
lists competing as a medium-term objective. Pick one position and make the three pages agree.

### Reconcile the mission lists across the docs
Source of truth is `kart-brain`: `state_machine_node.py:34` gates on `autonomous`,
`acceleration`, `skidpad`, `autocross`, `trackdrive`, `ebs_test`, `inspection`, `throttle_test`,
plus `manual` and `remote_control` on the non-autonomous branch. The docs list three different
subsets — `software/state_machine.md` has 9 (no `autonomous`), `software/dashboard.md` has 8
(no `throttle_test`/`ebs_test`), `software/ros2/packages.md` has 6. Also worth flagging in the
docs: `throttle_test` is missing from `protocol.py`'s `MISSIONS` map, so it falls through
`MISSIONS.get(..., 0)` and is transmitted to the ESP32 as **manual** (ID 0).

### Audit the non-electronics docs for contradictions and stale claims
The 2026-07-30 sweep covered `docs/assembly/electronics/**` and `docs/bom/**` only. Everything
else — `docs/software/**`, `docs/assembly/steering/**`, `docs/assembly/sensors/**`,
`docs/assembly/pneumatic-braking/**`, `docs/assembly/powertrain/**`, `docs/rules/**`,
`docs/build-journey/**`, and the top-level pages — was never opened. Those pages predate the
classic-ESP32 → ESP32-S3 change and are likely to repeat retired facts (classic pinout, MCP4728
DAC, `U12` optocoupler, CAN on the kart). Read them against the corrected electronics pages and
fix or file what disagrees.

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
