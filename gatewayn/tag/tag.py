import asyncio
from typing import Callable
from typing_extensions import Self
from bleak.backends.device import BLEDevice
from nbformat import write
from numpy import byte
from gatewayn.drivers.bluetooth.ble_conn.ble_conn import BLEConn
from gatewayn.config import Config
import logging

class Tag():
    def __init__(self, name: str = "", address: str = "", device: BLEDevice = None) -> None:
        self.name: str = name
        self.address: str = address
        self.bleDevice: BLEDevice = device
        self.main_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        self.bleConn: BLEConn = BLEConn()
        self.communication_config = Config()
        self.logger = logging.getLogger("Tag")
        self.logger.setLevel(logging.INFO)

    def get_acceleration_log(self, cb: Callable[[int, bytearray], None] = None) -> None:
        if cb is None:
            cb = self.default_log_callback
        self.main_loop.run_until_complete(self.bleConn.run_single_ble_command(
            self.bleDevice,
            read_chan = self.communication_config.channels.rx,
            write_chan = self.communication_config.channels.tx,
            cmd = self.communication_config.commands.get_acceleration_data,
            cb = cb
        ))

    def get_flash_statistics(self, cb: Callable[[int, bytearray], None] = None) -> None:
        if cb is None:
            cb = self.default_log_callback
        self.main_loop.run_until_complete(self.bleConn.run_single_ble_command(
            self.bleDevice,
            read_chan = self.communication_config.channels.rx,
            write_chan = self.communication_config.channels.tx,
            cmd = self.communication_config.commands.get_flash_statistics,
            cb = cb
        ))

    def get_logging_status(self, cb: Callable[[int, bytearray], None] = None) -> None:
        if cb is None:
            cb = self.default_log_callback
        self.main_loop.run_until_complete(self.bleConn.run_single_ble_command(
            self.bleDevice,
            read_chan = self.communication_config.channels.rx,
            write_chan = self.communication_config.channels.tx,
            cmd = self.communication_config.commands.get_logging_status,
            cb = cb
        ))

    async def default_log_callback(self, status_code: int, rx_bt: bytearray) -> None:
        self.logger.info(f"status {status_code}")
        self.logger.info(f"msg: {rx_bt}")

    async def multi_communication_callback(self, status_code: int, rx_bt: bytearray) -> None:
        pass