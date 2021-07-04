# -*- coding: utf-8 -*-
"""
TO-DOs:
    1. init : self.find_tags gehört nicht in den Konstruktor

"""

# %% libraries

# import operator
import asyncio
import nest_asyncio
import re
import time
from binascii import hexlify
from bleak import BleakScanner
from bleak import BleakClient
import datetime
import logging
from enum import Enum
import crcmod
import struct

# %% Global variables
readAllString = "FAFA030000000000000000"
UART_SRV = '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'
UART_TX = '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'
UART_RX = '6E400003-B5A3-F393-E0A9-E50E24DCCA9E'
sensordaten = bytearray()
crcfun = crcmod.mkCrcFun(0x11021, rev=False, initCrc=0xffff, xorOut=0)

# %% Configuration Logger------------------------------------------------------
# Creat a named logger 'SensorGatewayBleak' and set it on INFO level
Log_SensorGatewayBleak = logging.getLogger('SensorGatewayBleak')
Log_SensorGatewayBleak.setLevel(logging.INFO)

# Create a file handler
file_handler = logging.FileHandler('SensorGatewayBleak.log')
file_handler.setLevel(logging.INFO)

# Create a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create a formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
Log_SensorGatewayBleak.addHandler(file_handler)
Log_SensorGatewayBleak.addHandler(console_handler)

# %% Acitvate nest_asyncio-----------------------------------------------------
# Aktivate nest_asyncio to prevent an error while processing the communication loops
nest_asyncio.apply()
Log_SensorGatewayBleak.info('Set nest_asyncio as global configuration')


# %%region enums for sensor config

class SamplingRate(Enum):
    x01 = 1
    x0A = 10
    x19 = 25
    x32 = 50
    x64 = 100
    xC8 = 200
    xC9 = 400


class SamplingResolution(Enum):
    x08 = 8
    x0A = 10
    x0C = 12


class MeasuringRange(Enum):
    x02 = 2
    x04 = 4
    x08 = 8
    x10 = 16


# %% Class Async-Events
# Thread Safe Event Class
class Event_ts(asyncio.Event):
    def clear(self):
        self._loop.call_soon_threadsafe(super().clear)

    def set(self):
        self._loop.call_soon_threadsafe(super().set)


# %% Class RuuviTagAccelerometerCommunicationBleak----------------------------
class RuuviTagAccelerometerCommunicationBleak(Event_ts):
    def __init__(self):
        self.stopEvent = Event_ts()
        self.delta = 'Time'
        self.start_time = 'Time'
        self.end_time = 'Time'
        # Constructor of the class RuuviTagAccelerometerCommunicationBleak
        self.client = 'TestClient'
        # Create a child of the previously created logger 'SensorGatewayBleak'
        self.logger = logging.getLogger('SensorGatewayBleak.ClassRuuvi')
        self.logger.info('Initialize child logger ClassRuuvi')
        self.logger.info('Start constructor')

        # MAC - list of addresses of the bluetooth devices
        self.mac = []

        # Data recieved by the bluetooth devices
        self.data = []

        # Variable for bandwidth calculation
        self.start_time = time.time()

        # Auxiliary Variables
        self.reading_done = False
        self.success = ""
        # self.ConnectionError = False

        # Search for asyncio loops that are already running
        self.my_loop = asyncio.get_event_loop()
        # self.my_loop = asyncio.get_running_loop()
        self.logger.info('Searching for running loops completed')

        # Create a task 
        # taskobj = self.my_loop.create_task(self.find_tags())
        # self.logger.info('Searching for tags completed')
        #
        # self.my_loop.run_until_complete(taskobj)

        # Einige functionen müssen evtl. in eine __enter__-Funktion z.B. fand_tags

    # def __exit__(self):

    #     self.data = []
    #     self.logger.info('Reset self.data !')
    #     self.mac = []
    #     self.logger.info('Reset self.mac')
    #     # Do we need a "Reset Tag"-Command to get the Tag in a safe state?
    """    Check if mac address is a valid mac address    """

    def __check_mac_address(self, mac):
        if re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", mac.lower()):
            self.logger.info('MAC set to specific Mac-Address')

            return self.find_tags(mac)
        else:
            self.logger.error("Mac is not valid!")
            return False

    """    validate that found macs are ruuvi tags    """

    def __validate_mac(self, devices):
        tags_so_far = len(self.mac)
        for i in devices:
            self.logger.info('Device: %s with Address %s found!' % (i.name, i.address))
            if ("Ruuvi" in i.name) & (i.address not in self.mac):
                self.mac.append(i.address)
                self.logger.info('Device: %s with Address %s saved in MAC list!' % (i.name, i.address))
        tags_new = len(self.mac) - tags_so_far
        self.logger.info('%d new Ruuvi tags were found' % tags_new)

    def work_loop(self, macs="", command=""):
        print(macs)
        if not isinstance(macs, list):
            print("Search Mac")
            if macs != "":
                # self.__check_mac_address()
                # taskobj = self.my_loop.create_task(self.__check_mac_address(macs))
                # self.my_loop.run_until_complete(self.__check_mac_address())
                # print(taskobj.result())
                if not self.__check_mac_address(macs):
                    return
            else:
                taskobj = self.my_loop.create_task(self.find_tags())
                self.my_loop.run_until_complete(taskobj)
        try:
            taskobj = self.my_loop.create_task(self.connect_to_mac_command(command_string=command,specific_mac=macs))
            self.my_loop.run_until_complete(taskobj)
            # self.logger.info("Logging activated!")
        except RuntimeError as e:
            self.logger.error("Error while activate logging: {}".format(e))

    # -------------Find -> Connect -> Listen-Functions---------------------
    async def find_tags(self, mac=""):
        # First Funktion -> Find Ruuvitags

        if mac != "":
            device = [await BleakScanner.find_device_by_address(mac)]
            self.__validate_mac(device)
        else:
            devices = await BleakScanner.discover(timeout=5.0)
            self.__validate_mac(devices)
        if len(self.mac) == 0:
            return False
        return True

    async def connect_to_mac_command(self, command_string, specific_mac=""):
        # Second Funktion -> Connect to Ruuvitag and send commands
        if specific_mac != "":
            mac = [specific_mac]
        else:
            mac = self.mac
        for i in mac:
            print("Mac: "+str(i))
            print(command_string)
            try:
                async with BleakClient(i) as client:
                    # Send the command (Wait for Response must be True)
                    await client.start_notify(UART_RX, self.handle_sensor_commands)
                    await client.write_gatt_char(UART_TX,
                                                 bytearray.fromhex(command_string), True)
                    self.logger.info('Message send to MAC: %s' % (i))
                    await asyncio.sleep(1)
                    await client.stop_notify(UART_RX)
                    self.logger.info('Stop notify: %s' % (i))
            except Exception as e:
                self.logger.warning('Connection faild at MAC %s' % (i))
                self.logger.error("Error: {}".format(e))

            self.logger.info("Task done connect_to_mac_command!")

            # Reciving and Handling of Callbacks

    # Main Function for sensordatalogging
    async def connect_to_mac(self, i, readCommand):
        try:
            print("Mac address:" + str(i))
            async with BleakClient(i) as client:
                # Send the command (Wait for Response must be True)
                self.client = client
                await client.start_notify(UART_RX, self.handle_data)
                await client.write_gatt_char("6e400002-b5a3-f393-e0a9-e50e24dcca9e", bytearray.fromhex(readCommand),
                                             True)
                self.logger.info('Message send to MAC: %s' % (i))
                self.start_time = time.time()
                # print(self.start_time)
                # print(time.time())
                self.start_time = time.time()
                await self.stopEvent.wait()
                await client.stop_notify(UART_RX)
                self.stopEvent.clear()
                self.logger.info('Stop notify: %s' % (i))

        except Exception as e:
            self.logger.error('Error occured on tag {} with errorcode: {}'.format(i, e))
            self.logger.warning('Connection to tag not available')

            return None


    # ----------------------Interprete Ruuvitag Callback-----------------------
    async def handle_sensor_commands(self, sender: int, value: bytearray):
        """
        handle -- integer, characteristic read handle the data was received on
        value -- bytearray, the data returned in the notification
        """
        self.logger.info("handle_sensor_command called sender: {} and value {}".format(sender, value))

        if value[0] == 0xFB:
            if (value[1] == 0x00):
                self.logger.info("Status: %s" % str(self.ri_error_to_string(value[2])))
            elif value[0] == 0x4a and value[3] == 0x00:
                print("Status: %s" % (str(self.ri_error_to_string(value[3]), )))

                print("test Value")

                print(value[4])

                if value[4] == "C9":
                    print("Samplerate: 400 Hz")
                else:
                    print("Samplerate:    %d Hz" % value[4])
                print("Resolution:    %d Bits" % (int(value[5])))
                print("Scale:         %d G" % value[6])
                print("DSP function:  %x" % value[7])
                print("DSP parameter: %x" % value[8])
                print("Mode:          %x" % value[9])
                if value[10] > 1:
                    print("Frequency divider: %d" % value[10])

            elif (value[1] == 0x07):
                print("Status: %s" % str(self.ri_error_to_string(value[2])))

                print(value[3])
                """400 Hz cant be shown within 8bit. Value xC9 (201) is used for 400 Hz"""
                if value[3] == 201:
                    print("Samplerate: 400 Hz")
                else:
                    print("Samplerate:    %d Hz" % value[3])
                print("Resolution:    %s Bits" % (int(value[4])))
                print("Scale:         %xG" % value[5])
                print("DSP function:  %x" % value[6])
                print("DSP parameter: %x" % value[7])
                print("Mode:          %x" % value[8])
            elif (value[1] == 0x09):
                print("TIME")
                print("Status: %s" % str(self.ri_error_to_string(value[2])))
                # die Daten sind little-endian (niegrigwertigstes Bytes zuerst) gespeichert
                # die menschliche leseart erwartet aber big-endian (höchstwertstes Bytes zuerst)
                # deswegen Reihenfolge umdrehen
                print("Received data: %s" % hexlify(value[:-9:-1]))
                print(time.strftime('%D %H:%M:%S', time.gmtime(int(hexlify(value[:-9:-1]), 16) / 1000)))
            else:
                print("Antwort enthält falschen Typ")

    # ------------------------Activate/Deactivate Logging----------------------
    def activate_logging_at_sensor(self, specific_mac=""):
        # """
        # Loop funktion zum aufrufen in eigene Funktion, die activate Logging aufruft.
        # Async
        # """
        command_string = "FAFA0a0100000000000000"
        self.success = False
        self.work_loop(macs=specific_mac, command=command_string)
        if self.success:
            print("logging activated")
        else:
            logging.error("Logging is not activated")
            print("Logging is not activated")

    def deactivate_logging_at_sensor(self, specific_mac=""):
        self.success = False
        command_string = "FAFA0a0000000000000000"
        self.work_loop(macs=specific_mac, command=command_string)
        if self.success:
            print("logging deactivated")
        else:
            logging.error("Logging is not deactivated")
            print("Logging is not deactivated")

    # ----------------------------Acceleration Logging-------------------------
    def get_acceleration_data(self, specific_mac=""):
        # global readAllString #? Wofür ist dieser String
        self.data = []
        self.ConnectionError = False
        readAllString = "FAFA050000000000000000"
        # my_loop = asyncio.get_running_loop()
        # This is a DEBUG Funktion to Connect to a specific tag
        if specific_mac != "":
            if re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", specific_mac.lower()):
                mac = [specific_mac]
            else:
                self.logger.error('Mac address is not valid' + specific_mac)
                print("Mac is not valid")
                return
        else:
            self.logger.info('Try to get acceleration data from tags')
            mac = self.mac
            # mac = self.find_tags_mac()

        """Read acceleration samples for each sensor"""
        for i in mac:
            self.reading_done = False
            global sensordaten
            sensordaten = bytearray()
            taskobj = self.my_loop.create_task(self.connect_to_mac(i, readAllString))
            self.my_loop.run_until_complete(taskobj)

            """Wait  until all reading is done. We can only read one sensor at the time"""
            # while not self.reading_done:
            #     time.sleep(1)

        # try:
        #     recieved_data = self.data
        #     """Exit function if recieved data is empty"""
        #     if (len(self.data[0][0]) == 0):
        #         print("No data stored")
        #         return
        #     """Write data into csv file"""
        #     for i in range(len(recieved_data)):
        #         data = list(zip(recieved_data[i][0]))
        #         current_mac = recieved_data[i][1]
        #         for i in data:
        #             with open("acceleration-{}.csv".format(data[0][0][3]), 'a') as f:
        #                 f.write("{},{}".format(str(i[0])[1:-1], current_mac))
        #                 f.write("\n")
        # except Exception as e:
        #     self.logger.error("Error: {}".format(e))
        return self.data

    # --------------------------------handle data--------------------------------

    """Handle received data"""

    async def handle_data(self, handle, value):
        """
        handle -- integer, characteristic read handle the data was received on
        value -- bytearray, the data returned in the notification
        """
        print(time.time())
        if (value.startswith(b'\xfc')):
            # Daten
            sensordaten.extend(value[1:])
            print("Received data block: %s" % hexlify(value[1:]))
            # Marks end of data stream
        elif (value.startswith(b'\xfb')):
            self.end_time = time.time()
            print(len(sensordaten))
            self.delta = len(sensordaten) / (self.end_time - self.start_time)

            print('Bandwidth : {} Bytes/Second'.format(self.delta))
            self.stopEvent.set()
            # await self.client.stop_notify(UART_RX)
            # Status
            print("Status: %s" % str(self.ri_error_to_string(value[2])))

            crc = value[11:13];
            print("Received CRC: %s" % hexlify(crc))

            # CRC validation
            print(sensordaten)
            ourcrc = crcfun(sensordaten)
            print("Recalculated CRC: %x" % ourcrc)

            print("Received %d bytes" % len(sensordaten))
            print(hexlify(crc))
            if hexlify(crc) == bytearray():
                print("No crc Received")
                # device.disconnect
                self.reading_done = True
                self.taskrun = False
                # adapter.reset()
                return None

            if int(hexlify(crc), 16) != ourcrc:
                print("CRC are unequal")
                # device.disconnect
                self.reading_done = True
                self.taskrun = False
                # adapter.reset()
                return None

                # device.disconnect()

            self.taskrun = False

            timeStamp = hexlify(sensordaten[7::-1])

            # Start data
            if (value[4] == 12):
                # 12 Bit
                self.logger.info("Start processing reveived data with process_sensor_data_12")
                AccelorationData = self.process_sensor_data_12(sensordaten, value[5], value[3])
            elif (value[4] == 10):
                # 10 Bit
                self.logger.info("Start processing reveived data with process_sensor_data_10")
                AccelorationData = self.process_sensor_data_10(sensordaten, value[5], value[3])
            elif (value[4] == 8):
                # 8 Bit
                self.logger.info("Start processing reveived data with process_sensor_data_10")
                AccelorationData = self.process_sensor_data_8(sensordaten, value[5], value[3])
            else:
                print("Unknown Resolution")
            if AccelorationData != None:
                self.logger.info("Run in Funktion AccelorationData != None")
                self.data.append([list(map(list, zip(AccelorationData[0], AccelorationData[1], AccelorationData[2],
                                                     AccelorationData[3])))])
                print(self.data)
            self.reading_done = True

    # device.subscribe(uuIdRead, callback=handle_data)

    ##%% region processdata
    def process_sensor_data_8(self, bytes, scale, rate):
        j = 0
        pos = 0
        koords = ["\nx", "y", "z"]
        x_vector = list()
        y_vector = list()
        z_vector = list()
        timestamp_list = list()
        time_between_samples = 1 / rate

        if (scale == 2):
            print("Scale: 2G")
            faktor = 16 / (256 * 1000)
        elif (scale == 4):
            print("Scale: 4G")
            faktor = 32 / (256 * 1000)
        elif (scale == 8):
            print("Scale: 8G")
            faktor = 64 / (256 * 1000)
        elif (scale == 16):
            print("Scale: 16G")
            faktor = 192 / (256 * 1000)

        while (pos < len(bytes)):
            """Read and store timestamp. This is little endian again"""
            t = bytes[pos:pos + 8]
            inv_t = t[::-1]
            timestamp = int(hexlify(inv_t), 16) / 1000
            #
            # dt = datetime.datetime.utcfromtimestamp(int(hexlify(inv_t), 16) / 1000).strftime('%Y-%m-%d %H:%M:%S.%f')
            # print(dt)
            pos += 8
            """Read values"""
            for i in range(96):
                value = bytes[pos] << 8
                pos += 1
                if (value & 0x8000 == 0x8000):
                    # negative Zahl
                    # 16Bit Zweierkomplement zurückrechnen
                    value = value ^ 0xffff
                    value += 1
                    # negieren
                    value = -value
                value *= faktor

                print(timestamp)
                if j % 3 == 0:
                    x_vector.append(value)
                if j % 3 == 1:
                    y_vector.append(value)
                if j % 3 == 2:
                    z_vector.append(value)
                    timestamp += time_between_samples
                    print(datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f'))
                    timestamp_list.append(
                        datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f'))
                print("%d: %s = %f%s" % (j, koords[j % 3], value, "\n" if (j % 3 == 2) else ""))
                j += 1

        print("%d Werte entpackt" % (j,))
        print(len(x_vector))
        return x_vector, y_vector, z_vector, timestamp_list

    def process_sensor_data_10(self, bytes, scale, rate):
        runtime = time.time() - self.start_time
        j = 0
        pos = 0
        koords = ["\nx", "y", "z"]

        x_vector = list()
        y_vector = list()
        z_vector = list()
        timestamp_list = list()
        time_between_samples = 1 / rate

        if (scale == 2):
            print("Scale: 2G")
            faktor = 4 / (64 * 1000)
        elif (scale == 4):
            print("Scale: 4G")
            faktor = 8 / (64 * 1000)
        elif (scale == 8):
            print("Scale: 8G")
            faktor = 16 / (64 * 1000)
        elif (scale == 16):
            print("Scale: 16G")
            faktor = 48 / (64 * 1000)

        while (pos < len(bytes)):
            print("Timestamp: %s" % hexlify(bytes[pos + 7:pos:-1]))
            t = bytes[pos:pos + 8]
            inv_t = t[::-1]
            timestamp = int(hexlify(inv_t), 16) / 1000

            pos += 8

            for i in range(24):
                value = bytes[pos] & 0xc0
                value |= (bytes[pos] & 0x3f) << 10
                pos += 1
                value |= (bytes[pos] & 0xc0) << 2
                if (value & 0x8000 == 0x8000):
                    # negative Zahl
                    # 16Bit Zweierkomplement zurückrechnen
                    value = value ^ 0xffff
                    value += 1
                    # negieren
                    value = -value
                value *= faktor
                if j % 3 == 0:
                    x_vector.append(value)
                if j % 3 == 1:
                    y_vector.append(value)
                if j % 3 == 2:
                    timestamp += time_between_samples
                    timestamp_list.append(
                        datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f'))
                    z_vector.append(value)
                print("%d: %s = %f%s" % (j, koords[j % 3], value, "\n" if (j % 3 == 2) else ""))
                j += 1
                value = (bytes[pos] & 0x30) << 2
                value |= (bytes[pos] & 0x0f) << 12
                pos += 1
                value |= (bytes[pos] & 0xf0) << 4
                if (value & 0x8000 == 0x8000):
                    # negative Zahl
                    # 16Bit Zweierkomplement zurückrechnen
                    value = value ^ 0xffff
                    value += 1
                    # negieren
                    value = -value
                value *= faktor
                if j % 3 == 0:
                    x_vector.append(value)
                if j % 3 == 1:
                    y_vector.append(value)
                if j % 3 == 2:
                    timestamp += time_between_samples
                    timestamp_list.append(
                        datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f'))
                    z_vector.append(value)
                print("%d: %s = %f%s" % (j, koords[j % 3], value, "\n" if (j % 3 == 2) else ""))
                j += 1
                value = (bytes[pos] & 0x0c) << 4
                value |= (bytes[pos] & 0x03) << 14
                pos += 1
                value |= (bytes[pos] & 0xfc) << 6
                if (value & 0x8000 == 0x8000):
                    # negative Zahl
                    # 16Bit Zweierkomplement zurückrechnen
                    value = value ^ 0xffff
                    value += 1
                    # negieren
                    value = -value
                value *= faktor
                if j % 3 == 0:
                    x_vector.append(value)
                if j % 3 == 1:
                    y_vector.append(value)
                if j % 3 == 2:
                    timestamp += time_between_samples
                    timestamp_list.append(
                        datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f'))
                    z_vector.append(value)
                print("%d: %s = %f%s" % (j, koords[j % 3], value, "\n" if (j % 3 == 2) else ""))
                j += 1
                value = (bytes[pos] & 0x03) << 6
                pos += 1
                value |= (bytes[pos]) << 8
                pos += 1
                if (value & 0x8000 == 0x8000):
                    # negative Zahl
                    # 16Bit Zweierkomplement zurückrechnen
                    value = value ^ 0xffff
                    value += 1
                    # negieren
                    value = -value
                value *= faktor
                if j % 3 == 0:
                    x_vector.append(value)
                if j % 3 == 1:
                    y_vector.append(value)
                if j % 3 == 2:
                    timestamp += time_between_samples
                    timestamp_list.append(
                        datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f'))

                    z_vector.append(value)
                print("%d: %s = %f%s" % (j, koords[j % 3], value, "\n" if (j % 3 == 2) else ""))
                j += 1
        print((j / runtime))
        print("%d Werte entpackt" % (j,))
        print(len(x_vector))
        return x_vector, y_vector, z_vector, timestamp_list

    def process_sensor_data_12(self, bytes, scale, rate):
        j = 0
        pos = 0
        koords = ["x", "y", "z"]
        x_vector = list()
        y_vector = list()
        z_vector = list()
        timestamp_list = list()
        time_between_samples = 1 / rate

        if (scale == 2):
            print("Scale: 2G")
            faktor = 1 / (16 * 1000)
        elif (scale == 4):
            print("Scale: 4G")
            faktor = 2 / (16 * 1000)
        elif (scale == 8):
            print("Scale: 8G")
            faktor = 4 / (16 * 1000)
        elif (scale == 16):
            print("Scale: 16G")
            faktor = 12 / (16 * 1000)

        while (pos < len(bytes)):
            print("Timestamp: %s" % hexlify(bytes[pos + 7:pos:-1]))
            t = bytes[pos:pos + 8]
            inv_t = t[::-1]
            timestamp = int(hexlify(inv_t), 16) / 1000
            pos += 8

            for i in range(48):
                value = bytes[pos] & 0xf0
                value |= (bytes[pos] & 0x0f) << 12
                pos += 1
                value |= (bytes[pos] & 0xf0) << 4
                if (value & 0x8000 == 0x8000):
                    # negative Zahl
                    # 16Bit Zweierkomplement zurückrechnen
                    value = value ^ 0xffff
                    value += 1
                    # negieren
                    value = -value
                value *= faktor
                if j % 3 == 0:
                    x_vector.append(value)
                if j % 3 == 1:
                    y_vector.append(value)
                if j % 3 == 2:
                    timestamp_list.append(
                        datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f'))
                    timestamp += time_between_samples
                    z_vector.append(value)
                print("%d: %s = %f%s" % (j, koords[j % 3], value, "\n" if (j % 3 == 2) else ""))
                j += 1
                value = (bytes[pos] & 0x0f) << 4
                pos += 1
                value |= bytes[pos] << 8
                pos += 1
                if (value & 0x8000 == 0x8000):
                    # negative Zahl
                    # 16Bit Zweierkomplement zurückrechnen
                    value = value ^ 0xffff
                    value += 1
                    # negieren
                    value = -value
                value *= faktor
                if j % 3 == 0:
                    x_vector.append(value)
                if j % 3 == 1:
                    y_vector.append(value)
                if j % 3 == 2:
                    timestamp += time_between_samples
                    timestamp_list.append(
                        datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f'))
                    z_vector.append(value)
                print("%d: %s = %f%s" % (j, koords[j % 3], value, "\n" if (j % 3 == 2) else ""))
                j += 1

        print("%d Werte entpackt" % (j,))
        return x_vector, y_vector, z_vector, timestamp_list

    ##%% Set configurations of the sensor
    def set_config_sensor(self, specific_mac="", sampling_rate='FF', sampling_resolution='FF', measuring_range='FF', divider="1"):
        """Check if arguments are given and valid"""
        if sampling_rate == 'FF':
            hex_sampling_rate = 'FF'
        elif sampling_rate in SamplingRate._value2member_map_:
            hex_sampling_rate = SamplingRate(sampling_rate).name[1:]
        else:
            self.logger.warning("Wrong sampling rate")
            hex_sampling_rate = 'FF'
        """Check if arguments are given and valid"""
        if sampling_resolution == 'FF':
            hex_sampling_resolution = 'FF'
        elif sampling_resolution in SamplingResolution._value2member_map_:
            hex_sampling_resolution = SamplingResolution(sampling_resolution).name[1:]
        else:
            self.logger.warning("Wrong sampling resolution")
            hex_sampling_resolution = 'FF'
        """Check if arguments are given and valid"""
        if measuring_range == 'FF':
            hex_measuring_range = 'FF'
        elif measuring_range in MeasuringRange._value2member_map_:
            hex_measuring_range = MeasuringRange(measuring_range).name[1:]
        else:
            hex_measuring_range = 'FF'
        if divider == '1':
            hex_divider = '01'
        else:
            hex_divider= str(divider)
        """Exit function if no changes are made"""
        if (hex_sampling_rate == "FF") and (hex_sampling_resolution == "FF") and (hex_measuring_range == "FF")and(hex_divider=="1"):
            self.logger.warning("No changes are made. Try again with correct values")
            return False
        """Create command string and send it to targets"""
        command_string = "FAFA06" + hex_sampling_rate + hex_sampling_resolution + hex_measuring_range + "FFFFFF"+hex_divider+"00"

        self.success = False
        self.work_loop(macs=specific_mac, command=command_string)

        if self.success:
            print("Config set")
        else:
            logging.error("Config set")
            print("Config set")

    """Get configuration from sensors"""
    def get_config_from_sensor(self, specific_mac=""):
        command_string = "FAFA070000000000000000"
        self.success = False
        self.work_loop(macs=specific_mac, command=command_string)
        if self.success:
            print("Config read")
        else:
            logging.error("Config not read")
            print("Config not read")

    """Get time from sensors"""

    def get_time_from_sensor(self, specific_mac=""):
        command_string = "FAFA090000000000000000"
        self.success = False
        self.work_loop(macs=specific_mac, command=command_string)
        if self.success:
            print("Time read")
        else:
            logging.error("Time  read")
            print("Time  read")


    """Set sensor time"""

    def set_sensor_time(self, specific_mac=""):
        """Time has to be little endian and 16 bit long"""
        timestamp = struct.pack("<Q", int(time.time() * 1000)).hex()
        print(time.time())
        print(timestamp)

        command_string = "FAFA08" + timestamp
        print(command_string)
        self.success = False
        self.work_loop(macs=specific_mac, command=command_string)
        if self.success:
            print("Time set")
        else:
            logging.error("Time  set")
            print("Time  set")

    ##%% region error messages

    def ri_error_to_string(self, error):
        result = set()
        # print(error)
        if error == 0:
            Log_SensorGatewayBleak.info("RD_SUCCESS")
            result.add("RD_SUCCESS")
            self.success = True
        else:
            if error & (1 << 0):
                Log_SensorGatewayBleak.error("RD_ERROR_INTERNAL")
                result.add("RD_ERROR_INTERNAL")
            if error & (1 << 1):
                Log_SensorGatewayBleak.error("RD_ERROR_NO_MEM")
                result.add("RD_ERROR_NO_MEM")
            if error & (1 << 2):
                Log_SensorGatewayBleak.error("RD_ERROR_NOT_FOUND")
                result.add("RD_ERROR_NOT_FOUND")
            if error & (1 << 3):
                Log_SensorGatewayBleak.error("RD_ERROR_NOT_SUPPORTED")
                result.add("RD_ERROR_NOT_SUPPORTED")
            if error & (1 << 4):
                Log_SensorGatewayBleak.error("RD_ERROR_INVALID_PARAM")
                result.add("RD_ERROR_INVALID_PARAM")
            if error & (1 << 5):
                Log_SensorGatewayBleak.error("RD_ERROR_INVALID_STATE")
                result.add("RD_ERROR_INVALID_STATE")
            if error & (1 << 6):
                Log_SensorGatewayBleak.error("RD_ERROR_INVALID_LENGTH")
                result.add("RD_ERROR_INVALID_LENGTH")
            if error & (1 << 7):
                Log_SensorGatewayBleak.error("RD_ERROR_INVALID_FLAGS")
                result.add("RD_ERROR_INVALID_FLAGS")
            if error & (1 << 8):
                Log_SensorGatewayBleak.error("RD_ERROR_INVALID_DATA")
                result.add("RD_ERROR_INVALID_DATA")
            if error & (1 << 9):
                Log_SensorGatewayBleak.error("RD_ERROR_DATA_SIZE")
                result.add("RD_ERROR_DATA_SIZE")
            if error & (1 << 10):
                Log_SensorGatewayBleak.error("RD_ERROR_TIMEOUT")
                result.add("RD_ERROR_TIMEOUT")
            if error & (1 << 11):
                Log_SensorGatewayBleak.error("RD_ERROR_NULL")
                result.add("RD_ERROR_NULL")
            if error & (1 << 12):
                Log_SensorGatewayBleak.error("RD_ERROR_FORBIDDEN")
                result.add("RD_ERROR_FORBIDDEN")
            if error & (1 << 13):
                Log_SensorGatewayBleak.error("RD_ERROR_INVALID_ADDR")
                result.add("RD_ERROR_INVALID_ADDR")
            if error & (1 << 14):
                Log_SensorGatewayBleak.error("RD_ERROR_BUSY")
                result.add("RD_ERROR_BUSY")
            if error & (1 << 15):
                Log_SensorGatewayBleak.error("RD_ERROR_RESOURCES")
                result.add("RD_ERROR_RESOURCES")
            if error & (1 << 16):
                Log_SensorGatewayBleak.error("RD_ERROR_NOT_IMPLEMENTED")
                result.add("RD_ERROR_NOT_IMPLEMENTED")
            if error & (1 << 16):
                Log_SensorGatewayBleak.error("RD_ERROR_SELFTEST")
                result.add("RD_ERROR_SELFTEST")
            if error & (1 << 18):
                Log_SensorGatewayBleak.error("RD_STATUS_MORE_AVAILABLE")
                result.add("RD_STATUS_MORE_AVAILABLE")
            if error & (1 << 19):
                Log_SensorGatewayBleak.error("RD_ERROR_NOT_INITIALIZED")
                result.add("RD_ERROR_NOT_INITIALIZED")
            if error & (1 << 20):
                Log_SensorGatewayBleak.error("RD_ERROR_NOT_ACKNOWLEDGED")
                result.add("RD_ERROR_NOT_ACKNOWLEDGED")
            if error & (1 << 21):
                Log_SensorGatewayBleak.error("RD_ERROR_NOT_ENABLED")
                result.add("RD_ERROR_NOT_ENABLED")
            if error & (1 << 31):
                Log_SensorGatewayBleak.error("RD_ERROR_FATAL")
                result.add("RD_ERROR_FATAL")
        return result
