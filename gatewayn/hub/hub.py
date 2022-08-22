import asyncio
import logging
import time
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
        self.logger = logging.getLogger("Hub")
        self.logger.setLevel(logging.DEBUG)

    def discover_tags(self, timeout: float = 5.0, rediscover: bool = False) -> None:
        devices = self.main_loop.run_until_complete(self.ble_conn.scan_tags(Config.GlobalConfig.bluetooth_manufacturer_id.value, timeout))
        if not rediscover:
            self.__check_tags_online_state(devices)
            if not self.__has_new_devices(devices):
                self.logger.debug("found no new devices")
                return
            devices = filter(lambda dev: not any(dev.address == t.address for t in self.tags), devices)
        self.logger.debug("found new devices")
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

    def __has_new_devices(self, devices: list[BLEDevice]) -> bool:
        for device in devices:
            if not any(t.address == device.address for t in self.tags):
                return True
        return False

    def __check_tags_online_state(self, devices: list[BLEDevice]) -> None:
        for tag in self.tags:
            self.logger.debug(tag.__dict__)
            if not any(tag.address == dev.address for dev in devices):
                tag.online = False
                self.logger.debug(f"setting tag offline: {tag.address}")
            else:
                tag.online = True
                tag.last_seen = time.time()
                self.logger.debug(f"setting tag online: {tag.address}")