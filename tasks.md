<!-- consult-selectively: the project's task board (one per repo, at the root). Claim a task by setting status In progress + your id, commit, then Done. -->
# Task Board

Done items do not stay on the board. When one closes, move it — with its date and closing note —
to `tasks/done-archive.md`, which holds nothing actionable. Exception: a done step of a task that is
still open stays put, since archiving it strips the remaining open step of the context saying what
was already settled. A cluster moves to the archive whole, once its last step closes.

## Ready

### Add a pulldown on CMD_STEER_PWM so a resetting ESP32 cannot drive the steering motor
On 2026-08-08 the steering swung hard to one lock while the ESP32-S3 was being reflashed and
broke teeth off the steering gears. The kart was in autonomous at the time. Rubén's reading of
the event is that the swing happened during the flash itself, while the chip sat in the
bootloader running no code at all — which means no firmware change and no change on the Orin
can prevent a repeat, because nothing on the ESP32 is executing during that window.

The board has no hardware default for steering. `docs/assembly/electronics/kart-medulla/index.md`
states it plainly: "Steering is NOT muxed — the ESP32 always drives the Cytron H-bridge
directly; in manual mode firmware sets PWM = 0." So the steering's only safety is firmware
writing zero, which by definition does not exist while the chip is unbooted, resetting, or
crashed. `CMD_STEER_PWM` (CN9.1, ESP32-S3 GPIO 40) is left floating in all three cases, and a
floating CMOS line can sit above the Cytron MD25HV's input threshold indefinitely.

Fix: a pulldown from `CMD_STEER_PWM` to GND, at the Cytron end of the net so it also protects
against the connector being unplugged. 10 kΩ matches the pulldown already used on this board
for `SELECT_THROTTLE` (GPIO 15) and is nowhere near the ESP32's drive limit. The firmware
drives the Cytron in sign-magnitude mode — PWM duty for magnitude, a separate DIR pin for sign
(`km_act`) — so zero on the PWM line means the motor is off and DIR does not matter. **Confirm
the Cytron's mode switches actually select sign-magnitude before relying on that**: in a
locked-antiphase mode a low PWM line would mean full reverse, i.e. the pulldown would cause the
exact failure it is meant to prevent. A second pulldown on `CMD_STEER_DIR` (CN8.3) is cheap and
makes the resting direction deterministic.

This is the same protection throttle already has and steering was never given. Do it as a
rework on the current board, not only in v2 — the kart is being flashed regularly today.

Worth confirming with a meter while the fix is being made: probe CN9.1 against GND, motor
unplugged, and flash. A reading clearly above 0 V during the bootloader window confirms the
mechanism; near 0 V the whole time means the cause was something else and the fix is the
firmware/Orin side instead (see kart-brain `tasks.md`, same date).

Until the resistor exists, the operating rule is to de-power the Cytron or unplug the steering
motor before every flash.

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

## In progress

_(none)_

## Done

### The wiring SVG showed the Cytron on 12 V — fixed (2026-08-08)

The 2026-07-30 decision below fixed `wiring.yaml` and the prose pages but never reached
`wiring/images/wiring-global.svg`, which still had the Cytron box at `25 A · 12 V`, the steering
motor at `DC 12 V`, and a red wire drawn from the **12 V rail** labelled `12 V → Cytron`. The
third was a topology error, not a wording one, so it needed a reroute: the feed now branches off
the battery run at (900, 1410) and reaches the Cytron via the x = 1610 corridor, in bold stroke
per the legend's "bold = 48 V". Rubén confirmed the same day: "cytron is powered directly from
the battery". The Cytron box now reads `25 A · 7–58 V in` (its actual input range) and the motor
box `fed from the 48 V bridge`.

### Cytron H-bridge runs off the 48 V pack, not the 12 V rail (2026-07-30)
Settled by Rubén. `steering/index.md` was right; `kart-medulla/index.md` and
`power/battery.md` were wrong and are fixed. In `wiring/wiring.yaml` the Cytron's supply pin
moved from the `12V` net to `PACK48` and was renamed `v12` → `vin`, and the `STEER_M+`/`STEER_M-`
motor leads are re-labelled 48 V. The MD25HV accepts 7–58 V so the pack is in spec. The
"permanent, not switched through the mode switch" part of the original decision stands — that
was about inrush browning out the Orin, not about which rail.

### PCB fabrication sponsor identified: AISLER (2026-07-30)
Named in the 2026-07-29 LinkedIn post ("Thanks to AISLER for sponsoring the fabrication").
Added to `docs/credits.md` under Partners & sponsors, and the TODO comment removed.

### Reconciled the mission lists across the docs (2026-07-30)
The three pages listed three different subsets. Authoritative set taken from
`kart_control/scripts/state_machine_node.py:34` (`AUTONOMOUS_MISSIONS`) plus the
`manual`/`remote_control` branch at `:148`: ten missions total. `software/state_machine.md`
now carries the full list and cites its source; `dashboard.md` and `ros2/packages.md` say which
eight have buttons and link to it. Recorded there as a known bug: `throttle_test` is gated as
autonomous but missing from `protocol.py`'s `MISSIONS` map, so `MISSIONS.get(..., 0)` sends it
to the ESP32 as `manual` (ID 0).

### Audited the non-electronics docs for contradictions and stale claims (2026-07-30)
Covered `docs/software/**`, `docs/assembly/{steering,sensors,pneumatic-braking,powertrain}/**`,
`docs/rules/**`, `docs/build-journey/**` and the top-level pages, checked against the
`kart-brain` source and the live Orin. Findings and fixes are in `history.md` (2026-07-30).
What could not be settled from the desk was split back out into its own Ready entries.

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

## Build-journey mini-entries (added 2026-08-07) — status: Ready (blocked on media)
Convention in `AGENTS.md` (build-journey section): small dated entries for build moments too minor for a LinkedIn post, no LinkedIn link, mirrored to the portfolio build journey. First two to write, both waiting on photos + facts from Rubén:
- Steel steering gear arrived (replaces the worn 3D-printed gear the steering posts documented).
- MOSFET driver board 3.3 V fix (5 V-designed input stage: bridge rectifier removed, input resistor swapped; verify part numbers/values against the schematic in `~/dv/kart/kart-medulla/` before publishing).
