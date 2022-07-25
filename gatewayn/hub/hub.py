import asyncio
from gatewayn.sensor.sensor import Sensor
from gatewayn.drivers.bluetooth.ble_conn.ble_conn import BLEConn
from bleak.backends.device import BLEDevice

class Hub():
    def __init__(self):
        self.main_loop = asyncio.get_event_loop()
        self.sensors: list[Sensor] = []
        self.ble_conn = BLEConn()

    def discover_sensors(self, timeout = 5.0):
        self.sensors = []
        devices = self.main_loop.run_until_complete(self.ble_conn.scan_tags(timeout))
        print(devices)
        self.__devices_to_sensors(devices)
        print(self.sensors)
        print(self.get_sensor_by_mac("C1:FC:9B:69:04:8B"))
    
    def get_sensor_by_mac(self, mac: str = None) -> Sensor:
        """Get a sensor object by a known mac adress.

        :param mac: mac adress from a BLE device, defaults to None
        :type mac: str, optional
        :return: Returns a sensor object.
        :rtype: sensor.sensor
        """
        # TODO: REFACTOR - this is slower than needed
        if mac is not None:
            for sensor in self.sensors:
                if sensor.address == mac:
                    return sensor
        return None

    def get_sensor_by_name(self, name: str = None) -> Sensor:
        """Get a sensor object by a known mac adress.

        :param mac: mac adress from a BLE device, defaults to None
        :type mac: str, optional
        :return: Returns a sensor object.
        :rtype: sensor.sensor
        """
        # TODO: REFACTOR - this is slower than needed
        if name is not None:
            for sensor in self.sensors:
                if sensor.name == name:
                    return sensor
        return None

    def __devices_to_sensors(self, devices: list[BLEDevice]) -> list[Sensor]:
        self.sensors = [Sensor.from_device(dev) for dev in devices]
        return self.sensors