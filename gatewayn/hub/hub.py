import asyncio
from gatewayn.tag.tag import Tag
from gatewayn.tag.tag_builder import TagBuilder
from gatewayn.drivers.bluetooth.ble_conn.ble_conn import BLEConn
from bleak.backends.device import BLEDevice
from gatewayn.config import Config

class Hub():
    def __init__(self):
        self.main_loop = asyncio.get_event_loop()
        self.tags: list[Tag] = []
        self.ble_conn = BLEConn()

    def discover_tags(self, timeout: float = 5.0) -> None:
        self.tags = []
        devices = self.main_loop.run_until_complete(self.ble_conn.scan_tags(Config.GlobalConfig.bluetooth_manufacturer_id.value, timeout))
        self.__devices_to_tags(devices)
    
    def get_tag_by_mac(self, mac: str = None) -> Tag:
        """Get a tag object by a known mac adress.
        :param mac: mac adress from a BLE device, defaults to None
        :type mac: str, optional
        :return: Returns a tag object.
        :rtype: tag.tag
        """
        # TODO: REFACTOR - this is slower than needed
        if mac is not None:
            for tag in self.tags:
                if tag.address == mac:
                    return tag
        return None

    def get_tag_by_name(self, name: str = None) -> Tag:
        """Get a tag object by a known mac adress.
        :param mac: mac adress from a BLE device, defaults to None
        :type mac: str, optional
        :return: Returns a tag object.
        :rtype: tag.tag
        """
        # TODO: REFACTOR - this is slower than needed
        if name is not None:
            for tag in self.tags:
                if tag.name == name:
                    return tag
        return None

    def __devices_to_tags(self, devices: list[BLEDevice]) -> list[Tag]:
        self.tags = [TagBuilder().from_device(dev).build() for dev in devices]
        return self.tags