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
- **Sprocket:** T8F 11T (compatible with T8F chain)
- **Material:** Aluminum housing, full copper winding
- **Weight:** ~8 kg
- **Dimensions:** ~16.9 cm length x 9.6 cm height
- **Product link (Amazon):** [Kunray 72V 3000W Motor Kit](https://www.amazon.es/dp/B0C6WXYZ/ref=cm_sw_em_r_mt_dp_xyz)

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
