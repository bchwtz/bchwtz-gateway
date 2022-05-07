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

def ri_error_to_string(error):
    if(error == 0):
        return "RD_SUCCESS"
    elif(error == 1):
        return "RD_ERROR_INTERNAL"
    elif(error == 2):
        return "RD_ERROR_NO_MEM"
    elif(error == 3):
        return "RD_ERROR_NOT_FOUND"
    elif(error == 4):
        return "RD_ERROR_NOT_SUPPORTED"
    elif(error == 5):
        return "RD_ERROR_INVALID_PARAM"
    elif(error == 6):
        return "RD_ERROR_INVALID_STATE"
    elif(error == 7):
        return "RD_ERROR_INVALID_LENGTH"
    elif(error == 8):
        return "RD_ERROR_INVALID_FLAGS"
    elif(error == 9):
        return "RD_ERROR_INVALID_DATA"
    elif(error == 10):
        return "RD_ERROR_DATA_SIZE"
    elif(error == 11):
        return "RD_ERROR_TIMEOUT"
    elif(error == 12):
        return "RD_ERROR_NULL"
    elif(error == 13):
        return "RD_ERROR_FORBIDDEN"
    elif(error == 14):
        return "RD_ERROR_INVALID_ADDR"
    elif(error == 15):
        return "RD_ERROR_BUSY"
    elif(error == 16):
        return "RD_ERROR_RESOURCES"
    elif(error == 17):
        return "RD_ERROR_NOT_IMPLEMENTED"
    elif(error == 18):
        return "RD_ERROR_SELFTEST"
    elif(error == 19):
        return "RD_STATUS_MORE_AVAILABLE"
    elif(error == 20):
        return "RD_ERROR_NOT_INITIALIZED"
    elif(error == 21):
        return "RD_ERROR_NOT_ACKNOWLEDGED"
    elif(error == 22):
        return "RD_ERROR_NOT_ENABLED"
    elif(error == 31):
        return "RD_ERROR_FATAL"

# Pointer to file which receives data
class filepointer:
    csvfile = None

def unpack8(bytes, samplingrate, scale):
    j = 0
    pos = 0
    accvalues = [0, 0, 0]
    timestamp = 0
    timeBetweenSamples = 1000/samplingrate

    if(scale == 2):
        faktor = 16/(256*1000)
    elif(scale == 4):
        faktor = 32/(256*1000)
    elif(scale == 8):
        faktor = 64/(256*1000)
    elif(scale == 16):
        faktor = 192/(256*1000)

    while(pos < len(bytes)):
        # Ein Datenblock bei 8 Bit Auflösung ist 104 Bytes lang
        # Jeder Datenblock beginnt mit einem Zeitstempel
        if pos % 104 == 0:
            timestamp = int.from_bytes(
                bytes[pos:pos+7], byteorder='little', signed=False)
            pos += 8
            j = 0

        value = bytes[pos] << 8
        pos += 1
        if(value & 0x8000 == 0x8000):
            # negative Zahl
            # 16Bit Zweierkomplement zurückrechnen
            value = value ^ 0xffff
            value += 1
            # negieren
            value = -value

        # save value
        accvalues[j] = value * faktor

        # Write to CSV
        if(filepointer.csvfile != None and j % 3 == 2):
            if(filepointer.csvfile != None):
                filepointer.csvfile.write("%d;%f;%f;%f\n" % (
                    datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'), accvalues[0], accvalues[1], accvalues[1]))
            else:
                print("%d;%f;%f;%f\n" %
                    (datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'), accvalues[0], accvalues[1], accvalues[1]))
            timestamp += timeBetweenSamples
            j = 0
        else:
            j += 1

def unpack10(bytes, samplingrate, scale):
    i = 0
    j = 0
    pos = 0
    accvalues = [0, 0, 0]
    timestamp = 0
    timeBetweenSamples = 1000/samplingrate

    if(scale == 2):
        faktor = 4/(64*1000)
    elif(scale == 4):
        faktor = 8/(64*1000)
    elif(scale == 8):
        faktor = 16/(64*1000)
    elif(scale == 16):
        faktor = 48/(64*1000)

    while(pos < len(bytes)-1):
        # Ein Datenblock bei 10 Bit Auflösung ist 128 Bytes lang
        # Jeder Datenblock beginnt mit einem Zeitstempel
        if pos % 128 == 0:
            timestamp = int.from_bytes(
                bytes[pos:pos+7], byteorder='little', signed=False)
            pos += 8
            i = 0
            j = 0

        else:
            if i == 0:
                value = bytes[pos] & 0xc0
                value |= (bytes[pos] & 0x3f) << 10
                pos += 1
                value |= (bytes[pos] & 0xc0) << 2
                i += 1

            elif i == 1:
                value = (bytes[pos] & 0x30) << 2
                value |= (bytes[pos] & 0x0f) << 12
                pos += 1
                value |= (bytes[pos] & 0xf0) << 4
                i += 1

            elif i == 2:
                value = (bytes[pos] & 0x0c) << 4
                value |= (bytes[pos] & 0x03) << 14
                pos += 1
                value |= (bytes[pos] & 0xfc) << 6
                i += 1

            elif i == 3:
                value = (bytes[pos] & 0x03) << 6
                pos += 1
                value |= (bytes[pos]) << 8
                pos += 1
                i = 0

            if(value & 0x8000 == 0x8000):
                # negative Zahl
                # 16Bit Zweierkomplement zurückrechnen
                value = value ^ 0xffff
                value += 1
                # negieren
                value = -value

            # save value
            accvalues[j] = value * faktor

            j += 1

            # Write to CSV
            if(j == 3):
                if(filepointer.csvfile != None):
                    filepointer.csvfile.write("%d;%f;%f;%f\n" % (
                        timestamp, accvalues[0], accvalues[1], accvalues[2]))
                else:
                    print("%d;%f;%f;%f" %
                        (datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'), accvalues[0], accvalues[1], accvalues[2]))
                timestamp += timeBetweenSamples
                j = 0


def unpack12(bytes, samplingrate, scale):
    i = 0
    j = 0
    pos = 0
    accvalues = [0, 0, 0]
    timestamp = 0
    timeBetweenSamples = 1000/samplingrate

    if(scale == 2):
        faktor = 1/(16*1000)
    elif(scale == 4):
        faktor = 2/(16*1000)
    elif(scale == 8):
        faktor = 4/(16*1000)
    elif(scale == 16):
        faktor = 12/(16*1000)

    while(pos < len(bytes)-1):
        # Ein Datenblock bei 12 Bit Auflösung ist 152 Bytes lang
        # Jeder Datenblock beginnt mit einem Zeitstempel
        if pos % 152 == 0:
            timestamp = int.from_bytes(
                bytes[pos:pos+7], byteorder='little', signed=False)
            pos += 8
            i = 0
            j = 0

        else:
            if i == 0:
                value = bytes[pos] & 0xf0
                value |= (bytes[pos] & 0x0f) << 12
                pos += 1
                value |= (bytes[pos] & 0xf0) << 4
                i += 1

            elif i == 1:
                value = (bytes[pos] & 0x0f) << 4
                pos += 1
                value |= bytes[pos] << 8
                pos += 1
                i = 0

            if(value & 0x8000 == 0x8000):
                # negative Zahl
                # 16Bit Zweierkomplement zurückrechnen
                value = value ^ 0xffff
                value += 1
                # negieren
                value = -value

            # save value
            accvalues[j] = value * faktor

            j += 1

            # Write to CSV
            if(j == 3):
                if(filepointer.csvfile != None):
                    filepointer.csvfile.write("%d;%f;%f;%f\n" % (
                        timestamp, accvalues[0], accvalues[1], accvalues[2]))
                else:
                    print("%d;%f;%f;%f" %
                        (datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'), accvalues[0], accvalues[1], accvalues[2]))
                timestamp += timeBetweenSamples
                j = 0

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
