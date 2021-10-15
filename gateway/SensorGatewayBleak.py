"""
The gateway has three different tasks:

    Manipulate the state of one or more sensors via control messages
    Receive acceleration data from one or more sensors, parse and store them
    Logging Bluetooth advertisements from sensors

For the first two tasks there is the “SensorGatewayBleak” library.
Another module is used to log the advertisements. Both are written in python.
"""

# %% libraries

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
from functools import partial
# import async_timeout
import configparser
from gateway.MessageObjects import return_values_from_sensor, send_deactivate_logging_object,send_get_senor_time_object,send_get_acceleration_data_object,send_activate_logging_object,send_set_config_object, send_set_sensor_time_object,send_get_config_object,send_get_flash_statistics_object, send_get_logging_status_object
from gateway.SensorConfigEnum import SamplingRate, SamplingResolution,MeasuringRange

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


# # %%region enums for sensor config
#
# class SamplingRate(Enum):
#     x01 = 1
#     x0A = 10
#     x19 = 25
#     x32 = 50
#     x64 = 100
#     xC8 = 200
#     xC9 = 400
#
#
# class SamplingResolution(Enum):
#     """
#     For validation of the arguments set in set_config_sensor.
#     """
#     x08 = 8
#     x0A = 10
#     x0C = 12
#
#
# class MeasuringRange(Enum):
#     """
#     For validation of the arguments set in set_config_sensor.
#     """
#     x02 = 2
#     x04 = 4
#     x08 = 8
#     x10 = 16


# %% Class Async-Events
# Thread Safe Event Class
class Event_ts(asyncio.Event):
    """
    Custom event loop class for the RuuviTagAccelerometerCommunicationBleak.
    """
    def clear(self):
        self._loop.call_soon_threadsafe(super().clear)

    def set(self):
        self._loop.call_soon_threadsafe(super().set)


# %% Class RuuviTagAccelerometerCommunicationBleak----------------------------
class RuuviTagAccelerometerCommunicationBleak(Event_ts):
    """ This class represents the center of the sensor communication. It
    sends commands to the RuuviTag and handles the incomming trafic. To
    communicate with the sensors, the bleak and asyncio libraries are required.
    """
    def __init__(self):
        """
        Constructor mesthod of the class RuuviTagAccelerometerCommunicationBleak.

        :returns:
            None.

        """
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

        # MAC - list of addresses of the bluetooth devices
        self.mac = []

        # Data recieved by the bluetooth devices
        self.data = []

        self.sensor_data=[]
        # Variable for bandwidth calculation
        self.start_time = time.time()
        self.notification_done=True

        # Auxiliary Variables
        self.success = ""

        # Search for asyncio loops that are already running
        self.my_loop = asyncio.get_event_loop()
        self.current_mac=""

        # #self.__handle_config_file(Mode="INIT")


    def activate_debug_logger(self):
        """
        This function changes the level of the logger to level INFO.

        :returns:
            None

        """
        Log_SensorGatewayBleak.setLevel(logging.INFO)
        console_handler.setLevel(logging.INFO)


    def deactivate_debug_logger(self):
        """
        This function changes the level of the logger to level WARNING.

        :returns:
            None

        """
        Log_SensorGatewayBleak.setLevel(logging.WARNING)
        console_handler.setLevel(logging.WARNING)


    async def killswitch(self):
        """
        This funcion handels communication timeouts if a sensor gets out of
        range while transfering the data. So far, this funktion is the safest way
        to raise/handle a timeout error, while processing the code asyncronous.

        :returns:
            If an timout is raised, a log notification will appear in the kernel

        """
        self.logger.info("Start timeout function")
        while time.time()-self.start_time < 2 :
            self.logger.warning("Timeout timer running {}".format(time.strftime("%H:%M:%S",time.localtime(self.start_time))))
            await asyncio.sleep(1)
        try:
            self.stopEvent.set()
        except:
            pass
    async def killswitch_for_commands(self):
            self.logger.info("Start timeout function")
            while time.time() - self.start_time < 10:
                self.logger.warning(
                    "Timeout timer running {}".format(time.strftime("%H:%M:%S", time.localtime(self.start_time))))
                await asyncio.sleep(1)
                if self.notification_done:
                    self.notification_done = False
                    break
            try:
                self.stopEvent.set()
            except:
                pass


    def __handle_config_file(self, Mode=""):
        """
        This function will store some basic informations about the sensor such as
        Name and MAC-Address in an config.ini file. A distinction is made between
        three modes: 'READ', 'INIT' and 'WRITE'.

        :param arg1:
            Mode : keyword,str, optional
            DESCRIPTION: The default is "".

        :return:
            A config.ini will be created or updated.

        """
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
        """
        This funcion uses a regular expression to compare the MAC address of
        a bluetooth device with a valide variante of a RuuviTag MAC adress.

        :parameters:
            mac : str
            This parameter contains a specific MAC-Address

        :returns:
            There are two possible return statements. If the mac address is valid
            the funciton find_tags will be called with the mac address as parameter.
            If the mac address is not valid, an error message will raised.

        """
        if re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", mac.lower()):
            self.logger.info('MAC set to specific Mac-Address')
            return True
        else:
            self.logger.error("Mac is not valid!")
            return False


    def __validate_mac(self, devices):
        """
        This funcion updates the internal mac_list. If a MAC address passed the
        checked_mac_address process, it will extend the list 'mac'.

        :parameters:
            devices : dictionary {name, address}

        :returns:
            None.
        """
        tags_so_far = len(self.mac)
        for i in devices:
            self.logger.info('Device: %s with Address %s found!' % (i.name, i.address))
            if ("Ruuvi" in i.name) & (i.address not in self.mac):
                self.mac.append(i.address)
                self.logger.info('Device: %s with Address %s saved in MAC list!' % (i.name, i.address))
        tags_new = len(self.mac) - tags_so_far
        self.logger.info('%d new Ruuvi tags were found' % tags_new)


    def work_loop(self, macs="", command=""):
        """
        From this function, the command lines are transmitted to individual tags.
        For example, configurations can be made or individual parameters can be obtained

        :parameters:
            macs : str, optional
                DESCRIPTION. The default is "".
            command : str, optional
                DESCRIPTION. The default is "".

        :returns:
            None.

        """
        if not isinstance(macs, list):
            self.logger.info("Search custom MAC-Adress {}".format(macs))
            if macs != "":
                if not self.__check_mac_address(macs):
                    return
            else:
                self.taskobj = self.my_loop.create_task(self.find_tags())
                self.my_loop.run_until_complete(self.taskobj)
        try:
            self.taskobj = self.my_loop.create_task(self.connect_to_mac_command(command_string=command, specific_mac=macs))
            self.my_loop.run_until_complete(self.taskobj)
        except Exception as e:
            self.logger.error("Error while activate logging: {}".format(e))


    # -------------Find -> Connect -> Listen-Functions---------------------
    async def find_tags(self, mac=""):
        """
        The function searches for bluetooth devices nearby and passes the
        MAC addresses to the __validate_mac function.

        :parameters:
            mac : TYPE, optional
                The default is "".

        :returns:
            bool
                False : No Tags were found.
                True : At least one Tag was found nearby.

        """
        if mac != "":
            device = [await BleakScanner.find_device_by_address(mac)]
            self.__validate_mac(device)
        else:
            devices = await BleakScanner.discover(timeout=5.0)
            self.__validate_mac(devices)
        if len(self.mac) == 0:
            self.logger.warning("No RuuviTags were found.")
            return False
        return True


    async def connect_to_mac_command(self, command_string, specific_mac=""):

        """
        connect_to_mac_command gets called by the function work_loop. Its
        used to get or chang the Tag configurations.

        :parameters:
            command_string : str
                Specific comand for the bluetoothdevice.
            specific_mac : str, optional
                Specific MAC adress.

        :returns:
            Callbacks are passed to the handle_senson_comands.

        """
        if isinstance(specific_mac, list):
            mac = specific_mac
            print(mac)
        elif specific_mac != "":
            mac = [specific_mac]
        else:
            mac = self.mac
        for i in mac:

            self.logger.info("Send {} to MAC {} ".format(command_string,i))
            try:
                async with BleakClient(i) as client:
                    # Send the command (Wait for Response must be True)
                    await client.start_notify(UART_RX, partial(self.handle_sensor_commands, client))
                    await client.write_gatt_char(UART_TX,
                                                 bytearray.fromhex(command_string), True)
                    self.logger.info('Message send to MAC: %s' % (i))

                    self.start_time = time.time()
                    self.logger.info("Set Processtimer")
                    await self.killswitch_for_commands()
                    self.logger.info("Killswitch starts monitoring")
                    await self.stopEvent.wait()
                    self.logger.warning("Abort workloop Task via Killswtch after timeout!")
                    await client.stop_notify(UART_RX)
                    self.stopEvent.clear()
                    self.logger.info('Stop notify: %s' % (i))
                    self.logger.info("Task done connect_to_mac_command!")
            except Exception as e:
                self.logger.warning('Connection faild at MAC %s' % (i))
                self.logger.error("Error: {}".format(e))


    # Main Function for sensordatalogging
    async def connect_to_mac(self, i, readCommand):
        """
        Main function for sensor data logging.

        :parameters:
            i : list of mac adresses

            readCommand : str
                Specific comand for bluetoothdevice.

        :returns:
            None.

        """
        try:
            #Timeout after 60 Seconds
            self.logger.info("Send {} to MAC {} ".format(readCommand,i))
            async with BleakClient(i) as client:
                # Send the command (Wait for Response must be True)
                self.client = client
                await client.start_notify(UART_RX, self.handle_data)
                await client.write_gatt_char("6e400002-b5a3-f393-e0a9-e50e24dcca9e", bytearray.fromhex(readCommand),
                                             True)
                self.logger.info('Message send to MAC: %s' % (i))
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
    def handle_sensor_commands(self, client: BleakClient,sender: int, value: bytearray):
        """
        This function is called by the connect_to_mac_comand function.
        It handles the the incomming callbacks and saves it as log messages.

        :parameters:
            sender : int

            value : bytearray
                The data returned by the callbacks.

        :returns:
            None.

        """

        self.logger.info("handle_sensor_command called sender: {} and value {}".format(sender, value))

        if value[0] == 0x4A or value[0] == 0x21:
            message_return_value = return_values_from_sensor()
            self.logger.info("Received: %s" % hexlify(value))
            status_string=str(self.ri_error_to_string(value[3]), )
            self.logger.info("Status: %s" % status_string)
            if len(value) == 4:
                test=message_return_value.form_get_status(status=int(value[3]), mac=client.address)
                self.sensor_data.append([test.returnValue.__dict__])
                self.stopEvent.set()
                self.notification_done = True

            elif value[2] == 0x09:

                self.logger.info("Received time: %s" % hexlify(value[:-9:-1]))
                recieved_time=time.strftime('%D %H:%M:%S', time.gmtime(int(hexlify(value[:-9:-1]), 16) / 1000))
                self.logger.info(recieved_time)
                self.sensor_data.append([message_return_value.from_get_time(status=status_string, recieved_time=recieved_time,
                                                   mac=client.address).returnValue.__dict__])
                self.stopEvent.set()
                self.notification_done = True

            elif value[0] == 0x4a and value[3] == 0x00:
                sample_rate=""
                if value[4] == 201:
                    self.logger.info("Samplerate: 400 Hz")
                    sample_rate=400
                else:
                    self.logger.info("Samplerate:    %d Hz" % value[4])
                    sample_rate=int(value[4])
                recieved_config=message_return_value.from_get_config(status=status_string,sample_rate=sample_rate,resolution= int(value[5]),
                                                    scale=int(value[6]),dsp_function=int(value[7]), dsp_parameter=int(value[8]),
                                                    mode="%x"% value[9],divider=int(value[10]), mac=client.address)
                self.sensor_data.append([recieved_config.returnValue.__dict__])
                self.notification_done=True
                self.stopEvent.set()

        elif value[0] == 0xfb and value[1] == 0x0d:
            message_return_value = return_values_from_sensor()
            self.logger.info("Received: %s" % hexlify(value))
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
            recieved_flash_statistic=message_return_value.from_get_flash_statistics(
            logging_status=logging_status, ringbuffer_start=ringbuffer_start,
            ringbuffer_end=ringbuffer_end, ringbuffer_size=ringbuffer_size, valid_records=valid_records, dirty_records=dirty_records,
            words_reserved=words_reserved, words_used= words_used, largest_contig=largest_contig, freeable_words=freeable_words,
            mac=client.address)
            self.sensor_data.append([recieved_flash_statistic.returnValue.__dict__])
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
            self.notification_done = True

    # ------------------------Activate/Deactivate Logging----------------------
    def activate_logging_at_sensor(self,msg_object):
        """
        The “activate_logging_at_sensor()” function activates logging at all
        sensors in Bluetooth range of the gateway. It can also be used with a
        mac address as argument to activate the logging at a specific sensor.
        To activate the logging, the gateway sends a control acceleration logging
        message to the target sensor.
        The message content is `F0A 0xFA 0x0A 0x01`
        If Logging is already activated an error message will be received.

        :parameters:
            specific_mac : TYPE, optional
                The activate logging at sensor function can also be called to activate a
                specific_mac. The The default is "".

        :returns:
            Log message to kernel.

        """
        if isinstance(msg_object, send_activate_logging_object):
            self.success = False
            self.work_loop(macs=msg_object.mac, command=msg_object.command)
            if self.success:
                self.logger.info("Logging activated")
            else:
                self.logger.error("Logging is not activated")
            return self.sensor_data
        else:
            logging.error("%s is the wrong message object. "
                          "Use gateway.MessageObjects.send_activate_logging_object instead." % type(msg_object))


    def deactivate_logging_at_sensor(self, msg_object):
        """
        The “deactivate_logging_at_sensor()” function deactivates logging at
        all sensors in Bluetooth range. With a mac address as argument, a
        specific sensor can be deactivated. To deactivate the logging, the
        gateway sends a control acceleration logging message to the target sensor.
        The message content is 0xFA 0xFA 0x0A 0x00. Stopping the logging cause
        a deletion of all flash pages. If Logging is not activated an error
        message will be received.

        :parameters:
            specific_mac : TYPE, optional
                The `deactivate_logging_at_sensor` function can also be called to activate a
                specific_mac. The The default is "".

        :returns:
            Log message to kernel.

        """
        if isinstance(msg_object, send_deactivate_logging_object):
            self.success = False

            self.work_loop(macs=msg_object.mac, command=msg_object.command)
            if self.success:
                self.logger.info("Logging deactivated")
            else:
                self.logger.error("Logging not deactivated")
            return self.sensor_data
        else:
            logging.error("%s is the wrong message object. "
                          "Use gateway.MessageObjects.send_deactivate_logging_object instead." % type(msg_object))

    # ----------------------------Acceleration Logging-------------------------
    def get_acceleration_data(self, msg_object):
        """
        The `get_acceleration_data()` collects all samples from all sensors
        in Bluetooth range, parse and stores them. To do this, the gateway
        sends a “Start transmitting logged data” message to all targets and
        receives the data which are followed by an “End of data message”

        :parameters:
            specific_mac : TYPE, optional
                The `get_acceleration_data()` function can also be called to activate a
                specific_mac. The The default is "".

        :returns:
            TYPE: list
                DESCRIPTION.

        """
        if isinstance(msg_object, send_get_acceleration_data_object):
            self.data = []
            self.ConnectionError = False
            # This is a DEBUG Funktion to Connect to a specific tag
            if msg_object.mac != "":
                if re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", msg_object.mac.lower()):
                    mac = [msg_object.mac]
                else:
                    self.logger.error('Mac address is not valid' + msg_object.mac)
                    return
            else:
                self.logger.info('Try to get acceleration data from tags')
                print(len(self.mac))
                if len(self.mac)==0:
                    self.taskobj = self.my_loop.create_task(self.find_tags())
                    self.my_loop.run_until_complete(self.taskobj)
                mac=self.mac
            print(msg_object.mac)
            """Read acceleration samples for each sensor"""
            for i in mac:
                global sensordaten
                sensordaten = bytearray()
                self.current_mac=i
                taskobj = self.my_loop.create_task(self.connect_to_mac(i, msg_object.command))
                self.my_loop.run_until_complete(taskobj)

            return self.data
        else:
            logging.error("%s is the wrong message object. "
                          "Use gateway.MessageObjects.send_get_acceleration_data_object instead." % type(msg_object))

    # --------------------------------handle data--------------------------------

    async def handle_data(self, handle, value):
        """
        Handles the callbacks and pass them to the process_data functions

        :parameters:
            value : bytearray
                The callbacks returned by the tags.

        :returns:
            None.

        """
        if value[0] == 0x11:
            # Daten
            sensordaten.extend(value[1:])
            self.start_time = time.time()
            self.logger.debug("Received data block: %s" % hexlify(value[1:]))
            # Marks end of data stream
        elif value[0] == 0x4a and value[3] == 0x00:
            message_return_value = return_values_from_sensor()
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
            ourcrc = crcfun(sensordaten)

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
                dataList=message_return_value.from_get_accelorationdata(accelorationdata=AccelorationData,mac=self.current_mac)
                self.data.append(dataList.returnValue.__dict__)



    #%% region processdata
    def process_sensor_data_8(self, bytes, scale, rate):
        """
        This function parses the sensor data based on its resolution.

        :parameters:
            scale : TYPE
                Is needed to decode the acceleration data.
            rate : TYPE
                Rate of sampling in smaples per second.

        :returns:
            x_vector : int
                Acceleration in x direction.
            y_vector : int
                Acceleration in y direction
            z_vector : int
                Acceleration in z direction.
            timestamp_list : time
                Timestamp

        """
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
        """
        This function parses the sensor data based on its resolution.

        :parameters:
            scale : TYPE
                Is needed to decode the acceleration data.
            rate : TYPE
                Rate of sampling in smaples per second.

        :returns:
            x_vector : int
                Acceleration in x direction.
            y_vector : int
                Acceleration in y direction
            z_vector : int
                Acceleration in z direction.
            timestamp_list : time
                Timestamp

        """
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
        """
        This function parses the sensor data based on its resolution.

        :parameters:
            scale : TYPE
                Is needed to decode the acceleration data.
            rate : TYPE
                Rate of sampling in smaples per second.

        :returns:
            x_vector : int
                Acceleration in x direction.
            y_vector : int
                Acceleration in y direction
            z_vector : int
                Acceleration in z direction.
            timestamp_list : time
                Timestamp

        """
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
    def set_config_sensor(self, msg_object):
        """
        With the “set_config_sensor()” function three sensor properties can be manipulated:

            1. Sampling rate (sampling_rate): Measuring interval of the sensor. Allowed values can be found in Chapter.

            2. Sampling resolution (sampling_resolution): Resolution of the measured values. Allowed values can be found in Chapter.

            3. Measuring range(measuring_range): Measuring range. Allowed values can be found in Chapter.

        The configuration will be sent via a “Set configuration of acceleration sensor” message to a specific sensors in Bluetooth range.
        Only arguments with allowed values will be set. All others stay as they are.
        After setting the configuration all flash pages will be deleted.
        This can cause a loss of data. The Sensor send a status response message to the gateway if the configuration was set successful or not.

        :parameters:
            specific_mac : str, optional
                Specific MAC adress. The default is "".
            sampling_rate : str, optional
                The default is 'FF'.
            sampling_resolution : str, optional
                The default is 'FF'.
            measuring_range : str, optional
                The default is 'FF'.
            divider : str, optional
                The default is "FF".

        :return
            bool
                If the function ends without making any changes, it returns FALSE.

        """

        if isinstance(msg_object, send_set_config_object):
            self.success = False
            self.work_loop(macs=msg_object.mac, command=msg_object.command)

            if self.success:
                self.logger.info("Config set")
                return self.sensor_data
            else:
                logging.error("Config set")
        else:
            logging.error("%s is the wrong message object. "
                          "Use gateway.MessageObjects.send_set_config_object instead." % type(msg_object))


    def get_config_from_sensor(self, msg_object):
        """
        The “get_config_from_sensor()” send a “Read configuration of acceleration sensor”
        message to the target sensor. The sensor returns with a “Configuration response”
        message. The configuration will be displayed.
        To see a specific sensor configuration, use its mac address as argument.

        :parameters:
            specific_mac : str, optional
                Specific MAC adress. The default is "".

        :returns:
            sensor_data as list.

        """
        if isinstance(msg_object, send_get_config_object):
            self.success = False
            self.work_loop(macs=msg_object.mac, command=msg_object.command)
            if self.success:
                self.logger.info("Config read")
                return self.sensor_data
            else:
                logging.error("Config not read")
        else:
            logging.error("%s is the wrong message object. "
                          "Use gateway.MessageObjects.send_get_config_object instead." % type(msg_object))


    def get_time_from_sensor(self, msg_object):
        """
        The “get_time_from_sensor()” function returns the current time from a
        specific sensors in Bluetooth range. The function sends a “Read system time”
        message to the targets and receives a “Timestamp response” message.

        :parameters:
            specific_mac : str, optional
                Specific MAC adress. The default is "".

        :returns:
            sensor_data as list.

        """
        if isinstance(msg_object, send_get_senor_time_object):
            self.success = False
            self.work_loop(macs=msg_object.mac, command=msg_object.command)
            if self.success:
                self.logger.info("Time read")
                return self.sensor_data
            else:
                logging.error("Time  read")
        else:
            logging.error("%s is the wrong message object. "
                      "Use gateway.MessageObjects.send_get_senor_time_object instead." % type(msg_object))




    def set_sensor_time(self,msg_object):
        """
        With the “set_sensor_time() “ function all sensors in Bluetooth range
        will be set to the current time in UTC.
        Giving a specific mac address as argument will set the time at this sensor only.
        To set the sensor time a “Set system time” message, with the current time, will be send.
        After setting the sensor time all flash pages will be deleted.
        This can cause a loss of data. The Sensor send a response message to the gateway
        if the time was set successful or not.

        :parameters:
            specific_mac : str, optional
                Specific MAC adress. The default is "".

        :returns:
            None.

        """
        """Time has to be little endian and 16 bit long"""
        if (isinstance(msg_object, send_set_sensor_time_object)):
            self.success = False
            self.work_loop(macs=msg_object.mac, command=msg_object.command)
            if self.success:
                self.logger.info("Time set")
                return self.sensor_data
            else:
                logging.error("Time  set")
        else:
            logging.error("%s is the wrong message object. "
                          "Use gateway.MessageObjects.send_set_sensor_time_object instead." % type(msg_object))


    def get_flash_statistic(self, msg_object):
        # """
        # Loop funktion zum aufrufen in eigene Funktion, die activate Logging aufruft.
        # Async
        # """
        if(isinstance(msg_object, send_get_flash_statistics_object )):
            self.success = False
            self.work_loop(macs=msg_object.mac, command=msg_object.command)
            if self.success:
                self.logger.info("flash statistics read")
                return self.sensor_data
            else:
                logging.error("flash statistics is not read")
        else:
            logging.error("%s is the wrong message object. "
                          "Use gateway.MessageObjects.send_get_flash_statistics instead." % type(msg_object))





    def get_logging_status(self, msg_object):
        """
        Checks the logging status of a specific sensor.

        :parameters:
            specific_mac : str, optional
                Specific MAC address. The default is "".

        :returns:
            list

        """
        if isinstance(msg_object,  send_get_logging_status_object ):
            self.success = False
            self.work_loop(macs=msg_object.mac, command=msg_object.command)
            if self.success:
                self.logger.info("Logging status read")
                return self.sensor_data
            else:
                logging.error("Logging status is not read")
        else:
            logging.error("%s is the wrong message object. "
                          "Use gateway.MessageObjects.send_get_logging_status instead." % type(msg_object))

    #%% region error messages

    def ri_error_to_string(self, error):
        """
        Decodes the RuuviTag error, if it was raised.
        
        :returns:
            result : set
                A set of occured errors.
        """
        result = set()
        if (error == 0):
            Log_SensorGatewayBleak.info("RD_SUCCESS")
            result.add("RD_SUCCESS")
            self.success = True
        elif(error==1):
            Log_SensorGatewayBleak.error("RD_ERROR_INTERNAL")
            result.add("RD_ERROR_INTERNAL")
        elif(error==2):
            Log_SensorGatewayBleak.error("RD_ERROR_NO_MEM")
            result.add("RD_ERROR_NO_MEM")
        elif(error==3):
            Log_SensorGatewayBleak.error("RD_ERROR_NOT_FOUND")
            result.add("RD_ERROR_NOT_FOUND")
        elif(error==4):
            Log_SensorGatewayBleak.error("RD_ERROR_NOT_SUPPORTED")
            result.add("RD_ERROR_NOT_SUPPORTED")
        elif(error==5):
            Log_SensorGatewayBleak.error("RD_ERROR_INVALID_PARAM")
            result.add("RD_ERROR_INVALID_PARAM")
        elif(error==6):
            Log_SensorGatewayBleak.error("RD_ERROR_INVALID_STATE")
            result.add("RD_ERROR_INVALID_STATE")
        elif(error==7):
            Log_SensorGatewayBleak.error("RD_ERROR_INVALID_LENGTH")
            result.add("RD_ERROR_INVALID_LENGTH")
        elif(error==8):
            Log_SensorGatewayBleak.error("RD_ERROR_INVALID_FLAGS")
            result.add("RD_ERROR_INVALID_FLAGS")
        elif(error==9):
            Log_SensorGatewayBleak.error("RD_ERROR_INVALID_DATA")
            result.add("RD_ERROR_INVALID_DATA")
        elif(error==10):
            Log_SensorGatewayBleak.error("RD_ERROR_DATA_SIZE")
            result.add("RD_ERROR_DATA_SIZE")
        elif(error==11):
            Log_SensorGatewayBleak.error("RD_ERROR_TIMEOUT")
            result.add("RD_ERROR_TIMEOUT")
        elif(error==12):
            Log_SensorGatewayBleak.error("RD_ERROR_NULL")
            result.add("RD_ERROR_NULL")
        elif(error==13):
            Log_SensorGatewayBleak.error("RD_ERROR_FORBIDDEN")
            result.add("RD_ERROR_FORBIDDEN")
        elif(error==14):
            Log_SensorGatewayBleak.error("RD_ERROR_INVALID_ADDR")
            result.add("RD_ERROR_INVALID_ADDR")
        elif(error==15):
            Log_SensorGatewayBleak.error("RD_ERROR_BUSY")
            result.add("RD_ERROR_BUSY")
        elif(error==16):
            Log_SensorGatewayBleak.error("RD_ERROR_RESOURCES")
            result.add("RD_ERROR_RESOURCES")
        elif(error==17):
            Log_SensorGatewayBleak.error("RD_ERROR_NOT_IMPLEMENTED")
            result.add("RD_ERROR_NOT_IMPLEMENTED")
        elif(error==18):
            Log_SensorGatewayBleak.error("RD_ERROR_SELFTEST")
            result.add("RD_ERROR_SELFTEST")
        elif(error==19):
            Log_SensorGatewayBleak.error("RD_STATUS_MORE_AVAILABLE")
            result.add("RD_STATUS_MORE_AVAILABLE")
        elif(error==20):
            Log_SensorGatewayBleak.error("RD_ERROR_NOT_INITIALIZED")
            result.add("RD_ERROR_NOT_INITIALIZED")
        elif(error==21):
            Log_SensorGatewayBleak.error("RD_ERROR_NOT_ACKNOWLEDGED")
            result.add("RD_ERROR_NOT_ACKNOWLEDGED")
        elif(error==22):
            Log_SensorGatewayBleak.error("RD_ERROR_NOT_ENABLED")
            result.add("RD_ERROR_NOT_ENABLED")
        else:
            Log_SensorGatewayBleak.error("RD_ERROR_FATAL")
            result.add("RD_ERROR_FATAL")
        return result
