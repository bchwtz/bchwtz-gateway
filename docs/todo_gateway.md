# Gateway

## Hardware

### Uninterruptible Power Supply
For operating in remote environments the gateway should be equipped with a Uninterruptible Power Supply (UPS). This allows tolerating short power outages and should be configurable to user alternative energy sources such as solar panel or wind turbines to allow for autonomous operation.

The most promising products are:
* [PiJuice Hat](https://uk.pi-supply.com/products/pijuice-standard?lang=de)
* [Sixfab UPS Power Hat](https://sixfab.com/product/raspberry-pi-power-management-ups-hat/)
* [UPS PIco HV4.0B Advanced](https://pimodules.com/product/ups-pico-hv4-0-advanced)

**Questions:**
* How to work with unregulated power sources such as cheap/raw solar panels?
* Which UPS provides the best software (Free/Open/Functionality/Reliability)?

### Camera
A camera is required to record a video stream that is used to derive the ground truth for classification tasks. Use cases can be extended to perform analytics based on the captured images or the video stream.

#### RPi Camera
The main camera for the gateway will be the original camera module offered by the Raspberry Pi Foundation, which provides the benefit of an actively maintained software interface and guaranteed compatibility with the used Single Board Computer (SBC). Additionally it is available in two versions, a *normal* and a NoIR (Night Vision) Version. 

**Questions:**
* How to match the video feed with the data that is received via Bluetooth?
* Which illumination is required for the NoIR Version?
* Is it possible to mechanically align the angles (perfect Video overlay) and use both camera versions simultaneously?

#### Thermal Camera
For some use cases it may be reasonable to monitor temperatures via a thermal camera. The thermal camera should be seen as an optional addition to the gateway. 

**Questions:**
* Which module should be chosen in terms of features (especially resolution and connection) and size?
* How to align images from all installed cameras (perfectly aligned video stream)?

### 3g/4g/5g Module
Autonomous operation requires a network connection for control and (at least partial) data transfer.

**Questions:**
* Which module can be used solely via the GPIO Header (no USB Cable)?
* Which module offers the best software interaface( Free/Open/Functionality/Reliability)?

### Bluetooth Hardware
Alternating and/or extending the Bluetooth Hardware serves two purposes. Having multiple bluetooth devices should allow for monitoring more sensors simultaneously. Including at least one device with support for external antennas would also allow for increased range. Achieving this goal could can be done using at least one (but potentially both) of the following measures:

1. Adding external Bluetooth Hardware
2. Changing the Single Board Computer (SBC)


### Case

Heat Sink / Active Ventilation


## Software

- Scheduling and parallelizing download of logged Data
