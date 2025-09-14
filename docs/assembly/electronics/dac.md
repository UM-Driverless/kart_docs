### DAC – Digital to Analog Conversion

**Model:** MCP4725 I²C DAC Breakout Module  
**Power supply voltage:** 5V  
**Communication:** I²C @ 3.3V (logic level)  
**Detected issue:**  
The MCP4725 operates at 5V for power, but its I²C communication lines also run at that voltage. This creates a level mismatch when interfacing with a 3.3V microcontroller like the ESP32, which may result in communication errors or even damage to the I²C pins.

**Proposed or pending solution:**  
Use a **bidirectional I²C level shifter** (e.g., TXS0108E or BSS138-based) between the microcontroller and the DAC to safely interface 3.3V and 5V logic.
