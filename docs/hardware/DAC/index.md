### DAC – Digital to Analog Conversion

**Model:** [full name of the chip or board]  
**Power supply voltage:** 5V  
**Communication:** I2C @ 3.3V  
**Detected issue:**  
The DAC requires a 5V power supply, but the I2C line operates at 3.3V. This may damage the microcontroller or cause communication failures.

**Proposed or pending solution:**  
Use a **bidirectional I2C level shifter** (e.g., TXS0108E or BSS138) between the microcontroller and the DAC.
