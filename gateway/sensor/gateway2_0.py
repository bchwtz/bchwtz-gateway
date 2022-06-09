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
    """This is a simple "terminal" program that uses the Nordic Semiconductor
    (nRF) UART service. It reads from stdin and sends each line of data to the
    remote device. Any data received from the device is printed to stdout.
    """

    def match_nus_uuid(device: BLEDevice, adv: AdvertisementData):
        # This assumes that the device includes the UART service UUID in the
        # advertising data. This test may need to be adjusted depending on the
        # actual advertising data supplied by the device.
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
        if data[0] == 0x11:
            # Daten
            # Time wird gesetzt um die Abfrage des Ringbuffers auf 10 Sekunden zu setzen -> Querabhängigkeit zu _timeout Funktion
            
            print("Received data block: %s" % hexlify(data[1:]))
        # Response messages des Sensors
        if data[0] == 0x22 and data[2] == 0xF2:
            status_string = str(ri_error_to_string(data[3]), )
            print("Status: %s" % status_string)

        if data[0] == 0x22 and data[2] == 0xF3:
            print("Received heartbeat: {}".format(
                int.from_bytes(data[4:6], byteorder='big', signed=False))
                )
            status_string = str(ri_error_to_string(data[3]), )
            print("Status: %s" % status_string)
            

        if data[0] == 0x4A or data[0] == 0x21:
            
            print("Received: %s" % hexlify(data))
            status_string = str(ri_error_to_string(data[3]), )
            print("Status: %s" % status_string)
            
            if data[2] == 0x09:
                print("Received time: %s" % hexlify(data[:-9:-1]))
                received_time=time.strftime('%D %H:%M:%S', time.gmtime(int(hexlify(data[:-9:-1]), 16) / 1000))
                print(received_time)

            # elif data[0] == 0x4a and data[3] == 0x00:
            #     sample_rate = ""
            #     if data[4] == 201:
            #         print("Samplerate: 400 Hz")
            #         sample_rate = 400
            #     else:
            #         print("Samplerate:    %d Hz" % data[4])
            #         sample_rate=int(data[4])
            #     received_config=message_return_value.from_get_config(status=status_string,sample_rate=sample_rate,resolution= int(data[5]),
            #                                         scale=int(data[6]),dsp_function=int(data[7]), dsp_parameter=int(data[8]),
            #                                         mode="%x"% data[9],divider=int(data[10]), mac=client.address)
            #     self.sensor_data.append(received_config.returnValue.__dict__)
            #     self.config = SensorConfig.from_dict(received_config.returnValue.__dict__)
            #     self.notification_done=True

        elif data[0] == 0xfb and data[1] == 0x0d:
            
            print("Received: %s" % hexlify(data))
            logging_status = data[3]
            ringbuffer_start = data[4]
            ringbuffer_end = data[5]
            ringbuffer_size = data[6]
            valid_records = data[7] | (data[8] << 8)
            dirty_records = data[9] | (data[10] << 8)
            words_reserved = data[11] | (data[12] << 8)
            words_used = data[13] | (data[14] << 8)
            largest_contig = data[15] | (data[16] << 8)
            freeable_words = data[17] | (data[18] << 8)
            
            print("Last Status %s" % (str(ri_error_to_string(logging_status)),))
            print("Ringbuffer start %d" % (ringbuffer_start,))
            print("Ringbuffer end %d" % (ringbuffer_end,))
            print("Ringbuffer size %d" % (ringbuffer_size,))
            print("Valid records %d" % (valid_records,))
            print("Dirty records %d" % (dirty_records,))
            print("Words reserved %d" % (words_reserved,))
            print("Words used %d" % (words_used,))
            print("Largest continuos %d" % (largest_contig,))
            print("Freeable words %d\n" % (freeable_words,))
            

    print(device.name)
    async with BleakClient(device, disconnected_callback=handle_disconnect) as client:
        await client.start_notify(UART_TX_CHAR_UUID, handle_rx)

        print("Connected, start typing and press ENTER...")

        loop = asyncio.get_running_loop()
        run = True
        while run:
            # This waits until you type a line and press ENTER.
            # A real terminal program might put stdin in raw mode so that things
            # like CTRL+C get passed to the remote device.
            data = await loop.run_in_executor(None, sys.stdin.readline)

            # data will be empty on EOF (e.g. CTRL+D on *nix)
            if not data:
                break

            # some devices, like devices running MicroPython, expect Windows
            # line endings (uncomment line below if needed)
            # data = data.replace(b"\n", b"\r\n")
            # data = data.replace('\n', '')
            command = int(data)
            # print("command" + command)
            if command == 1:
                # send get log statics
                print("send get log statictis")
                await client.write_gatt_char(UART_RX_CHAR_UUID, bytearray.fromhex("FAFA0d0000000000000000"))
            elif command == 2:
                #  send get sensor time
                print("get heartbeat")
                await client.write_gatt_char(UART_RX_CHAR_UUID, bytearray.fromhex("2200F30000000000000000"))
            elif command == 3:
                #  send get sensor time
                print("set heartbeat to 1 sec")
                hex_beat = hex(1000)[2:]
                hex_msg = f"2200F2{'0000'[:4 - len(hex_beat)]}{hex_beat}000000000000"
                print(hex_msg)
                await client.write_gatt_char(UART_RX_CHAR_UUID, bytearray.fromhex(hex_msg))
            elif command == 4:
                #  send get sensor time
                print("set heartbeat to 3 sec")
                hex_beat = hex(int(3000))[2:]
                hex_msg = f"2200F2{'0000'[:4 - len(hex_beat)]}{hex_beat}000000000000"
                await client.write_gatt_char(UART_RX_CHAR_UUID, bytearray.fromhex(hex_msg))
            elif command == 10:
                await client.disconnect()
                run = False
            # print("sent:", data)


if __name__ == "__main__":
    try:
        asyncio.run(uart_terminal())
        print("hallo")
    except asyncio.CancelledError:
        # task is cancelled on disconnect, so we ignore this error
        pass