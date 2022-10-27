from gateway.tag.tag import Tag
from bleak.backends.device import BLEDevice
from typing_extensions import Self
import aiopubsub

from gateway.sensor.sensor import Sensor
from gateway.sensor.temperature import TemperatureSensor
from gateway.sensor.humidity import HumiditySensor
from gateway.sensor.acceleration import AccelerationSensor
from gateway.sensor.barometer import BarometerSensor

class TagBuilder:
    """ Helper to be able to easily build Tags
    """
    def __init__(self) -> None:
        """ Sets up a new TagBuilder
        """
        self.tag_ble_device: BLEDevice = None
        self.tag_name: str = ""
        self.tag_address: str = ""
        self.tag_online: bool = True
        self.tag_sensors = []
        self.tag_pubsub_hub: aiopubsub.Hub = None

    def from_device(self, device: BLEDevice, pubsub_hub: aiopubsub.Hub = None) -> Self:
        """ Creates a new tag from its ble_device
            Arguments:
                device: the ble_device gained by discovery or an advertisement
                pubsub_hub: important object for internal events
        """
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
        """ Sets the name of the device
            Arguments:
                name: the name of the ble_device
        """
        self.tag_name = name
        return self

    def address(self, address: str = "") -> Self:
        """ Sets the address of the device
            Arguments:
                address: the mac address of the ble_device
        """
        self.tag_address = address
        return self

    def ble_device(self, ble_device: BLEDevice) -> Self:
        """ Sets the ble_device
            Arguments:
                ble_device: the ble_device discovered by bleak
        """
        self.tag_ble_device = ble_device
        return self

    def online(self, online: bool = True) -> Self:
        """ Sets the online status of the device
            Arguments:
                online: Status of the device
        """
        self.tag_online = online
        return self

    def build(self) -> Tag:
        """ builds a new tag from the predefined values in the builder
            Returns:
                A new tag
        """
        tag = Tag(name=self.tag_name, address=self.tag_address, device=self.tag_ble_device, online=self.tag_online, pubsub_hub=self.tag_pubsub_hub)
        return tag