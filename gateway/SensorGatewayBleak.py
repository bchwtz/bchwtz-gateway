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
import yaml
# import async_timeout
import configparser

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
# Log_SensorGatewayBleak.setLevel(logging.INFO)

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
        self.heartbeat = 8
        self.killTask=""
        self.stopEvent = Event_ts()
        self.delta = 'Time'
        self.start_time = 'Time'
        self.end_time = 'Time'
        
        # Constructor of the class RuuviTagAccelerometerCommunicationBleak
        self.client = 'TestClient'
        
        # Create a child of the previously created logger 'SensorGatewayBleak'
        self.logger = logging.getLogger('SensorGatewayBleak.ClassRuuvi')
        # self.logger.info('Initialize child logger ClassRuuvi')
        # self.logger.info('Start constructor')

        # MAC - list of addresses of the bluetooth devices
        self.mac = []

        # Data recieved by the bluetooth devices
        self.data = []

        self.sensor_data=[]
        # Variable for bandwidth calculation
        self.start_time = time.time()

        # Auxiliary Variables
        self.success = ""

        # Search for asyncio loops that are already running
        self.my_loop = asyncio.get_event_loop()
        
        # self.logger.info('Searching for running loops completed')
        # #self.__handle_config_file(Mode="INIT")
        # self.logger.info('Class object successfully initialized!')
        
    def read_RuuviTag_conf(self, abs_path = "gateway/Ruuvi_commands.yml"):
        with open(abs_path, "r") as ymlfile:
            ruuvi_commands = yaml.load(ymlfile)
        self.ruuvi_commands = ruuvi_commands
    
    # def __exit__(self):
    def activate_debug_logger(self):
        Log_SensorGatewayBleak.setLevel(logging.INFO)
        console_handler.setLevel(logging.INFO)

    def deactivate_debug_logger(self):
        Log_SensorGatewayBleak.setLevel(logging.WARNING)
        console_handler.setLevel(logging.WARNING)

    #     self.data = []
    #     self.logger.info('Reset self.data !')
    #     self.mac = []
    #     self.logger.info('Reset self.mac')
    #     # Do we need a "Reset Tag"-Command to get the Tag in a safe state?
    
    def Handle_Config_File(self, Mode = ""):
        # [[Tag1,MAC1],...,[TagN,MACN]]
        ErrFlag = 0
        if Mode == "Read" or Mode == "INIT":
            try:
                Read_Parser = configparser.ConfigParser()
                Read_Parser.read('TagList.ini')
                for tag in Read_Parser["Tags"]:
                    self.TagList.append([tag, Read_Parser.get("Tag", tag)])
            except:
                ErrFlag = 1
                print("Could not read TagList.ini")
        elif Mode == "INIT" and ErrFlag ==1:
            Write_Parser = configparser.ConfigParser()
            Write_Parser.add_section("Tags")
            cfgfile = open("TagList.ini","w")
            Write_Parser.write(cfgfile)
            cfgfile.close()
            self.TagList=[]
        elif Mode == "WRITE":
            Write_Parser = configparser.ConfigParser()
            Write_Parser.add_section("Tags")
            for tag in self.TagList:
                Write_Parser.set("Tags", tag[0] , tag[1])
            cfgfile = open("TagList.ini","w")
            Write_Parser.write(cfgfile)
            cfgfile.close()
            
    """    Check if mac address is a valid mac address    """
    async def killswitch(self):
        self.logger.info("Start timeout function")
        while time.time()-self.start_time < 10 :
            self.logger.warning("Timeout timer running {}".format(time.strftime("%H:%M:%S",time.localtime(self.start_time))))
            await asyncio.sleep(1)
        try:
            self.stopEvent.set()
        except:
            pass


    def __handle_config_file(self, Mode=""):
        # [[Tag1,MAC1],...,[TagN,MACN]]
        ErrFlag = 0
        if Mode == "Read" or Mode == "INIT":
            try:
                Read_Parser = configparser.ConfigParser()
                Read_Parser.read('TagList.ini')
                for tag in Read_Parser["Tags"]:
                    self.TagList.append([tag, Read_Parser.get("Tag", tag)])
            except:
                ErrFlag = 1
                self.logger.warning("Could not read ini")
                pass
        if Mode == "INIT" and ErrFlag == 1:
            Write_Parser = configparser.ConfigParser()
            Write_Parser.add_section("Tags")
            cfgfile = open("TagList.ini", "w")
            Write_Parser.write(cfgfile)
            cfgfile.close()
            self.TagList = []
        if Mode == "WRITE":
            Write_Parser = configparser.ConfigParser()
            Write_Parser.add_section("Tags")
            for tag in self.TagList:
                Write_Parser.set("Tags", tag[0], tag[1])
            cfgfile = open("TagList.ini", "w")
            Write_Parser.write(cfgfile)
            cfgfile.close()

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
        if not isinstance(macs, list):
            self.logger.info("Search custom MAC-Adress {}".format(macs))
            if macs != "":
                # self.__check_mac_address()
                # taskobj = self.my_loop.create_task(self.__check_mac_address(macs))
                # self.my_loop.run_until_complete(self.__check_mac_address())
                # print(taskobj.result())
                if not self.__check_mac_address(macs):
                    return
            else:
                self.taskobj = self.my_loop.create_task(self.find_tags())
                self.my_loop.run_until_complete(self.taskobj)
        try:
            self.taskobj = self.my_loop.create_task(self.connect_to_mac_command(command_string=command, specific_mac=macs))
            self.my_loop.run_until_complete(self.taskobj)
            #self.success = True
        except Exception as e:
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

            self.logger.info("Send {} to MAC {} ".format(command_string,i))
            try:
                async with BleakClient(i) as client:
                    # Send the command (Wait for Response must be True)
                    await client.start_notify(UART_RX, self.handle_sensor_commands)
                    await client.write_gatt_char(UART_TX,
                                                 bytearray.fromhex(command_string), True)
                    self.logger.info('Message send to MAC: %s' % (i))
                    await self.stopEvent.wait()
                    await client.stop_notify(UART_RX)
                    self.stopEvent.clear()
                    self.logger.info('Stop notify: %s' % (i))
            except Exception as e:
                self.logger.warning('Connection faild at MAC %s' % (i))
                self.logger.error("Error: {}".format(e))

            self.logger.info("Task done connect_to_mac_command!")

            # Reciving and Handling of Callbacks

    # Main Function for sensordatalogging
    async def connect_to_mac(self, i, readCommand):
        try:
            """Timeout after 60 Seconds"""
            # with async_timeout.timeout(60):
            self.logger.info("Send {} to MAC {} ".format(readCommand,i))
            async with BleakClient(i) as client:
                # Send the command (Wait for Response must be True)
                self.client = client
                await client.start_notify(UART_RX, self.handle_data)
                await client.write_gatt_char("6e400002-b5a3-f393-e0a9-e50e24dcca9e", bytearray.fromhex(readCommand),
                                             True)
                self.logger.info('Message send to MAC: %s' % (i))
                #self.my_loop.create_task(self.killswitch())
                self.start_time = time.time()
                self.logger.info("Set Processtimer")
                await self.killswitch()
                self.logger.info("Killswitch starts monitoring")
                await self.stopEvent.wait()
                self.logger.warning("Abort workloop Task via Killswtch after timeout!")
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

        if value[0] == 0x4A or value[0] == 0x21:
            self.logger.info("Received: %s" % hexlify(value))
            status_string=str(self.ri_error_to_string(value[3]), )
            self.sensor_data={"Status":status_string}
            self.logger.info("Status: %s" % status_string)
            if len(value) == 4:
                self.stopEvent.set()
            elif value[2] == 0x09:
                self.logger.info("Received time: %s" % hexlify(value[:-9:-1]))
                recieved_time=time.strftime('%D %H:%M:%S', time.gmtime(int(hexlify(value[:-9:-1]), 16) / 1000))
                self.logger.info(recieved_time)
                self.sensor_data={"Received time": recieved_time}
                self.stopEvent.set()
            elif value[0] == 0x4a and value[3] == 0x00:
                sample_rate=""
                if value[4] == 201:
                    self.logger.info("Samplerate: 400 Hz")
                    sample_rate=400
                else:
                    self.logger.info("Samplerate:    %d Hz" % value[4])
                    sample_rate=int(value[4])
                # print("Samplerate:    %d Hz" % value[4])
                self.sensor_data={"Samplerate": sample_rate,
                                  "Resolution":int(value[5]),
                                  "Scale":int(value[6]),
                                  "DSP function": int(value[7]),
                                  "DSP parameter": int(value[8]),
                                  "Mode":  "%x" % value[9]
                                  }
                self.logger.info("Resolution:    %d Bits" % (int(value[5])))
                self.logger.info("Scale:         %d G" % value[6])
                self.logger.info("DSP function:  %x" % value[7])
                self.logger.info("DSP parameter: %x" % value[8])
                self.logger.info("Mode:          %x" % value[9])

                if value[10] > 1:
                    self.sensor_data={"Frequency divider": int(value[10])}
                    self.logger.info("Frequency divider: %d" % value[10])

                self.stopEvent.set()

        elif value[0] == 0xfb and value[1] == 0x0d:
            self.logger.info("Received: %s" % hexlify(value))
            message_status = value[2]
            logging_status = value[3]
            ringbuffer_start = value[4]
            ringbuffer_end = value[5]
            ringbuffer_size = value[6]
            valid_records = value[7] | (value[8] << 8)
            dirty_records = value[9] | (value[10] << 8)
            words_reserved = value[11] | (value[12] << 8)
            words_used = value[13] | (value[14] << 8)
            largest_contig = value[15] | (value[16] << 8)
            freeable_words = value[17] | (value[18] << 8)
            self.sensor_data={"Message Status": "%s"%(self.ri_error_to_string(message_status)),
                              "Last Status": "%s"%(self.ri_error_to_string(logging_status)),
                              "Ringbuffer start": ringbuffer_start,
                              "Ringbuffer end": ringbuffer_end,
                              "Ringbuffer size": ringbuffer_size,
                              "Valid records":valid_records,
                              "Dirty records":dirty_records,
                              "Words reserved":words_reserved,
                              "Words used":words_used,
                              "Largest continuos":largest_contig,
                              "Freeable words":freeable_words
                              }
            self.logger.info("Message Status %s" % (str(self.ri_error_to_string(message_status)),))
            self.logger.info("Last Status %s" % (str(self.ri_error_to_string(logging_status)),))
            self.logger.info("Ringbuffer start %d" % (ringbuffer_start,))
            self.logger.info("Ringbuffer end %d" % (ringbuffer_end,))
            self.logger.info("Ringbuffer size %d" % (ringbuffer_size,))
            self.logger.info("Valid records %d" % (valid_records,))
            self.logger.info("Dirty records %d" % (dirty_records,))
            self.logger.info("Words reserved %d" % (words_reserved,))
            self.logger.info("Words used %d" % (words_used,))
            self.logger.info("Largest continuos %d" % (largest_contig,))
            self.logger.info("Freeable words %d\n" % (freeable_words,))
            self.stopEvent.set()

    # ------------------------Activate/Deactivate Logging----------------------
    def activate_logging_at_sensor(self, specific_mac=""):
        # """
        # Loop funktion zum aufrufen in eigene Funktion, die activate Logging aufruft.
        # Async
        # """
        # command_string = "FAFA0a0100000000000000"
        command_string = "4a4a080100000000000000"
        self.success = False
        self.work_loop(macs=specific_mac, command=command_string)
        if self.success:
            self.logger.info("Logging activated")
        else:
            self.logger.error("Logging is not activated")

    def deactivate_logging_at_sensor(self, specific_mac=""):
        self.success = False
        command_string = "4a4a080000000000000000"
        self.work_loop(macs=specific_mac, command=command_string)
        if self.success:
            self.logger.info("Logging deactivated")
        else:
            self.logger.error("Logging not deactivated")

    # ----------------------------Acceleration Logging-------------------------
    def get_acceleration_data(self, specific_mac=""):
        # global readAllString #? Wofür ist dieser String
        self.data = []
        self.ConnectionError = False
        readAllString = "4a4a110100000000000000"
        # my_loop = asyncio.get_running_loop()
        # This is a DEBUG Funktion to Connect to a specific tag
        if specific_mac != "":
            if re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", specific_mac.lower()):
                mac = [specific_mac]
            else:
                self.logger.error('Mac address is not valid' + specific_mac)
                return
        else:
            self.logger.info('Try to get acceleration data from tags')
            mac = self.mac
            # mac = self.find_tags_mac()

        """Read acceleration samples for each sensor"""
        for i in mac:
            global sensordaten
            sensordaten = bytearray()
            taskobj = self.my_loop.create_task(self.connect_to_mac(i, readAllString))
            self.my_loop.run_until_complete(taskobj)

        return self.data

    # --------------------------------handle data--------------------------------

    """Handle received data"""

    async def handle_data(self, handle, value):
        """
        handle -- integer, characteristic read handle the data was received on
        value -- bytearray, the data returned in the notification
        """
        # self.heartbeat=20
        # if time.time()-self.start_time >20:
        #     self.logger.warn("Timout while getting acceleration data")
        #     self.stopEvent.set()
        if value[0] == 0x11:
            # Daten
            sensordaten.extend(value[1:])
            self.start_time = time.time()
            self.logger.debug("Received data block: %s" % hexlify(value[1:]))
            # Marks end of data stream
        elif value[0] == 0x4a and value[3] == 0x00:
            self.start_time = time.time()
            self.end_time = time.time()
            print(len(sensordaten))
            self.delta = len(sensordaten) / (self.end_time - self.start_time)

            self.logger.debug('Bandwidth : {} Bytes/Second'.format(self.delta))
            self.stopEvent.set()
            # Status
            self.logger.debug("Status: %s" % str(self.ri_error_to_string(value[3])))

            crc = value[12:14];
            self.logger.debug("Received CRC: %s" % hexlify(crc))

            # CRC validation
            #print(sensordaten)
            ourcrc = crcfun(sensordaten)
            #print("Recalculated CRC: %x" % ourcrc)

            print("Received %d bytes" % len(sensordaten))
            #print(hexlify(crc))
            if hexlify(crc) == bytearray():
                self.logger.info("No crc received")
                return None

            if int(hexlify(crc), 16) != ourcrc:
                self.logger.warning("CRC are unequal")
                return None


            timeStamp = hexlify(sensordaten[7::-1])

            # Start data
            if (value[5] == 12):
                # 12 Bit
                self.logger.info("Start processing reveived data with process_sensor_data_12")
                AccelorationData = self.process_sensor_data_12(sensordaten, value[6], value[4])
            elif (value[5] == 10):
                # 10 Bit
                self.logger.info("Start processing reveived data with process_sensor_data_10")
                AccelorationData = self.process_sensor_data_10(sensordaten, value[6], value[4])
            elif (value[5] == 8):
                # 8 Bit
                self.logger.info("Start processing reveived data with process_sensor_data_10")
                AccelorationData = self.process_sensor_data_8(sensordaten, value[6], value[4])
            else:
                print("Unknown Resolution")
            if AccelorationData != None:
                self.logger.info("Run in Funktion AccelorationData != None")
                self.data.append([list(map(list, zip(AccelorationData[0], AccelorationData[1], AccelorationData[2],
                                                     AccelorationData[3])))])
                #print(self.data)


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
            self.logger.info("Scale: 2G")
            faktor = 16 / (256 * 1000)
        elif (scale == 4):
            self.logger.info("Scale: 4G")
            faktor = 32 / (256 * 1000)
        elif (scale == 8):
            self.logger.info("Scale: 8G")
            faktor = 64 / (256 * 1000)
        elif (scale == 16):
            self.logger.info("Scale: 16G")
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

                self.logger.info(timestamp)
                if j % 3 == 0:
                    x_vector.append(value)
                if j % 3 == 1:
                    y_vector.append(value)
                if j % 3 == 2:
                    z_vector.append(value)
                    timestamp += time_between_samples
                    self.logger.info(datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f'))
                    timestamp_list.append(
                        datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f'))
                self.logger.info("%d: %s = %f%s" % (j, koords[j % 3], value, "\n" if (j % 3 == 2) else ""))
                j += 1

        self.logger.info("%d Werte entpackt" % (j,))
        self.logger.info(len(x_vector))
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
            self.logger.info("Scale: 2G")
            faktor = 4 / (64 * 1000)
        elif (scale == 4):
            self.logger.info("Scale: 4G")
            faktor = 8 / (64 * 1000)
        elif (scale == 8):
            self.logger.info("Scale: 8G")
            faktor = 16 / (64 * 1000)
        elif (scale == 16):
            self.logger.info("Scale: 16G")
            faktor = 48 / (64 * 1000)

        while (pos < len(bytes)):
            self.logger.info("Timestamp: %s" % hexlify(bytes[pos + 7:pos:-1]))
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
                self.logger.info("%d: %s = %f%s" % (j, koords[j % 3], value, "\n" if (j % 3 == 2) else ""))
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
                self.logger.info("%d: %s = %f%s" % (j, koords[j % 3], value, "\n" if (j % 3 == 2) else ""))
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
                self.logger.info("%d: %s = %f%s" % (j, koords[j % 3], value, "\n" if (j % 3 == 2) else ""))
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
                self.logger.info("%d: %s = %f%s" % (j, koords[j % 3], value, "\n" if (j % 3 == 2) else ""))
                j += 1
        self.logger.info((j / runtime))
        self.logger.info("%d Werte entpackt" % (j,))
        self.logger.info(len(x_vector))
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
            self.logger.info("Scale: 2G")
            faktor = 1 / (16 * 1000)
        elif (scale == 4):
            self.logger.info("Scale: 4G")
            faktor = 2 / (16 * 1000)
        elif (scale == 8):
            self.logger.info("Scale: 8G")
            faktor = 4 / (16 * 1000)
        elif (scale == 16):
            self.logger.info("Scale: 16G")
            faktor = 12 / (16 * 1000)

        while (pos < len(bytes)):
            self.logger.info("Timestamp: %s" % hexlify(bytes[pos + 7:pos:-1]))
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
                self.logger.info("%d: %s = %f%s" % (j, koords[j % 3], value, "\n" if (j % 3 == 2) else ""))
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
                self.logger.info("%d: %s = %f%s" % (j, koords[j % 3], value, "\n" if (j % 3 == 2) else ""))
                j += 1

        self.logger.info("%d Werte entpackt" % (j,))
        return x_vector, y_vector, z_vector, timestamp_list

    ##%% Set configurations of the sensor
    def set_config_sensor(self, specific_mac="", sampling_rate='FF', sampling_resolution='FF', measuring_range='FF',
                          divider="FF"):
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
        if divider == 'FF':
            hex_divider = 'FF'
        else:
            hex_divider = str(divider)
        """Exit function if no changes are made"""
        if (hex_sampling_rate == "FF") and (hex_sampling_resolution == "FF") and (hex_measuring_range == "FF") and (
                hex_divider == "FF"):
            self.logger.warning("No changes are made. Try again with correct values")
            return False
        """Create command string and send it to targets"""
        command_string = "4a4a02" + hex_sampling_rate + hex_sampling_resolution + hex_measuring_range + "FFFFFF" + hex_divider + "00"

        self.success = False
        self.work_loop(macs=specific_mac, command=command_string)

        if self.success:
            self.logger.info("Config set")
        else:
            logging.error("Config set")


    """Get configuration from sensors"""

    def get_config_from_sensor(self, specific_mac=""):
        command_string = "4a4a030000000000000000"
        self.success = False
        self.work_loop(macs=specific_mac, command=command_string)
        if self.success:
            self.logger.info("Config read")
            return self.sensor_data
        else:
            logging.error("Config not read")


    """Get time from sensors"""

    def get_time_from_sensor(self, specific_mac=""):
        command_string = "2121090000000000000000"
        self.success = False
        self.work_loop(macs=specific_mac, command=command_string)
        if self.success:
            self.logger.info("Time read")
            return self.sensor_data
        else:
            logging.error("Time  read")


    """Set sensor time"""

    def set_sensor_time(self, specific_mac=""):
        """Time has to be little endian and 16 bit long"""
        timestamp = struct.pack("<Q", int(time.time() * 1000)).hex()
        self.logger.info(time.time())
        self.logger.info(timestamp)

        command_string = "212108" + timestamp
        self.logger.info(command_string)
        self.success = False
        self.work_loop(macs=specific_mac, command=command_string)
        if self.success:
            self.logger.info("Time set")
        else:
            logging.error("Time  set")


    def get_flash_statistic(self, specific_mac=""):
        # """
        # Loop funktion zum aufrufen in eigene Funktion, die activate Logging aufruft.
        # Async
        # """

        command_string = "FAFA0d0000000000000000"
        self.success = False
        self.work_loop(macs=specific_mac, command=command_string)
        if self.success:
            self.logger.info("flash statistics read")
            return self.sensor_data
        else:
            logging.error("flash statistics is not read")


    def get_logging_status(self, specific_mac=""):
        # """
        # Loop funktion zum aufrufen in eigene Funktion, die activate Logging aufruft.
        # Async
        # """

        command_string = "4A4A090000000000000000"
        self.success = False
        self.work_loop(macs=specific_mac, command=command_string)
        if self.success:
            self.logger.info("Logging status read")
            return self.sensor_data
        else:
            logging.error("Logging status is not read")

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
