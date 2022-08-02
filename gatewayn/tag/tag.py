import asyncio
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



class Tag():
    def __init__(self, name: str = "", address: str = "", device: BLEDevice = None) -> None:
        self.name: str = name
        self.address: str = address
        self.ble_device: BLEDevice = device
        self.main_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        self.ble_conn: BLEConn = BLEConn()
        self.logger = logging.getLogger("Tag")
        self.logger.setLevel(logging.INFO)
        # TODO: add sensors as ble caps on firmware side to autoload sensor classes by names
        self.sensors: list[Sensor] = []

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
            cb = self.default_log_callback
        self.main_loop.run_until_complete(self.ble_conn.run_single_ble_command(
            self.ble_device,
            read_chan = Config.CommunicationChannels.rx.value,
            write_chan = Config.CommunicationChannels.tx.value,
            cmd = Config.Commands.get_tag_config,
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

    async def default_log_callback(self, status_code: int, rx_bt: bytes) -> None:
        dec = Decoder()
        res = dec.decode_ruuvi_msg(rx_bt)
        self.logger.info(f"status {status_code}")
        self.logger.info(f"msg: {res}")

    async def multi_communication_callback(self, status_code: int, rx_bt: bytearray) -> None:
        pass