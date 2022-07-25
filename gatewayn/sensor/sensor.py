import asyncio
from typing_extensions import Self
from bleak.backends.device import BLEDevice
from gatewayn.drivers.bluetooth.ble_conn.ble_conn import BLEConn

class Sensor():
    def __init__(self, name: str = "", address: str = "", device: BLEDevice = None) -> None:
        self.name: str = name
        self.address: str = address
        self.bleDevice: BLEDevice = device
        self.main_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()

    def from_device(device: BLEDevice) -> Self:
        sensor = Sensor()
        sensor.bleDevice: BLEDevice = device
        sensor.name = device.name
        sensor.address = device.address
        return sensor
