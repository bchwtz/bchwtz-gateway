import asyncio
from datetime import datetime
from typing import Callable
import time
from typing_extensions import Self
from xmlrpc.client import DateTime
from bleak.backends.device import BLEDevice
from gatewayn.tag.tag_interface.encoder import Encoder
from gatewayn.tag.tagconfig import TagConfig
from nbformat import write
from numpy import byte
from gatewayn.drivers.bluetooth.ble_conn.ble_conn import BLEConn
from gatewayn.config import Config
import logging
from gatewayn.tag.tag_interface.decoder import Decoder

from gatewayn.sensor.sensor import Sensor
from gatewayn.tag.tag_interface.signals import SigScanner



class Tag():
    def __init__(self, name: str = "", address: str = "", device: BLEDevice = None) -> None:
        self.name: str = name
        self.address: str = address
        self.ble_device: BLEDevice = device
        self.main_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        self.ble_conn: BLEConn = BLEConn()
        self.logger = logging.getLogger("Tag")
        self.logger.setLevel(logging.INFO)
        self.samplerate: int = 0
        # TODO: add sensors as ble caps on firmware side to autoload sensor classes by names
        self.sensors: list[Sensor] = []
        self.dec: Decoder = Decoder()
        self.enc: Encoder = Encoder()
        self.config: TagConfig = None
        self.time: DateTime = None

    def get_acceleration_log(self, cb: Callable[[int, bytearray], None] = None) -> None:
        if cb is None:
            cb = self.default_log_callback
        self.main_loop.run_until_complete(self.ble_conn.run_single_ble_command(
            tag = self.ble_device,
            read_chan = Config.CommunicationChannels.rx.value,
            write_chan = Config.CommunicationChannels.tx.value,
            cmd = Config.Commands.get_acceleration_data.value,
            cb = cb
        ))

    def get_config(self, cb: Callable[[int, bytearray], None] = None) -> None:
        if cb is None:
            cb = self.multi_communication_callback
        self.main_loop.run_until_complete(self.ble_conn.run_single_ble_command(
            tag = self.ble_device,
            read_chan = Config.CommunicationChannels.rx.value,
            write_chan = Config.CommunicationChannels.tx.value,
            cmd = Config.Commands.get_tag_config.value,
            cb = cb
        ))

    def get_time(self, cb: Callable[[int, bytearray], None] = None) -> None:
        if cb is None:
            cb = self.multi_communication_callback
        self.main_loop.run_until_complete(self.ble_conn.run_single_ble_command(
            tag = self.ble_device,
            read_chan = Config.CommunicationChannels.rx.value,
            write_chan = Config.CommunicationChannels.tx.value,
            cmd = Config.Commands.get_tag_timestamp.value,
            cb = cb
        ))

    def get_flash_statistics(self, cb: Callable[[int, bytearray], None] = None) -> None:
        if cb is None:
            cb = self.default_log_callback
        self.main_loop.run_until_complete(self.ble_conn.run_single_ble_command(
            tag = self.ble_device,
            read_chan = Config.CommunicationChannels.rx.value,
            write_chan = Config.CommunicationChannels.tx.value,
            cmd = Config.Commands.get_flash_statistics.value,
            cb = cb
        ))

    def get_logging_status(self, cb: Callable[[int, bytearray], None] = None) -> None:
        if cb is None:
            cb = self.default_log_callback
        self.main_loop.run_until_complete(self.ble_conn.run_single_ble_command(
            tag = self.ble_device,
            read_chan = Config.CommunicationChannels.rx.value,
            write_chan = Config.CommunicationChannels.tx.value,
            cmd = Config.Commands.get_logging_status.value,
            cb = cb
        ))

    async def default_log_callback(self, status_code: int, rx_bt: bytearray) -> None:
        res = self.dec.decode_ruuvi_msg(rx_bt)
        self.logger.info(f"status {status_code}")
        self.logger.info(f"msg: {res}")

    async def multi_communication_callback(self, status_code: int, rx_bt: bytearray) -> None:
        caught_signals = None
        caught_signals = SigScanner.scan_signals(rx_bt, Config.ReturnSignals)
        print(caught_signals)
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

    def set_time_to_now(self, cb: Callable[[int, bytearray], None] = None) -> None:
        if cb is None:
            cb = self.multi_communication_callback
        cmd = self.enc.encode_time(time = datetime.now().timestamp())
        print(cmd)
        self.main_loop.run_until_complete(self.ble_conn.run_single_ble_command(
            tag = self.ble_device,
            read_chan = Config.CommunicationChannels.rx.value,
            write_chan = Config.CommunicationChannels.tx.value,
            cmd = cmd,
            cb = cb
        ))

    # TODO : move to enc
    def set_heartbeat(self, heartbeat_interval: int = 10):
        self.logger.info("Set heartbeat interval to: {}".format(heartbeat_interval))
        hex_beat = hex(heartbeat_interval)[2:]
        hex_msg = f"2200F2{'0000'[:4 - len(hex_beat)]}{hex_beat}000000000000"

    def set_config(self, config: TagConfig = None):
        if config is not None:
            self.config = config
        cmd = self.enc.encode_config(config = self.config)
        self.main_loop.run_until_complete(self.ble_conn.run_single_ble_command(
            tag = self.ble_device,
            read_chan = Config.CommunicationChannels.rx.value,
            write_chan = Config.CommunicationChannels.tx.value,
            cmd = cmd,
            cb = self.multi_communication_callback
        ))
