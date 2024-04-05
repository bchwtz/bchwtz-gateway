# Sensor

## Hardware

### External Flash Memory
For more extensive data logging external memory (not in the SoC) is required. The most promising candidate is the [Macronix MX25R](https://www.macronix.com/en-us/products/NOR-Flash/Serial-NOR-Flash/Pages/spec.aspx?p=MX25R6435F&m=Serial%20NOR%20Flash&n=PM2138) as it supports low power battery driven applications, is quite flexible in terms of required voltage and is also used in some newer Nordic reference designs.

### Board Redesign
The current sensor board revision features two antennas, while the bluetooth antenna is required and onboard NFC antenna is not used, therefore the board footprint could be smaller. 

Inspiration for a board revision could be drawn from the discontinued [nRF51822 Bluetooth Smart Beacon Kit](https://www.nordicsemi.com/Software-and-tools/Reference-Designs/nRF51822-Beacon-Kit) reference design.


## Software

### General ToDo
- Remotely customizing the Heartbeat interval (persistence required)
- Flexibilizing the Logging Rate so that it can be precisely controlled and the sensor supports rates that the accelerometer does not support natively (e.g. 2 Hz)
- Adapted Advertisement Message Format: Indicate amount of used internal storage to be used by the gateway to trigger connections and manage dowloading of logged data.

### Security

**Questions:**
* Can Advertisements be encrypted?
* How to manage access for downloading internally stored data and allow for encrypted transportation?

