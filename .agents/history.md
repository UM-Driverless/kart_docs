<!-- consult selectively — grep, never read in full -->

# History

Append-only log of notable decisions and events for `kart_docs`. Newest at the bottom.

---

## 2026-04-13 — Kart Medulla MCU: classic ESP32 → ESP32-S3 (docs reframed)

**Decision.** The next revision of the Kart Medulla interface PCB targets the **ESP32-S3** (ESP32-S3-WROOM-1 module). The classic ESP32 (ESP32-WROOM-32 on a DevKitC V4) is retired as the target MCU for new hardware.

**Status at decision time.** No Kart Medulla PCB has been manufactured. The classic ESP32 is currently hand-wired directly in the kart for basic functionality — this continues to be the operational setup until the S3 PCB is built and flashed.

**Why.**

- **Pin count.** The classic ESP32 ran out of usable GPIOs once CAN, SPI, status RGB, buzzer, and the Orin link were added on top of 3× halls, 3× pressure, accelerator, brake, SDC, steering, and relay. Too many classic-ESP32 GPIOs are reserved for flash/SDIO or are strap-pin traps. The S3 offers ~45 usable GPIOs.
- **Native USB-OTG.** Orin link moves from UART (through an external USB-UART bridge chip) to direct USB CDC-ACM — drops a BOM item, raises throughput from ~1 Mbit/s to ~12 Mbit/s full-speed USB, and gives hot-plug handling for free.
- **Built-in USB-Serial-JTAG.** Flash + serial monitor + step-debugging over one USB cable. No external ESP-Prog / FT2232H.

**Trade-off accepted.** The S3 has no built-in DAC, so `CMD_ACC` (5V analog throttle output) now comes from an external **MCP4728** (quad 12-bit I²C DAC) on the interface PCB. 12-bit vs the classic's 8-bit is a resolution upgrade. MCP4728 shares the existing I²C bus, so no additional GPIO cost.

**Variants considered and rejected.** ESP32-S2 (has DAC but single-core, no BT), ESP32-C3 (too few GPIOs), ESP32-C6 (no DAC, Wi-Fi 6 unnecessary for a kart), ESP32-H2 (no Wi-Fi).

**Docs reframe performed today.**

- `docs/assembly/electronics/kart-medulla/index.md` — rewritten around ESP32-S3 (new pinout table, hardware decisions, Why-S3 rationale).
- `docs/assembly/electronics/kart-medulla/legacy-wiring.md` — new page preserving the classic ESP32 hand-wiring as currently deployed in the kart. **Temporary** — to be removed once the S3 PCB is deployed.
- `mkdocs.yml` — nav renamed "Kart Medulla (ESP32)" → "Kart Medulla (ESP32-S3)" with the legacy page nested under it.
- `docs/assembly/electronics/bom.yaml` — added `esp32_s3` entry (status `planned`); `esp32_wroom_32` demoted to `status: legacy` with a pointer to the legacy wiring page.
- `docs/bom/index.md` — now lists both MCUs.
- `docs/assembly/electronics/orin-setup.md` — PlatformIO flashing snippet now shows both environments (`esp32dev` for the legacy setup, `esp32-s3-devkitc-1` for when firmware migrates).

**Pointers to deeper context.**

- PCB project + `.epro` backups + full decision log: Drive folder `formula_24-25-26/dv/kart/kart-medulla/` — especially `README.md`, `history.md`, and `pinout-esp32-s3.txt` (which keeps both classic and S3 pinouts side-by-side as a reference).
- EasyEDA project: account `dv.umotorsport@gmail.com`, Personal Workspace, project ID `5b30b0a2e25c44179a5af8629b1dff0d`.

**Follow-ups.**

- Firmware (`kart_medulla` repo) needs to gain a working `esp32-s3-devkitc-1` PlatformIO/IDF configuration. `sdkconfig.esp32-s3-devkitc-1` is already present; pinout in firmware will need updating to match the S3 assignments once they're finalized during PCB layout.
- Delete `legacy-wiring.md` once the S3 PCB is manufactured, flashed, and deployed in the kart.
