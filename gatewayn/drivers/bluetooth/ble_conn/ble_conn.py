import binascii
from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice
import asyncio
import logging
from termcolor import colored
from typing import Callable
from binascii import hexlify
class BLEConn():
    def __init__(self) -> None:
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger("BLEConn")
        self.logger.setLevel(logging.INFO)

    async def scan_tags(self, timeout = 5.0) -> list[BLEDevice]:
        """The function searches for bluetooth devices nearby and passes the
        MAC addresses to the __validate_mac function.

        :param timeout: timeout for the find_tags function, defaults to 5.0
        :type timeout: float, optional
        """
        sensorlist = []
        devices = await BleakScanner.discover(timeout=timeout)
        sensorlist = self.__validate_mac(devices)
        return sensorlist

    async def run_single_ble_command(self, tag: BLEDevice, read_chan: str, write_chan: str, cmd: str = "", timeout = 5.0, cb: Callable[[int, bytearray], None] = None, retries = 0, max_retries = 5):
        """ Connects to a given tag and starts notification of the given callback
        :param tag: communication device abstraction
        :type tag: Tag
        :param : timeout
        :type timeout: float
        :param cb: Callback that will be executed when a notification is received
        :type cb: Callable[[int, bytearray]
        """
        try:
            async with BleakClient(tag) as client:
                await client.start_notify(char_specifier = read_chan, callback = cb)
                await client.write_gatt_char(write_chan, bytearray.fromhex(cmd), True)
        except:
            if retries < max_retries:
                self.logger.info("retrying...")
                await self.run_single_ble_command(tag, read_chan, write_chan, cmd, timeout, cb, retries+1, max_retries)
            return

    def __validate_mac(self, devices: list[BLEDevice]) -> list[BLEDevice]:
        """ This funcion updates the internal mac_list. If a MAC address passed the
        checked_mac_address process, it will extend the list 'mac'.
        :param devices: device passed by the BleakScanner function
        :type devices: bleak.backends.device.BLEDevice

        TODO: check for vendor name or some other idempotent information
        """
        sensorlist = []
        for i in devices:
            self.logger.warn(i.metadata)
            self.logger.info('Device: %s with Address %s found!' % (i.name, i.address))
            if ("Ruuvi" in i.name):
                self.logger.info(colored('Device: %s with Address %s saved in MAC list!' % (i.name, i.address), "green", attrs=['bold']) )
                sensorlist.append(i)
        return sensorlist
