# H-bridge data
- **Cytron MD25HV** (25 A cont, 60 A peak, 7V-58V)
    - Product page: <https://www.cytron.io/p-25amp-7v-58v-high-voltage-dc-motor-driver>
    - Datasheet: <https://docs.google.com/document/d/1xJHVG2dc3aEtedCHf3L9NzUy5KqpxeWjeS9Lfh9XuqA>
    - GitHub library: <https://github.com/CytronTechnologies/CytronMotorDriver>
    - Tutorial: <https://www.cytron.io/tutorial/controlling-md10c-with-arduino>
    - Tutorial: <https://www.instructables.com/Controlling-Motor-Speed/>
    - **Note**: Upgraded from MD30C to support 13S battery (41.6V-54.6V). MD30C was limited to 30V max.

### Reasoning
Suggested H-bridges by gpt:

- **Cytron MD25HV** (25 A cont, 60 A peak, 7V-58V) - **CURRENT CHOICE**
- ~~**Cytron MD30C** (30 A cont, 80 A peak, 5V-30V) - Insufficient voltage rating for 13S battery~~
- **Pololu VNH5019 Driver** (12 A cont, 30 A peak)
    - <https://www.pololu.com/product/1451?utm_source=chatgpt.com>
- ~~Sabertooth 2x32: Overkill but excellent for dual motors, up to 32 A per channel~~
- ~~Simple BTS7960: Cheap dual half-bridge module, supports 43 A per channel, needs external PWM and logic control~~
- ~~IBT-4~~
    - Needs two synced pwm signals to control the H bridge, so it's harder to use. Otherwise it would work and it's cheaper

## Alternative motor controllers (investigated, not adopted)

Beyond a plain H-bridge, a few integrated speed/servo controllers were considered. None replaced the MD25HV, but they're worth knowing about if the control approach is ever revisited.

??? info "Driver alternatives (click to expand)"

    #### VESC (Vedder Electronic Speed Controller)
    - **Advantages**: multi-purpose, can be reused for other systems.
    - **Implementation**: test with an existing unit first; ESP32 communication via UART at 3.3 V; keep the AS5600 magnetic sensor on I²C. Note: VESC DC mode doesn't include position control, so an external PID is still needed.
    - **Alternative unit**: [Flysky FSESC67100 V2 Pro on Wallapop](https://es.wallapop.com/item/flysky-fsesc67100-v2-pro-1133224964)

    #### Kelly Controller KDS series
    - **Link**: [Kelly Controller shop](https://kellycontroller.com/shop/kds/)
    - **Specs**: ~60 €, 48 V (max 60 V), 50 A.
    - **Control**: 0–5 V analog for power, REV/DIR signal for direction. Requires an external microcontroller with PID for position control.

    #### AllMotion EZSV23WV servo controller
    - **Link**: [AllMotion EZSV23WV](https://www.allmotion.com/ezsv23wv-servo-control)
    - Integrated servo-control solution.

    #### Generic PWM motor controller
    - **Link**: [Component Authority DC motor controller](https://componentauthority.com/products/dc-10-55v-max-60a-pwm-motor-speed-controller-cw-ccw-reversible-12v-24v-36v)
    - **Specs**: 10–55 V DC, max 60 A, CW/CCW reversible. Works like the current Cytron solution — use with an ESP32 for the same control method.
