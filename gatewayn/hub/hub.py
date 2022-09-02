import asyncio
import logging
import time
from gatewayn.tag.tag import Tag
from gatewayn.tag.tag_builder import TagBuilder
from gatewayn.drivers.bluetooth.ble_conn.ble_conn import BLEConn
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from gatewayn.config import Config

class Hub():
    def __init__(self):
        self.tags: list[Tag] = []
        self.ble_conn = BLEConn()
        self.logger = logging.getLogger("Hub")
        self.logger.setLevel(logging.DEBUG)

    async def discover_tags(self, timeout: float = 5.0, rediscover: bool = False, autoload_config: bool = True) -> None:
        devices = await self.ble_conn.scan_tags(Config.GlobalConfig.bluetooth_manufacturer_id.value, timeout)
        if not rediscover:
            self.__check_tags_online_state(devices)
            if not self.__has_new_devices(devices):
                self.logger.debug("found no new devices")
                return
            devices = filter(lambda dev: not any(dev.address == t.address for t in self.tags), devices)
        self.logger.debug("found new devices")
        self.__devices_to_tags(devices)
        if autoload_config:
            for dev in devices:
                tag = self.get_tag_by_address(dev.address)
                tag.get_config()
    
    async def listen_for_advertisements(self, timeout: float = 50) -> None:
        await self.ble_conn.listen_advertisements(timeout, self.cb_advertisements)
    
    async def cb_advertisements(self, device: BLEDevice, data: AdvertisementData):
        devices = self.ble_conn.validate_manufacturer([device], Config.GlobalConfig.bluetooth_manufacturer_id.value)
        if len(devices) <= 0:
            return
        # print(data)
        device = devices[0]
        tag = self.get_tag_by_address(devices[0].address)
        if tag is None:
            tag = Tag(device.name, device.address, device, True)
            self.tags.append(tag)
            await tag.get_config()
            self.logger.info(f"setting up new device with address {tag.address}")
            return
        if tag.config is None or tag.config.samplerate == 0:
            self.logger.warn("tag config was not loaded yet!")
            return
        dt = tag.dec.decode_ruuvi_advertisement(data.manufacturer_data.get(Config.GlobalConfig.bluetooth_manufacturer_id.value), tag.config.samplerate, tag.config.scale, None)
        print(f"dt = {dt}")

    def get_tag_by_address(self, address: str = None) -> Tag:
        """Get a tag object by a known mac adress.
        :param address: mac adress from a BLE device, defaults to None
        :type mac: str, optional
        :return: Returns a tag object.
        :rtype: tag.tag
        """
        # TODO: REFACTOR - this is slower than needed
        if address is not None:
            for tag in self.tags:
                if tag.address == address:
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