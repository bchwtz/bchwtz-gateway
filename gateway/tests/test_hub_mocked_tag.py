"""This modul emulates the functions of the hub if a tag is present. """
from bleak.backends.device import BLEDevice
import asyncio
from ..drivers.bluetooth.ble_conn.ble_conn import BLEConn
from gateway.tag.tag import Tag
from gateway.tag.tag_builder import TagBuilder
from gateway.hub.hub import Hub
from unittest.mock import MagicMock

# https://github.com/pytest-dev/pytest-asyncio/issues/212
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

class TestHub():
    """This class is used to test the therotical functionality of the hub.
    For this to work the run_single_ble_command method has to be mocked using MagicMock.
    Also the bluetooth tag has to be mocked using the methods provided by the tag module. The tag is given a 
    made up MAC-adress and a made up name.
    Afterwards, the mocked tag is added to the list of found tags kept by the mocked hub.
    """
    conn = BLEConn()
    conn.run_single_ble_command = MagicMock(return_value = None)
    print(conn.run_single_ble_command())
    ble_device = BLEDevice(
        address='CF:43:43:33:71:A1',
        name='TestDevice')

    test_tag = TagBuilder().from_device(ble_device).build()
    test_hub = Hub()
    test_hub.tags.append(test_tag)
    
    def test_get_tag_by_name_wrong_name(self):
        """Validating that the get_tag_by_name-method is working and returning a Tag."""
        assert isinstance(self.test_hub.get_tag_by_name(name="TestDevice"),Tag)

    def test_get_tag_by_name_wrong_Mac(self):
        """Validating that the get_tag_by_mac-method is working and returning a Tag."""
        assert isinstance(self.test_hub.get_tag_by_mac(mac="CF:43:43:33:71:A1"),Tag)