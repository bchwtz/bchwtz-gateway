import asyncio
from gatewayn.sensor import Sensor
from gatewayn.drivers.bluetooth.bleconn import BLEConn

class Hub():
    def __init__(self):
        self.main_loop = asyncio.get_event_loop()
        self.sensors: list[Sensor] = []
        self.ble_conn = BLEConn()

    def discover_sensors(self, timeout = 5.0):
        self.sensors = []
        taskobj = self.main_loop.create_task(self.ble_conn.find_tags(timeout))