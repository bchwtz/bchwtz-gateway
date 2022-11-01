import binascii
from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice
import asyncio
import logging
from termcolor import colored
from typing import Callable
from binascii import hexlify
import time

class BLEConn():
    """ Wraps bleak to be easily accessible for the gateway's usecase and to be able to use custom logging.
    """
    def __init__(self) -> None:
        """ creates a new instance of BLEConn.
        """
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger: logging.Logger = logging.getLogger("BLEConn")
        self.logger.setLevel(logging.WARNING)
        self.stopEvent: asyncio.Event = asyncio.Event()
        self.stopEvent.clear()

    # cof - bleak adscanning seems broken - have to investigate further later... muuuuuch later...
    async def listen_advertisements(self, timeout: float = 5.0, cb: Callable[[BLEDevice, dict], None] = None) -> None:
        """ Starts listening for advertisements.
            Arguments:
                timeout: specifies how long the listening should be running
                cb: Callback that is called on every advertisement that is discovered
        """
        scanner = BleakScanner()
        scanner.register_detection_callback(cb)
        await scanner.start()
        await asyncio.sleep(timeout)
        await scanner.stop()

    async def scan_tags(self, manufacturer_id: int = 0, timeout: float = 20.0) -> list[BLEDevice]:
        """The function searches for bluetooth devices nearby and passes the
            MAC addresses to the validate_manufacturer function.
            Arguments:
                timeout: timeout for the find_tags function
            Returns:
                A list of BLEDevice that can be used by other parts of the software now
        """
        devicelist = []
        devices = await BleakScanner.discover(timeout=timeout)
        devicelist = self.validate_manufacturer(devices, manufacturer_id)
        return devicelist

    async def run_single_ble_command(self, tag: BLEDevice, read_chan: str, write_chan: str, cmd: str = "", timeout = 20.0, cb: Callable[[int, bytearray], None] = None, retries: int = 0, max_retries: int = 5, disconnect: bool = True):
        """ Connects to a given tag and starts notification of the given callback
        Arguments:
            tag: communication device abstraction
            timeout: how long should one run of the function take?
            b: Callback that will be executed when a notification is received
        """
        try:
            async with BleakClient(tag, timeout = timeout) as client:
                await client.start_notify(char_specifier = read_chan, callback = cb)
                await client.write_gatt_char(write_chan, bytearray.fromhex(cmd), disconnect)
                time.sleep(timeout)
                # await client.stop_notify(char_specifier = read_chan)
                if disconnect:
                    self.logger.warn("disconnecting...")
                    await client.disconnect()
                else:
                    self.logger.warn("waiting...")
                    await self.stopEvent.wait()
                    self.logger.warn("ending...")
                    await client.disconnect()
                    await self.stopEvent.clear()

        except Exception as e:
            if retries < max_retries:
                self.logger.warn(f"{e} - retrying...")
                await self.run_single_ble_command(tag, read_chan, write_chan, cmd, timeout, cb, retries+1, max_retries)
            return

    def validate_manufacturer(self, devices: list[BLEDevice], manufacturer_id: int = 0) -> list[BLEDevice]:
        """ This funcion updates the internal mac_list. If a MAC address passed the
        checked_mac_address process, it will extend the list 'mac'.
        Arguments:
            devices: device passed by the BleakScanner function

        TODO: check for vendor name or some other idempotent information
        """
        devicelist = []
        for i in devices:
            if "manufacturer_data" in i.metadata:
                if manufacturer_id in i.metadata["manufacturer_data"]:
                    self.logger.info(colored('Device: %s with Address %s discovered!' % (i.name, i.address), "green", attrs=['bold']) )
                    devicelist.append(i)
        return devicelist
