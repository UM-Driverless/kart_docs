# Powertrain

## Motor

We use a **Brushless DC (BLDC) motor** from [Kunray](https://kunraymotors.com/shop/) (model **MY1020**, 48V 2000W), along with its supplied controller.  
The motivation for selecting an electric motor over a combustion engine is discussed in the [FAQ](../../faq.md#motor-choice).

---

## Motor Specifications

- **Type:** High-speed BLDC motor (Brushless DC)
- **Model:** Kunray MY1020
- **Nominal voltage:** 48VDC (13S battery configuration)
- **Nominal power:** 2000W
- **Nominal current:** *(to be confirmed)*
- **Rated speed:** *(to be confirmed)*
- **Max speed:** *(to be confirmed)*
- **Max torque:** *(to be confirmed)*
- **Sprocket:** T8F 11T (compatible with T8F chain)
- **Material:** Aluminum housing, full copper winding
- **Weight:** ~8 kg
- **Dimensions:** ~16.9 cm length x 9.6 cm height
- **Product link (AliExpress):** [Kunray 48V 2000W Motor Kit](https://a.aliexpress.com/_EGHEGIw)

---

## Controller Specifications

- **Input voltage:** 48V
- **Max current:** *(to be confirmed)*
- **Max supported power:** 2000W
- **MOSFETs:** *(to be confirmed)*
- **Phase angle:** *(to be confirmed)*
- **Undervoltage protection:** *(to be confirmed)*
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
