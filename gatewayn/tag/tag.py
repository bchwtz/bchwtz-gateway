import asyncio
from time import time
from typing import Callable
from typing_extensions import Self
from bleak.backends.device import BLEDevice
from nbformat import write
from numpy import byte
from gatewayn.drivers.bluetooth.ble_conn.ble_conn import BLEConn
from gatewayn.config import Config
import logging
from gatewayn.drivers.tag_interface.decoder import Decoder

from gatewayn.sensor.sensor import Sensor
from gatewayn.drivers.tag_interface.signals import SigScanner



class Tag():
    def __init__(self, name: str = "", address: str = "", device: BLEDevice = None) -> None:
        self.name: str = name
        self.address: str = address
        self.ble_device: BLEDevice = device
        self.main_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        self.ble_conn: BLEConn = BLEConn()
        self.logger = logging.getLogger("Tag")
        self.logger.setLevel(logging.INFO)
        self.samplerate = 0
        # TODO: add sensors as ble caps on firmware side to autoload sensor classes by names
        self.sensors: list[Sensor] = []
        self.dec = Decoder()
        self.time = None

    def get_acceleration_log(self, cb: Callable[[int, bytearray], None] = None) -> None:
        if cb is None:
            cb = self.default_log_callback
        self.main_loop.run_until_complete(self.ble_conn.run_single_ble_command(
            self.ble_device,
            read_chan = Config.CommunicationChannels.rx.value,
            write_chan = Config.CommunicationChannels.tx.value,
            cmd = Config.Commands.get_acceleration_data.value,
            cb = cb
        ))

    def get_config(self, cb: Callable[[int, bytearray], None] = None) -> None:
        if cb is None:
            cb = self.multi_communication_callback
        self.main_loop.run_until_complete(self.ble_conn.run_single_ble_command(
            self.ble_device,
            read_chan = Config.CommunicationChannels.rx.value,
            write_chan = Config.CommunicationChannels.tx.value,
            cmd = Config.Commands.get_tag_config.value,
            cb = cb
        ))

    def get_time(self, cb: Callable[[int, bytearray], None] = None) -> None:
        if cb is None:
            cb = self.multi_communication_callback
        self.main_loop.run_until_complete(self.ble_conn.run_single_ble_command(
            self.ble_device,
            read_chan = Config.CommunicationChannels.rx.value,
            write_chan = Config.CommunicationChannels.tx.value,
            cmd = Config.Commands.get_tag_timestamp.value,
            cb = cb
        ))

    def get_flash_statistics(self, cb: Callable[[int, bytearray], None] = None) -> None:
        if cb is None:
            cb = self.default_log_callback
        self.main_loop.run_until_complete(self.ble_conn.run_single_ble_command(
            self.ble_device,
            read_chan = Config.CommunicationChannels.rx.value,
            write_chan = Config.CommunicationChannels.tx.value,
            cmd = Config.Commands.get_flash_statistics.value,
            cb = cb
        ))

    def get_logging_status(self, cb: Callable[[int, bytearray], None] = None) -> None:
        if cb is None:
            cb = self.default_log_callback
        self.main_loop.run_until_complete(self.ble_conn.run_single_ble_command(
            self.ble_device,
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
        if "samplerate" in caught_signals:
            self.handle_samplerate_cb(rx_bt)
        elif "time" in caught_signals:
            self.handle_time_cb(rx_bt)

    def handle_samplerate_cb(self, rx_bt: bytearray) -> None:
        samplerate = self.dec.decode_samplerate_rx(rx_bt)
        self.samplerate = samplerate
    
    def handle_time_cb(self, rx_bt: bytearray) -> None:
        time = self.dec.decode_time_rx(rx_bt)
        self.time = time