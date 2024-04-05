import binascii
from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice
import asyncio
import logging
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
        self.logger.setLevel(logging.INFO)
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
        # devicelist = self.validate_manufacturer(devices, manufacturer_id)
        return devicelist

    async def run_single_ble_command(self, tag: BLEDevice, read_chan: str, write_chan: str, cmd: str = "", timeout: float = 20.0, cb: Callable[[int, bytearray], None] = None, retries: int = 0, max_retries: int = 5, await_response: bool = True):
        """ Connects to a given tag and starts notification of the given callback
        Arguments:
            tag: communication device abstraction
            timeout: how long should one run of the function take?
            b: Callback that will be executed when a notification is received
        """
        self.logger.info("connecting to %s", tag.address)
        try:

            async with BleakClient(tag) as client:
                # if not device.details["props"]["Paired"]:
                #     await client.pair()
                self.logger.info("connected to %s", tag.address)
                self.logger.info("sending command %s", cmd)
                if cb is not None:
                    await client.start_notify(char_specifier = read_chan, callback = cb)
                await client.write_gatt_char(write_chan, bytearray.fromhex(cmd), await_response)
                if await_response:
                    self.logger.info("disconnecting...")
                else:
                    self.logger.info("waiting...")
                    await self.stopEvent.wait()
                self.logger.info("ending...")
                self.stopEvent.clear()

        except Exception as e:
            if retries < max_retries:
                self.logger.warn(f"{e} - retrying...")
                await self.run_single_ble_command(tag, read_chan, write_chan, cmd, timeout, cb, retries+1, max_retries)
            return

    async def listen_for_data_stream(self, tag: BLEDevice, read_chan: str, timeout: float = 20.0, cb: Callable[[int, bytearray], None]=None):
            client = await self.get_client(tag)
            await client.start_notify(char_specifier = read_chan, callback = cb)
            asyncio.sleep(timeout)
            # await client.stop_notify(char_specifier = read_chan)
            await client.stop_notify(char_specifier=read_chan)

