#!/usr/bin/env python
# coding: utf-8

# https://bleak.readthedocs.io/en/latest/api.html
#
# https://pypi.org/project/bleak/
#
# https://github.com/hbldh/bleak

# loop.run_until_complete() erzeugt im Jupyter Notebook einen Fehler
# siehe https://pypi.org/project/nest-asyncio/
import time
from datetime import datetime
from bleak import BleakClient
from bleak import BleakScanner
from binascii import hexlify
import asyncio
import nest_asyncio
from gateway.sensor.decode_utils import unpack10, unpack12, unpack8

from gateway.sensor.errorcode_utils import ri_error_to_string
nest_asyncio.apply()

from gateway.event.event import Event_ts

loop = asyncio.get_event_loop()

async def scan_devices():
    devices = await BleakScanner.discover()
    return devices

devices = loop.run_until_complete(scan_devices())
# Mit der Ausführung der nächsten Zelle warten bis der Scan abgeschlossen ist. Weil die Ausführung asynchron erfolgt wartet das Jupyter Notebook nicht automatisch.
ruuviTags = [d.address for d in (devices) if("Ruuvi" in d.name)]
if(len(ruuviTags) < 1):
    raise Exception("No Ruuvi Tag found")

address = ruuviTags[0]
print(address)

UART_SRV = '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'
UART_TX = '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'
UART_RX = '6E400003-B5A3-F393-E0A9-E50E24DCCA9E'

stopEvent = Event_ts()

# Pointer to file which receives data
class filepointer:
    csvfile = None

# configurations
samplerate = 10
resolution = 10
scale = 2

def callback(sender: int, value: bytearray):
    print("Received: %s" % hexlify(value))
    if value[0] == 0x4A:
        print("Status: %s" % (str(ri_error_to_string(value[3]),)))
        stopEvent.set()
    elif value[0] == 0x11:
        if resolution == 8:
            unpack8(value[1:], samplerate, scale)
        elif resolution == 10:
            unpack10(value[1:], samplerate, scale)
        elif resolution == 12:
            unpack12(value[1:], samplerate, scale)

async def setupForStreaming(address, samplerate, resolution, scale):
    async with BleakClient(address) as client:
        await client.start_notify(UART_RX, callback)
        await client.write_gatt_char(UART_TX, bytearray.fromhex("4a4a02%02x%02x%02xFFFFFF0000" % (samplerate, resolution, scale)))
        await stopEvent.wait()
        print("Samplerate set")
        await client.stop_notify(UART_RX)
        stopEvent.clear()


async def activateStreaming(address):
    async with BleakClient(address) as client:
        await client.start_notify(UART_RX, callback)
        await client.write_gatt_char(UART_TX, bytearray.fromhex("4a4a080200000000000000"))
        print("Streaming activated")
        await stopEvent.wait()
        await client.stop_notify(UART_RX)


async def listenForData(address, samplingtime, filename):
    filepointer.csvfile = open(filename, "w")
    async with BleakClient(address) as client:
        await client.start_notify(UART_RX, callback)
        await asyncio.sleep(samplingtime)
        await client.stop_notify(UART_RX)
    filepointer.csvfile.close()
    filepointer.csvfile = None

loop.run_until_complete(setupForStreaming(
    address, samplerate, resolution, scale))

loop.run_until_complete(activateStreaming(address))

filename = str(int(time.time()))+".csv"
loop.run_until_complete(listenForData(address, 10*60, filename))

print(filename)
