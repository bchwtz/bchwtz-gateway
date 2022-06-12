from unittest.mock import create_autospec
import unittest
import sys
import os

CURRENT_DIR_PATH = os.path.dirname(__file__)
ROOT_DIR_PATH = os.path.join(CURRENT_DIR_PATH, "..", "..")
if not ROOT_DIR_PATH in sys.path:
    sys.path.append(ROOT_DIR_PATH)

from bleak import BleakClient 
from gateway import hub

class SensorWorkflowTests(unittest.TestCase):
    """
    Workflow tests for Sensors. This tests expect a sensor with up to date firmware within range.
    """
    def setUp(self):
        """"
        Set up tests. Here we try to find at least one sensor.
        """
        myhub = hub.Hub()
        myhub.discover()

        self.sensor = myhub.sensorlist[0]

    def tearDown(self):
        print("Tear down")
    
    def testSetHeartbeat(self):
        def callback_mock(_, client: BleakClient, sender: int, value: bytearray):
            print(value)
            pass 
        
        callback_mock_function = create_autospec(callback_mock, return_value='fishy')
        self.sensor.handle_ble_callback = callback_mock_function

        self.sensor.get_heartbeat()
        
        callback_mock_function.assert_called_once()
        
        print("finish")


if __name__ == '__main__':
    unittest.main()