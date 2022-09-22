import asyncio
import logging
from threading import Thread
import time
import uuid
from gatewayn.tag.tag import Tag
from gatewayn.tag.tag_builder import TagBuilder
from gatewayn.drivers.bluetooth.ble_conn.ble_conn import BLEConn
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from gatewayn.config import Config
import json
from paho.mqtt.client import Client, MQTTMessage
import aiopubsub

class Hub(object):

    instance = None

    def __init__(self):
        self.tags: list[Tag] = []
        self.ble_conn = BLEConn()
        self.logger = logging.getLogger("Hub")
        self.logger.setLevel(logging.DEBUG)
        self.mqtt_client: Client = None
        self.pubsub_hub: aiopubsub.Hub = aiopubsub.Hub()
        self.main_loop: asyncio.BaseEventLoop = asyncio.get_event_loop()

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
        self.log_mqtt()
    
    async def listen_for_advertisements(self, timeout: float = 50) -> None:
        await self.ble_conn.listen_advertisements(timeout, self.cb_advertisements)
    
    async def cb_advertisements(self, device: BLEDevice, data: AdvertisementData):
        device.metadata = data.__dict__
        devices = self.ble_conn.validate_manufacturer([device], Config.GlobalConfig.bluetooth_manufacturer_id.value)
        if len(devices) <= 0:
            return
        # print(data)
        device = devices[0]
        tag = self.get_tag_by_address(devices[0].address)
        if tag is None:
            tag = Tag(device.name, device.address, device, True, self.pubsub_hub)
            self.tags.append(tag)
            await tag.get_config()
            self.logger.info(f"setting up new device with address {tag.address}")
        # if tag.config is None or tag.config.samplerate == 0:
        #     self.logger.warn("tag config was not loaded yet!")
        #     return
        tag.read_sensor_data(data.manufacturer_data.get(Config.GlobalConfig.bluetooth_manufacturer_id.value))
        tag.last_seen = time.time()
        tag.online = True
        self.log_mqtt()

    def log_mqtt(self):
        if self.mqtt_client is not None:
            self.logger.info("logging to channel %s", Config.MQTTConfig.topic_listen_adv.value)
            self.mqtt_client.publish(Config.MQTTConfig.topic_listen_adv.value, json.dumps(self, default=lambda o: o.get_props() if getattr(o, "get_props", None) is not None else None, skipkeys=True, check_circular=False, sort_keys=True, indent=4))

    async def on_log_event(self, key: aiopubsub.Key, tag: Tag):
        self.logger.info("logging to mqtt")
        self.log_mqtt()

    async def on_command_event(self, key: aiopubsub.Key, cmd: dict):
        self.logger.info("fetching time")
        for t in self.tags:
            await t.get_time()

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
        self.tags = [TagBuilder().from_device(dev, self.pubsub_hub).build() for dev in devices]
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

    def get_props(self):
        return {'tags': self.tags}

    async def subscribe_to_log_events(self):
        self.log_subscriber: aiopubsub.Subscriber = aiopubsub.Subscriber(self.pubsub_hub, "events")
        subscribe_key = aiopubsub.Key('*', 'log', '*')
        self.log_subscriber.add_async_listener(subscribe_key, self.on_log_event)

    def mqtt_on_connect(self, client, userdata, flags, rc):
        self.logger.info("connected to mqtt")
        self.logger.debug("result: %s"%rc)
        sub = Config.MQTTConfig.topic_command.value
        res = self.mqtt_client.subscribe(sub, 0)
        self.logger.info(sub)

    def mqtt_on_command(self, client, userdata, message: MQTTMessage):
        msg_dct: dict = json.loads(message.payload)
        self.logger.info(msg_dct)
        name = msg_dct["name"]
        id = msg_dct["id"]
        payload = msg_dct["payload"]
        # print(self.internal_command_publisher.__dict__)
        if name == "get_time":
            for t in self.tags:
                self.logger.info("running get_time on tag: %s", t.address)
                asyncio.run_coroutine_threadsafe(t.get_time(), self.main_loop)

        elif name == "get_config":
            for t in self.tags:
                self.logger.info("running get_config on tag: %s", t.address)
                asyncio.run_coroutine_threadsafe(t.get_config(), self.main_loop)


        # self.internal_command_publisher.publish(aiopubsub.Key("command"), {"name": name, "payload": payload})
        self.logger.debug("sent payload")
        # self.logger.info(self.tags[0].__dict__)
        # self.tags[0].test_pub()
        res = {"id": str(uuid.uuid4()), "request_id": id, "payload": "success!", "name": name}
        self.mqtt_client.publish(Config.MQTTConfig.topic_command_res.value, json.dumps(res))
        # self.logger.info("sent response to %s" % Config.MQTTConfig.topic_command_res.value)