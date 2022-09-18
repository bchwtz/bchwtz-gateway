import asyncio
from datetime import datetime
from typing import Callable
import time
from typing_extensions import Self
from xmlrpc.client import DateTime
from bleak.backends.device import BLEDevice
from gatewayn.sensor.acceleration import AccelerationSensor
from gatewayn.sensor.barometer import BarometerSensor
from gatewayn.sensor.temperature import TemperatureSensor
from gatewayn.sensor.humidity import HumiditySensor
from gatewayn.sensor.battery import BatterySensor
from gatewayn.tag.tag_interface.encoder import Encoder
from gatewayn.tag.tagconfig import TagConfig
from nbformat import write
from numpy import byte
from gatewayn.drivers.bluetooth.ble_conn.ble_conn import BLEConn
from gatewayn.config import Config
import logging
from gatewayn.tag.tag_interface.decoder import Decoder
from bleak.backends.scanner import AdvertisementData

from gatewayn.sensor.sensor import Sensor
from gatewayn.tag.tag_interface.signals import SigScanner
import mongox


client = mongox.Client("mongodb://localhost:27017", get_event_loop=asyncio.get_running_loop)
db = client.get_database("gateway")
class Tag(object):
    def __init__(self, name: str = "", address: str = "", device: BLEDevice = None, online: bool = True) -> None:
        self.name: str = name
        self.address: str = address
        self.ble_device: BLEDevice = device
        self.ble_conn: BLEConn = BLEConn()
        self.logger = logging.getLogger("Tag")
        self.logger.setLevel(logging.INFO)
        # TODO: add sensors as ble caps on firmware side to autoload sensor classes by names
        self.sensors: list[Sensor] = [
            AccelerationSensor(),
            BarometerSensor(),
            TemperatureSensor(),
            HumiditySensor(),
            BatterySensor(),
        ]
        self.dec: Decoder = Decoder()
        self.enc: Encoder = Encoder()
        self.config: TagConfig = None
        self.time: DateTime = None
        self.online: bool = online
        self.last_seen: float = time.time()

    async def get_acceleration_log(self, cb: Callable[[int, bytearray], None] = None) -> None:
        if cb is None:
            cb = self.default_log_callback
        await self.ble_conn.run_single_ble_command(
            tag = self.ble_device,
            read_chan = Config.CommunicationChannels.rx.value,
            write_chan = Config.CommunicationChannels.tx.value,
            cmd = Config.Commands.get_acceleration_data.value,
            cb = cb
        )

    async def get_config(self, cb: Callable[[int, bytearray], None] = None) -> None:
        if cb is None:
            cb = self.multi_communication_callback
        await self.ble_conn.run_single_ble_command(
            tag = self.ble_device,
            read_chan = Config.CommunicationChannels.rx.value,
            write_chan = Config.CommunicationChannels.tx.value,
            cmd = Config.Commands.get_tag_config.value,
            cb = cb
        )

    async def get_time(self, cb: Callable[[int, bytearray], None] = None) -> None:
        if cb is None:
            cb = self.multi_communication_callback
        await self.ble_conn.run_single_ble_command(
            tag = self.ble_device,
            read_chan = Config.CommunicationChannels.rx.value,
            write_chan = Config.CommunicationChannels.tx.value,
            cmd = Config.Commands.get_tag_timestamp.value,
            cb = cb
        )

    async def get_flash_statistics(self, cb: Callable[[int, bytearray], None] = None) -> None:
        if cb is None:
            cb = self.default_log_callback
        await self.ble_conn.run_single_ble_command(
            tag = self.ble_device,
            read_chan = Config.CommunicationChannels.rx.value,
            write_chan = Config.CommunicationChannels.tx.value,
            cmd = Config.Commands.get_flash_statistics.value,
            cb = cb
        )

    async def get_logging_status(self, cb: Callable[[int, bytearray], None] = None) -> None:
        if cb is None:
            cb = self.default_log_callback
        await self.ble_conn.run_single_ble_command(
            tag = self.ble_device,
            read_chan = Config.CommunicationChannels.rx.value,
            write_chan = Config.CommunicationChannels.tx.value,
            cmd = Config.Commands.get_logging_status.value,
            cb = cb
        )

    def default_log_callback(self, status_code: int, rx_bt: bytearray) -> None:
        res = self.dec.decode_ruuvi_msg(rx_bt)
        self.logger.info(f"status {status_code}")
        self.logger.info(f"msg: {res}")

    def multi_communication_callback(self, status_code: int, rx_bt: bytearray) -> None:
        caught_signals = None
        caught_signals = SigScanner.scan_signals(rx_bt, Config.ReturnSignals)
        self.logger.debug(caught_signals)
        if caught_signals == None:
            return
        if "config" in caught_signals:
            self.handle_config_cb(rx_bt)
        elif "time" in caught_signals:
            self.handle_time_cb(rx_bt)

    def handle_config_cb(self, rx_bt: bytearray) -> None:
        self.config = self.dec.decode_config_rx(rx_bt)
    
    def handle_time_cb(self, rx_bt: bytearray) -> None:
        time = self.dec.decode_time_rx(rx_bt)
        self.time = time

    async def set_time_to_now(self, cb: Callable[[int, bytearray], None] = None) -> None:
        if cb is None:
            cb = self.multi_communication_callback
        cmd = self.enc.encode_time(time = datetime.now().timestamp())
        self.logger.debug(cmd)
        await self.ble_conn.run_single_ble_command(
            tag = self.ble_device,
            read_chan = Config.CommunicationChannels.rx.value,
            write_chan = Config.CommunicationChannels.tx.value,
            cmd = cmd,
            cb = cb
        )

    # TODO : move to enc
    def set_heartbeat(self, heartbeat_interval: int = 10):
        self.logger.debug("Set heartbeat interval to: {}".format(heartbeat_interval))
        hex_beat = hex(heartbeat_interval)[2:]
        hex_msg = f"2200F2{'0000'[:4 - len(hex_beat)]}{hex_beat}000000000000"

    async def set_config(self, config: TagConfig = None):
        if config is not None:
            self.config = config
        cmd = self.enc.encode_config(config = self.config)
        await self.ble_conn.run_single_ble_command(
            tag = self.ble_device,
            read_chan = Config.CommunicationChannels.rx.value,
            write_chan = Config.CommunicationChannels.tx.value,
            cmd = cmd,
            cb = self.multi_communication_callback
        )

    def read_sensor_data(self, data: AdvertisementData = None):
        if data is None:
            return
        tag_data = self.dec.decode_advertisement(data)
        self.logger.info(tag_data)
        for sensor in self.sensors:
            sensor.read_data_from_advertisement(tag_data)

    def get_props(self):
        return {'name': self.name, 'address': self.address, 'sensors': self.sensors, 'time': self.time, 'config': self.config, 'online': self.online, 'last_seen': self.last_seen}