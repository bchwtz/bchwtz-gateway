from bleak.backends.device import BLEDevice
import asyncio
from ..drivers.bluetooth.ble_conn.ble_conn import BLEConn
from gatewayn.tag.tag import Tag
from gatewayn.tag.tag_builder import TagBuilder
from gatewayn.hub.hub import Hub
from unittest.mock import MagicMock

# https://github.com/pytest-dev/pytest-asyncio/issues/212
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

class TestHub():
    conn = BLEConn()
    conn.run_single_ble_command = MagicMock(return_value = None)
    print(conn.run_single_ble_command())
    ble_device = BLEDevice(
        address='6C:5D:7F:8G:9H',
        name='TestDevice')

    test_tag = TagBuilder().from_device(ble_device).build()
    test_hub = Hub()
    test_hub.tags.append(test_tag)
    
    def test_get_tag_by_name_wrong_Mac(self):
        assert isinstance(self.test_hub.get_tag_by_mac(mac="6C:5D:7F:8G:9H"),Tag)
    
    def test_get_tag_by_name_wrong_name(self):
        assert isinstance(self.test_hub.get_tag_by_name(name="TestDevice"),Tag)
