import struct
from unittest.mock import AsyncMock
from gatewayn.drivers.bluetooth.ble_conn.ble_conn import BLEConn
from bleak.backends.device import BLEDevice
from gatewayn.tag.tag_builder import TagBuilder
from datetime import datetime, date
import asyncio
import time

def test_time_on_tag_built_in():
        conn = BLEConn()
        conn.run_single_ble_command = AsyncMock(return_value = None)
        # creating new BLEDevice
        ble_device = BLEDevice(
        address='6C:5D:7F:8G:9H',
        name='TestDevice')

        test_tag = TagBuilder().from_device(ble_device).build()
        test_tag.ble_conn = conn
        current_date_time = str(date.today().strftime("%m/%d/%y")) + " " + str(datetime.now().strftime("%H:%M:%S"))
        print(test_tag.online)


        # asyncio.run(test_tag.set_time_to_now())
        # # test_tag.set_time_to_now()
        # time.sleep(2)
        # print(current_date_time)
        # print(f'test_tag.time: {test_tag.time}')
        # if test_tag.time == current_date_time:
        #     print("success")

if __name__ == "__main__":
    test_time_on_tag_built_in()