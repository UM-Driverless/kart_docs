# Hydraulics

The kart keeps its original hydraulic brakes. They are what actually stops the wheels — the
[pneumatic system](../pneumatic-braking/index.md) is the actuator that squeezes them, both for
normal autonomous braking (ASB) and for the emergency circuit (EBS). This page covers the fluid
side: hoses, bleeding, and the pressure sensor that tells the kart how hard it is braking.

The installed brake components and compatible service-spare candidates are listed in the
[hydraulic brake BOM](bom.yaml).

## Brake lines

Flexible brake hoses with `M10x1.0 female inverted flare` connectors.

### Bleeding / purging

The lines have to be purged of air after any work that opens the circuit; trapped air makes the
pedal spongy and the pressure reading meaningless. Reference video for the procedure:
[youtu.be/dXhEvykyabk](https://youtu.be/dXhEvykyabk?si=LNnOBOaIlJ93uHi6).

## Brake pressure sensor — bought, not fitted

!!! warning "This sensor is on hand and unused"
    `~/dv/kart/pneumatics/README.md` records the Sensata unit as *"not used in this system"*, and the
    2026-04 Festo price sheet lists it as *"Not Festo; on hand, currently unused"*. Nothing on the
    kart currently measures hydraulic brake-line pressure. Treat everything below as the plan for
    when it goes in, not as installed hardware.

A **Sensata PTE7100**, recorded in the dv notes as **PTE/700-33**
([datasheet](../../assets/datasheets/sensata_pte7100_hermetic_analog_pressure_sensor_da-1919220.pdf)).
Photos of the actual unit are in `~/dv/kart/pneumatics/pictures/` (`6010450369185516303`,
`6010450369185516304`).

| | |
|---|---|
| Range | 0–200 bar |
| Output | 1–5 V, supply 8–32 Vdc |
| Pressure port | 7/16-20 UNF-2A (male) |
| Seal | HNBR o-ring |
| Electrical connector | Packard Metri-Pack 150 |
| Supplied with | Neither a mating connector nor a snubber — order both separately |

**Adapter to the brake line:** a `male M10x1.0 inverted flare to female 7/16-20 UNF` adapter, since
the sensor's port thread does not match the hoses.

![The Sensata pressure sensor with its adapter](index/20250703193056.png)

When it is fitted, its signal goes to one of the Kart Medulla's two hydraulic-pressure ADC inputs —
see [Kart Medulla](../electronics/kart-medulla/index.md). Its 1–5 V swing is divided down on the
board before reaching the ESP32's 3.3 V ADC.

Not to be confused with the kart's **pneumatic** pressure sensors, which are fitted and reading:
those are Festo SDE5-D10 units on the EBS air circuit, covered on the
[Pneumatic Braking](../pneumatic-braking/index.md) page.

### Possible alternative

[Bosch Motorsport PSS-260](https://xtramotorsport.com/product/bosch-motorsport-pss-260-brake-pressure-sensor/)
(PN 0261545188) — 0.5–4.5 V, 0–260 bar. Not bought; kept as a fallback if the Sensata becomes hard
to source.
