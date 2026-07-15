# BMS (battery node)

The `kb_bms` package is a ROS 2 node that reads the traction pack's **smart BMS over Bluetooth Low Energy (BLE), directly from the Jetson Orin** — there is no ESP32 and no CAN bus in this path. It publishes a standard `sensor_msgs/BatteryState` on `/battery/state`, which the dashboard turns into the battery gauge and battery tab.

**Source:** `src/kb_bms/kb_bms/bms_node.py`

!!! info "Why BLE straight from the Orin?"
    The pack uses a JBD / Xiaoxiang smart BMS with a built-in BLE module (the same one the vendor's phone app talks to). Connecting the Orin's Bluetooth radio to it means the battery reading works **even when the ESP32 serial link is down** — which is exactly when the dashboard's battery gauge would otherwise read `--`. See the hardware side on the [Battery](../../assembly/electronics/power/battery.md) page.

---

## Node overview

| | |
|---|---|
| **Package** | `kb_bms` (Python, `ament_python`) |
| **Node** | `kb_bms` |
| **Publishes** | `/battery/state` (`sensor_msgs/BatteryState`, QoS: reliable, depth 10) |
| **Dependency** | [`bleak`](https://github.com/hbldh/bleak) (cross-platform BLE), plus `bluetoothctl` for self-heal |

### Parameters

| Parameter | Default | Description |
|---|---|---|
| `mac` | `A5:C2:37:39:58:5D` | BLE MAC address of the BMS |
| `name` | `SP22S003BP21S100A` | BMS advertised name (fallback if the MAC connect fails) |
| `publish_period` | `1.0` | Seconds between `/battery/state` publishes |

The default MAC/name identify the kart's JBD `SP22S003B` unit (100 A, up to 21S). Override with `--ros-args -p mac:=...` if the BMS is swapped.

---

## Threading model

The node keeps ROS and BLE on separate threads, matching the dashboard node's pattern:

- **BLE thread (background):** runs bleak's asyncio loop — connect → subscribe to the notify characteristic → poll the pack → parse → stash the latest reading under a lock. It reconnects forever on any failure (pack powered off, BLE drop, out of range) without ever killing the node.
- **Spin thread (ROS):** a ROS timer publishes the latest stashed reading every `publish_period`.

!!! warning "Publishing must happen on the spin thread"
    Publishing happens **only** from the ROS timer. Cross-thread `rclpy` publishing from the asyncio thread silently no-ops, so the BLE thread only ever updates the shared `_latest` dict under a lock; the timer reads it and publishes.

### Connect and self-heal

On each connection attempt the node first tries the plain `mac`. If that fails it scans by `name` (BLE addresses can rotate, but the model name is stable) and connects to whatever device matches.

If the BMS is unreachable for several consecutive tries (every 3rd failure), the node runs `bluetoothctl disconnect` and `remove` on the MAC. This clears a stale BlueZ state where a crashed/leaked client leaves BlueZ holding `Connected: yes`: while "connected" the BMS stops advertising, so both connect-by-MAC and scan-by-name fail forever until a human intervenes. Forcing BlueZ to drop and forget the device lets the next attempt rediscover it fresh.

---

## JBD BLE protocol

Two GATT characteristics carry everything (16-bit UUIDs expanded onto the Bluetooth base UUID):

| Role | UUID |
|---|---|
| **Write** (send command) | `0000ff02-0000-1000-8000-00805f9b34fb` |
| **Notify** (receive reply) | `0000ff01-0000-1000-8000-00805f9b34fb` |

The node writes a fixed command to the write characteristic (`response=False`), waits ~0.6 s, then reassembles the reply from the notification bytes.

### Commands

| Command | Bytes (hex) | Register | Returns |
|---|---|---|---|
| Basic info | `DD A5 03 00 FF FD 77` | `0x03` | Pack summary (voltage, current, SOC, temps, …) |
| Cell voltages | `DD A5 04 00 FF FC 77` | `0x04` | Per-cell millivolts |

### Frame format

Replies are big-endian frames:

```
DD <reg> <status> <len> <payload…> <chk_hi> <chk_lo> 77
```

The node scans the notification buffer for `DD … 77` frames and parses the payload of length `<len>`.

**Register 0x03 (basic) payload offsets** — parsed into a dict:

| Field | Offset / source | Encoding |
|---|---|---|
| `voltage` | bytes 0–1 | `u16 / 100` → volts |
| `current` | bytes 2–3 | `s16 / 100` → amps (signed: + charge, − discharge) |
| `remain_ah` | bytes 4–5 | `u16 / 100` → Ah remaining |
| `nominal_ah` | bytes 6–7 | `u16 / 100` → Ah nominal |
| `cycles` | bytes 8–9 | `u16` |
| `protection` | bytes 16–17 | `u16` protection-status bitfield (0 = no faults) |
| `soc` | byte 19 | percent (0–100) |
| `n_cells` | byte 21 | cell count |
| `temps` | byte 22 = NTC count, then `u16` each from byte 23 | `(raw − 2731) / 10` → °C (raw is deci-kelvin) |

**Register 0x04 (cells) payload:** a list of `u16` values, one per cell, in millivolts.

---

## Published `BatteryState` fields

The timer maps the parsed dict onto `sensor_msgs/BatteryState`:

| `BatteryState` field | Source | Notes |
|---|---|---|
| `voltage` | `voltage` | pack volts |
| `current` | `current` | + charging, − discharging |
| `charge` | `remain_ah` | Ah remaining |
| `capacity` | `remain_ah` | Ah remaining (same as `charge`) |
| `design_capacity` | `nominal_ah` | Ah nominal |
| `percentage` | `soc / 100` | 0.0–1.0 |
| `temperature` | `temps[0]` | first NTC in °C, or `NaN` if none |
| `present` | reading age < 10 s | false when the last successful read is stale |
| `power_supply_status` | from `current` | `CHARGING` if > 0.2 A, `DISCHARGING` if < −0.2 A, else `NOT_CHARGING` |
| `power_supply_health` | from `protection` | `GOOD` if `protection == 0`, else `UNKNOWN` |
| `power_supply_technology` | constant | `LION` |
| `cell_voltage[]` | `cells` | per-cell volts (mV ÷ 1000) |
| `cell_temperature[]` | `temps` | all NTCs in °C |

---

## How the dashboard consumes it

The [`kb_dashboard`](packages.md#kb_dashboard) node subscribes to `/battery/state` and feeds two UI areas (`dashboard_node.py::_on_battery`):

- **Telemetry BATT gauge** — `voltage` number and an SOC dial from `percentage`.
- **Battery tab** — current, remaining charge, temperature(s), and a per-cell voltage strip from `cell_voltage[]` (rendered in mV).

Because the node publishes independently over BLE, the battery readout stays live regardless of the ESP32 serial link state.

---

## Running it

`kb_bms` is started as part of the dashboard/bringup launches, or standalone:

```bash
ros2 run kb_bms bms_node

# Watch the published state
ros2 topic echo /battery/state --once

# Override the target BMS
ros2 run kb_bms bms_node --ros-args -p mac:=AA:BB:CC:DD:EE:FF
```

!!! tip "BLE prerequisites on the Orin"
    The Orin's Bluetooth must be up and `bleak` installed. If the gauge stops updating, check the node logs — it prints `BMS connected (<addr>)` on success and `BMS BLE error (…); retrying in 5s` while it cannot reach the pack.

See also: [Packages → kb_bms](packages.md#kb_bms) and the hardware [Battery](../../assembly/electronics/power/battery.md) page.
