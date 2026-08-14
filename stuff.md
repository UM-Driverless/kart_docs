# stuff.md
This file is to paste random links with no order or structure when no clear place exists for them or maybe they are not relevant enough to be documented. Just put it in here in case it is useful later.

- Seeed XIAO ESP32C3 microcontroller connected to a matching CAN bus breakout board. These boards provide a compact and inexpensive way to interface with the kart's electronics.
    - https://www.seeedstudio.com/Seeed-Studio-CAN-Bus-Breakout-Board-for-XIAO-and-QT-Py-p-5702.html?srsltid=AfmBOooOSsP4wEzBwZ_tEvypCTqoEWubQBnAdiPAb93lrFVh4PwPtZyo
    - https://www.seeedstudio.com/Seeed-XIAO-ESP32C3-p-5431.html?srsltid=AfmBOoqQL7ELWi1TzG4-n3cpRV_ZJvhqvYwIAZiPaPFKksbLwGAYxiHz


# to note which executable environment is used by uv
Show Python executable path:
`uv run python -c "import sys; print(sys.executable)"`

Show virtual environment location:
`uv venv --help` or check `.venv/` directory


# Cheap phones for kart HMI dashboard (second-hand, USB-C)
Use any phone as a wireless touchscreen dashboard for the Orin — just a browser in kiosk mode pointing at a web UI served by the Orin over WiFi. No Nextion needed.

Good second-hand options (Wallapop, ~30-60€):
- **Xiaomi Redmi Note 10/11** — big 6.5" screen, USB-C, everywhere on Wallapop
- **Xiaomi Poco X3 NFC/Pro** — big screen, USB-C, dirt cheap used
- **Samsung Galaxy A13/A14** — USB-C, 6.6" screen, common
- **Samsung Galaxy S10e** — compact, IP68, AMOLED (great outdoors), USB-C
- **Google Pixel 4a** — clean Android, OLED, USB-C, easy kiosk mode

For now: just use our own phones. Buy a dedicated one later if the dashboard works well.

Kiosk app: [FreeKiosk](https://github.com/RushB-fr/freekiosk) (free, open-source, locks phone to one browser tab)
Dashboard: [ROSboard](https://github.com/dheera/rosboard) (`pip install rosboard`) for instant ROS2 topic visualization + custom FastAPI for mission control buttons.

# CAN-bus parts, if the kart ever gets a CAN link (moved here from TODO.md, 2026-08-14)
There is no CAN on the kart today — the Orin talks to the medulla over plain USB serial. GPIO 41/42
on the ESP32-S3 are held unassigned in case that changes. Part that was being considered:
- CAN driver module: https://es.aliexpress.com/item/1005006299445174.html
