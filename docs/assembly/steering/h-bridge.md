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
