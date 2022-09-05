import struct
from unittest.mock import AsyncMock
from gatewayn.drivers.bluetooth.ble_conn.ble_conn import BLEConn
from bleak.backends.device import BLEDevice
from gatewayn.tag.tag_builder import TagBuilder
from datetime import datetime, date


class TestTag:

        def test_time_on_tag_rmxcd_one(self):
                conn = BLEConn()
                conn.run_single_ble_command = AsyncMock(return_value = None)
                # creating new BLEDevice
                ble_device = BLEDevice(
                address='CF:43:43:33:71:A1',
                name='TestDevice')

                test_tag = TagBuilder().from_device(ble_device).build()
                test_tag.ble_conn = conn            

                time_for_tag = datetime.now().timestamp()
                current_date_time = str(date.today().strftime("%m/%d/%y")) + " " + str(datetime.now().strftime("%H:%M:%S"))


                now = struct.pack("<Q", int(time_for_tag * 1000)).hex()
                # Constructing time cmd
                rxcmd = '210009' + now
                test_tag.multi_communication_callback(0, bytes.fromhex(rxcmd))     
                assert test_tag.time == current_date_time
        
        def test_time_on_tag_rmxcd_two(self):
                conn = BLEConn()
                conn.run_single_ble_command = AsyncMock(return_value = None)
                # creating new BLEDevice
                ble_device = BLEDevice(
                address='CF:43:43:33:71:A1',
                name='TestDevice')

                test_tag = TagBuilder().from_device(ble_device).build()
                test_tag.ble_conn = conn
                time_for_tag = datetime.now().timestamp()
                current_date_time = str(date.today().strftime("%m/%d/%y")) + " " + str(datetime.now().strftime("%H:%M:%S"))     
                now = struct.pack("<Q", int(time_for_tag * 1000)).hex()
                # Constructing time cmd
                rxcmd = '4A0009' + now
                test_tag.multi_communication_callback(0, bytes.fromhex(rxcmd))     
                assert test_tag.time == current_date_time

        def test_time_on_tag_rmxcd_wrong(self):
                conn = BLEConn()
                conn.run_single_ble_command = AsyncMock(return_value = None)
                # creating new BLEDevice
                ble_device = BLEDevice(
                address='CF:43:43:33:71:A1',
                name='TestDevice')

                test_tag = TagBuilder().from_device(ble_device).build()
                test_tag.ble_conn = conn
                time_for_tag = datetime.now().timestamp()
                current_date_time = str(date.today().strftime("%m/%d/%y")) + " " + str(datetime.now().strftime("%H:%M:%S"))


                now = struct.pack("<Q", int(time_for_tag * 1000)).hex()
                # Constructing time cmd
                rxcmd = '4BBB09' + now
                test_tag.multi_communication_callback(0, bytes.fromhex(rxcmd))

                assert test_tag.time != current_date_time
        
        def test_time_on_tag_rmxcd_wrong_none(self):
                conn = BLEConn()
                conn.run_single_ble_command = AsyncMock(return_value = None)
                # creating new BLEDevice
                ble_device = BLEDevice(
                address='CF:43:43:33:71:A1',
                name='TestDevice')

                test_tag = TagBuilder().from_device(ble_device).build()
                test_tag.ble_conn = conn
                time_for_tag = datetime.now().timestamp()

                now = struct.pack("<Q", int(time_for_tag * 1000)).hex()
                # Constructing time cmd
                rxcmd = '4BBB09' + now
                test_tag.multi_communication_callback(0, bytes.fromhex(rxcmd))

                assert test_tag.time == None
