# Introduction

As a brief introduction to the python library it makes sense to have a view on this class diagram of the library:

``` mermaid
classDiagram
  Sensor <|-- HumiditySensor
  Sensor "n" <-- "1" Tag:has
  Measurement "n" <-- "1" Sensor:has
  HumidityMeasurement "n" <-- "1" HumiditySensor:has
  BLEConn "1" <-- "1" Hub:uses

  link Hub "/hub_ref/#gatewayn.hub.hub.Hub" "Hub"
  link Tag "/tag_ref/#gatewayn.tag.tag.Tag" "Tag"
  link Sensor "/sensor_ref/#gatewayn.sensor.sensor.Sensor" "Sensor"
  link HumiditySensor "/sensor_ref/#gatewayn.sensor.humidity.HumiditySensor" "Sensor"
  link Measurement "/sensor_ref/#gatewayn.sensor.measurement.Measurement" "Measurement"
  link HumidityMeasurement "/sensor_ref/#gatewayn.sensor.humidity.HumiditySensor.HumidityMeasurement" "HumidityMeasurement"
  link BLEConn "/ble_conn_ref/#gatewayn.drivers.bluetooth.ble_conn.ble_conn.BLEConn" "BLEConn"


  Tag "n" <-- "1" Hub:has
  class Sensor {
    +String name
    +[Measurement] measurements
  }

  class Tag{
    +String address
    +String name
  }
  class Hub{
    +String sensors
    +BLEConn ble_conn
  }
  class Measurement{
    +any measurement
    +[any] measurements
  }
  class HumiditySensor{
    +[HumidityMeasurement] measurements
  }
  class HumidityMeasurement{
    +float humidity
  }
  class BLEConn{
    +logging.logger logger
    scan_tags(manufacturer_id: int = 0, timeout: float = 20.0)
    listen_advertisements(timeout: float = 5.0, cb: Callable[[BLEDevice, dict], None] = None)
  }
```
In the diagram you can see the actual links and references of the different classes inside the library. If you need the implementation reference for a single class in this diagram, just click on its box and you will be forwarded to the correct page.

This is how the gateway listens for advertisements and sets up new tags:

``` mermaid
sequenceDiagram
  Gateway->>Hub: __init__()
  activate Hub

  loop listen_advertisements
    Gateway->>Hub: listen_advertisements(timeout=20)
    activate Hub
    Hub->>Gateway: return None
    Hub->>BLEConn: listen_advertisements(cb)
    deactivate Hub
  end
  Note right of Hub: startup procedure
  BLEConn-->>Hub: listen_advertisement_cb(msg)
  activate Hub
  Hub->>Tag: __devices_to_tags()
  activate Tag
  Tag->>Hub: adds the Tag to taglist of hub
  deactivate Tag
  deactivate Hub
```