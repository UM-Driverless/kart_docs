---
# BOM Entry
bom:
  component_id: "KUNRAY_MY1020"
  part_number: "MY1020"
  category: "motor"
  quantity: 1
  unit_cost: 150.00
  currency: "EUR"
  status: "active"
  criticality: "essential"
  suppliers:
    - name: "Amazon"
      part_number: "B0C6WXYZ"
      url: "https://www.amazon.es/dp/B0C6WXYZ/ref=cm_sw_em_r_mt_dp_xyz"
      verified: true
    - name: "Kunray Official"
      url: "https://kunraymotors.com/shop/"
      verified: true
  specifications:
    voltage: "72V"
    power: "3000W"
    weight: "8kg"
    shaft_diameter: "10mm"
    shaft_type: "no keyway"
  notes: "Includes motor controller"
---

# Powertrain

## Motor

We use a **Brushless DC (BLDC) motor** from [Kunray](https://kunraymotors.com/shop/) (model **MY1020**, 72V 3000W), along with its supplied controller.  
The motivation for selecting an electric motor over a combustion engine is discussed in the [FAQ](../../faq.md#motor-choice).

---

## Motor Specifications

- **Type:** High-speed BLDC motor (Brushless DC)
- **Model:** Kunray MY1020
- **Nominal voltage:** 48VDC *(?)*
- **Nominal power:** 2000W–2500W *(?)*
- **Nominal current:** *(?)*
- **Rated speed:** *(?)*
- **Max speed:** *(?)*
- **Max torque:** *(?)*
- **Material:** Aluminum housing, full copper winding
- **Weight:** ~8 kg
- **Dimensions:** ~16.9 cm length x 9.6 cm height
- **Shaft:** 10mm diameter, no keyway (non-standard)
- **Product link (Amazon):** <a href="https://www.amazon.es/dp/B0C6WXYZ/ref=cm_sw_em_r_mt_dp_xyz" target="_blank">Kunray 72V 3000W Motor Kit</a>

> **Note:** For transmission system details (chain, sprockets), see [Transmission](../transmission/index.md)

---

## Controller Specifications

- **Input voltage:** 48V *(?)*
- **Max current:** *(?)*
- **Max supported power:** *(?)*
- **MOSFETs:** *(?)*
- **Phase angle:** *(?)*
- **Undervoltage protection:** *(?)*
- **Built-in features:**
  - Reverse mode
  - PWM speed control
  - Three speed modes (low/medium/high)
  - High/low-level braking input
  - Hall sensor support
  - Sensorless mode supported
  - Ignition lock (anti-theft)
  - Cruise control
  - Soft start
  - Twist-grip throttle control
- **Product link (AliExpress):** [Kunray BLDC Controller 72V](https://www.aliexpress.com/item/...)

---

## Throttle Pedal Sensor

The throttle pedal sensor has the following wire assignments:

- **Red:** Vcc  
- **Yellow:** Ground  
- **Green/Blue:** Signal  

The twist-grip throttle that comes with the motor kit also includes:

- **Voltage range:** 12V–72V  
- **Functions:** Throttle signal, 3-speed selector, reverse mode  
- **Cable length:** ~1.5 m  
- **Material:** Rubber + ABS  

---

## Assembly

*This section will include real photos of the kart assembly taken from OwnCloud.*

>  **Important:** During the first installation, the **red steering part** was mounted in the wrong orientation. Refer to these pictures to ensure correct assembly in future setups.

*(Insert images here once available)*

---

## To be added:

- Full wiring table (cable color, pin name, voltage, function)
- Integration with control system (e.g., microcontroller / bluepill)
- DAC details (used to convert PWM signal if applicable)
