from gatewayn.tag.tag import Tag
from bleak.backends.device import BLEDevice
from typing_extensions import Self
import aiopubsub

from gatewayn.sensor.sensor import Sensor
from gatewayn.sensor.temperature import TemperatureSensor
from gatewayn.sensor.humidity import HumiditySensor
from gatewayn.sensor.acceleration import AccelerationSensor
from gatewayn.sensor.barometer import BarometerSensor

class TagBuilder:
    def __init__(self) -> None:
        self.tag_ble_device: BLEDevice = None
        self.tag_name: str = ""
        self.tag_address: str = ""
        self.tag_online: bool = True
        self.tag_sensors = []
        self.tag_pubsub_hub: aiopubsub.Hub = None

    def from_device(self, device: BLEDevice, pubsub_hub: aiopubsub.Hub = None) -> Self:
        self.tag_ble_device: BLEDevice = device
        self.tag_name = device.name
        self.tag_address = device.address
        self.tag_sensors = [
            TemperatureSensor(),
            HumiditySensor(),
            AccelerationSensor(),
            BarometerSensor(),
        ]
        self.tag_online = True
        self.tag_pubsub_hub = pubsub_hub
        return self

    def name(self, name: str = "") -> Self:
        self.tag_name = name
        return self

    def address(self, address: str = "") -> Self:
        self.tag_address = address
        return self

    def ble_device(self, ble_device: BLEDevice) -> Self:
        self.tag_ble_device = ble_device
        return self

    def online(self, online: bool = True) -> Self:
        self.tag_online = online
        return self

    def build(self) -> Tag:
        tag = Tag(name=self.tag_name, address=self.tag_address, device=self.tag_ble_device, online=self.tag_online, pubsub_hub=self.tag_pubsub_hub)
        return tag