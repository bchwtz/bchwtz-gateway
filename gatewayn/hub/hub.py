import asyncio
from gatewayn.sensor.sensor import Sensor
from gatewayn.drivers.bluetooth.bleconn import BLEConn

class Hub():
    def __init__(self):
        self.main_loop = asyncio.get_event_loop()
        self.sensors: list[Sensor] = []
        self.ble_conn = BLEConn()

    def discover_sensors(self, timeout = 5.0):
        self.sensors = []
        taskobj = self.main_loop.create_task(self.ble_conn.find_tags(timeout))
    
    def get_sensor_by_mac(self, mac = None) -> Sensor:
        """Get a sensor object by a known mac adress.

        :param mac: mac adress from a BLE device, defaults to None
        :type mac: str, optional
        :return: Returns a sensor object.
        :rtype: sensor.sensor
        """
        # TODO: REFACTOR - this is slower than needed
        if mac is not None:
            for sensor in self.sensors:
                if sensor.mac == mac:
                    return sensor
        return None