"""This modul focuses on testing the tag in general."""
import struct
from unittest.mock import AsyncMock
from gateway.drivers.bluetooth.ble_conn.ble_conn import BLEConn
from bleak.backends.device import BLEDevice
from gateway.tag.tag_builder import TagBuilder
from datetime import datetime, date

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

class TestTag:
        """Class for testing the tag functionality. 
        Each test instantiates its own tag. The reason is, that if the tag would be
        created a class level all tests would share the same tag instance, which could screw
        with the tests itself.
        """

        def test_time_on_tag_rmxcd_one(self):
                """Tests that the time on the tag is set correctly.
                The tag supports two commands for setting its system time. Each command gets tested separately.
                The only difference being the rxcmd"""
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
                """Tests that the time on the tag is set correctly.
                The tag supports two commands for setting its system time. Each command gets tested separately.
                The only difference being the rxcmd"""
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
                """Asserts, that if the wrong command is used the times does not get set."""
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
                """Asserts, that if the wrong command is used the times does not get set.
                Again each separate command is tested."""
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

        def test_tag_online(self):
                """Per Default the tag should be listed as online."""
                conn = BLEConn()
                conn.run_single_ble_command = AsyncMock(return_value = None)
                # creating new BLEDevice
                ble_device = BLEDevice(
                address='CF:43:43:33:71:A1',
                name='TestDevice')

                test_tag = TagBuilder().from_device(ble_device).build()
                test_tag.ble_conn = conn
                assert test_tag.online == True