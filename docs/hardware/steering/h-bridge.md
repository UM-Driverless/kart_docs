# H-bridge data
- **Cytron MD30C** (30 A cont, 80 A peak)  
    - https://www.cytron.io/p-30amp-5v-30v-dc-motor-driver  
    - Bought here to ship to Spain: https://opencircuit.es/producto/30amp-5v-30v-dc-motor-driver
    - https://www.cytron.io/p-30amp-5v-30v-dc-motor-driver?srsltid=AfmBOoo-TCLyyRQ5SBEhwpIMcAhQIaXDzO-NgCP_LdYCx8KNeVAThvSF  
    - https://docs.google.com/document/d/178uDa3dmoG0ZX859rWUOS2Xyafkd8hSsSET5-ZLXMYQ/view  
    - https://github.com/CytronTechnologies/CytronMotorDriver
    - https://www.cytron.io/tutorial/controlling-md10c-with-arduino
    - https://www.instructables.com/Controlling-Motor-Speed/

### Reasoning
Suggested H-bridges by gpt:
r
- **Cytron MD30C** (30 A cont, 80 A peak)  
- **Pololu VNH5019 Driver** (12 A cont, 30 A peak)  
    - https://www.pololu.com/product/1451?utm_source=chatgpt.com  
- ~~Sabertooth 2x32: Overkill but excellent for dual motors, up to 32 A per channel~~  
- ~~Simple BTS7960: Cheap dual half-bridge module, supports 43 A per channel, needs external PWM and logic control~~  
- ~~IBT-4~~
    - Needs two synced pwm signals to control the H bridge, so it's harder to use. Otherwise it would work and it's cheaper