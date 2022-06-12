"""
UART Service
-------------
An example showing how to write a simple program using the Nordic Semiconductor
(nRF) UART service.
"""

import asyncio
from binascii import hexlify
import sys
import time

from bleak import BleakScanner, BleakClient
from bleak.backends.scanner import AdvertisementData
from bleak.backends.device import BLEDevice

from errorcode_utils import ri_error_to_string

UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
UART_TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"
# UART_SRV= '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'
# UART_TX= '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'
# UART_RX= '6E400003-B5A3-F393-E0A9-E50E24DCCA9E' 
# Adv_UART_RX= '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'

# All BLE devices have MTU of at least 23. Subtracting 3 bytes overhead, we can
# safely send 20 bytes at a time to any device supporting this service.
UART_SAFE_SIZE = 20


async def uart_terminal():
    def match_nus_uuid(device: BLEDevice, adv: AdvertisementData):
        if UART_SERVICE_UUID.lower() in adv.service_uuids:
            return True
        return False

    device = await BleakScanner.find_device_by_filter(match_nus_uuid)

    def handle_disconnect(_: BleakClient):
        print("Device was disconnected, goodbye.")
        # cancelling all tasks effectively ends the program
        for task in asyncio.all_tasks():
            task.cancel()

    def handle_rx(_: int, data: bytearray):
        print("received:", data)
        
    async with BleakClient(device, disconnected_callback=handle_disconnect) as client:
        await client.start_notify(UART_TX_CHAR_UUID, handle_rx)
        print("Connected, start typing and press ENTER...")

        loop = asyncio.get_running_loop()
        idle = True
        while idle:
            data = await loop.run_in_executor(None, sys.stdin.readline)

            # data will be empty on EOF (e.g. CTRL+D on *nix)
            if not data:
                break

            command = int(data)
            # print("command" + command)
            if command == 1:
                # send get log statics
                await client.write_gatt_char(UART_RX_CHAR_UUID, bytearray.fromhex("FAFA0d0000000000000000"))
            elif command == 2:
                #  send get sensor time
                await client.write_gatt_char(UART_RX_CHAR_UUID, bytearray.fromhex("2200F30000000000000000"))
            elif command == 10:
                await client.disconnect()
                idle = False


if __name__ == "__main__":
    try:
        asyncio.run(uart_terminal())
    except asyncio.CancelledError:
        # task is cancelled on disconnect, so we ignore this error
        pass