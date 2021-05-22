# -*- coding: utf-8 -*-
"""
TO-DOs:
    1. init : self.find_tags gehört nicht in den Konstruktor
    

"""


import asyncio
import nest_asyncio
import re
import operator
import time
from binascii import hexlify
from bleak import BleakScanner
from bleak import BleakClient
import logging

# -------------------Global Variables-------------------------
address = "F2:23:D0:45:E4:DD"
readAllString = "FAFA030000000000000000"
UART_SRV = '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'
UART_TX = '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'
UART_RX = '6E400003-B5A3-F393-E0A9-E50E24DCCA9E'


# -------------------Logger Configurations--------------------
# Load the default configurations of the python logger
# logging.basicConfig()
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
# ------------------------------------------------------------


# --------------------Acitvate nest_asyncio-------------------
# Aktivate nest_asyncio to prevent an error while processing the communication loops
nest_asyncio.apply()


# ------------------------------------------------------------


# -----------Class RuuviTagAccelerometerCommunicationBleak----
class RuuviTagAccelerometerCommunicationBleak:
    def __init__(self):
        # Constructor of the class RuuviTagAccelerometerCommunicationBleak

        # Create a child of the previously created logger 'SensorGatewayBleak'
        self.logger = logging.getLogger('SensorGatewayBleak.ClassRuuvi')
        self.logger.info('Initialize child logger ClassRuuvi')
        self.logger.info('Start constructor')

        # MAC - list of addresses of the bluetooth devices
        self.mac = []

        # Data recieved by the bluetooth devices
        self.data = []

        # Auxiliary Variables
        # self.reading_done=False
        # self.ConnectionError = False

        # Search for asyncio loops that are already running
        my_loop = asyncio.get_running_loop()
        self.logger.info('Searching for running loops completed')

        # Create a task 
        taskobj = my_loop.create_task(self.find_tags())
        self.logger.info('Searching for tags completed')

        my_loop.run_until_complete(taskobj)
        
        #Einige functionen müssen evtl. in eine __enter__-Funktion z.B. fand_tags
        
        
    def __exit__(self):
        self.data = []
        self.logger.info('Reset self.data !')
        self.mac = []
        self.logger.info('Reset self.mac')
        # Do we need a "Reset Tag"-Command to get the Tag in a safe state?


    #-------------Find -> Connect -> Listen-Functions---------------------
    async def find_tags(self):
        # First Funktion -> Find Ruuvitags
        
        Tags_sofar = len(self.mac)
        devices = await BleakScanner.discover()
        for i in devices:
            self.logger.info('Device: %s with Address %s found!' % (i.name, i.address))
            if ("Ruuvi" in i.name) & (i.address not in self.mac):
                self.mac.append(i.address)
                self.logger.info('Device: %s with Address %s saved in MAC list!' % (i.name, i.address))
        tags_new = len(self.mac) - Tags_sofar
        self.logger.info('%d new Ruuvi tags were found' % tags_new)
        return

    def handle_sensor_commands(self,sender: int, value: bytearray):
        """
        handle -- integer, characteristic read handle the data was received on
        value -- bytearray, the data returned in the notification
        """
        print("handle sensor commands")
        if value[0] == 0xFB:
            if (value[1] == 0x00):
                print("Status: %s" % str(self.ri_error_to_string(value[2])))
            elif (value[1] == 0x07):
                print("Status: %s" % str(self.ri_error_to_string(value[2])))
                print("Received data: %s" % hexlify(value[3:]))
                print(value[3])
                print(type(value[3]))
                print("Samplerate:    %s Hz" % value[3])
                print("Resolution:    %s Bits" % (int(value[4])))
                print("Scale:         %xG" % value[5])
                print("DSP function:  %x" % value[6])
                print("DSP parameter: %x" % value[7])
                print("Mode:          %x" % value[8])
            elif (value[1] == 0x09):
                print("Status: %s" % str(self.ri_error_to_string(value[2])))
                # die Daten sind little-endian (niegrigwertigstes Bytes zuerst) gespeichert
                # die menschliche lesart erwartet aber big-endian (höchstwertstes Bytes zuerst)
                # deswegen Reihenfolge umdrehen
                print("Received data: %s" % hexlify(value[:-9:-1]))
                print(time.strftime('%D %H:%M:%S', time.gmtime(int(hexlify(value[:-9:-1]), 16) / 1000)))

            else:
                print("Antwort enthält falschen Typ")
        self.reading_done=True

    """Error messages"""

    @staticmethod
    def ri_error_to_string(error):
        result = set()
        if error == 0:
            result.add("RD_SUCCESS")

        else:
            if error & (1 << 0):
                result.add("RD_ERROR_INTERNAL")
            if error & (1 << 1):
                result.add("RD_ERROR_NO_MEM")
            if error & (1 << 2):
                result.add("RD_ERROR_NOT_FOUND")
            if error & (1 << 3):
                result.add("RD_ERROR_NOT_SUPPORTED")
            if error & (1 << 4):
                result.add("RD_ERROR_INVALID_PARAM")
            if error & (1 << 5):
                result.add("RD_ERROR_INVALID_STATE")
            if error & (1 << 6):
                result.add("RD_ERROR_INVALID_LENGTH")
            if error & (1 << 7):
                result.add("RD_ERROR_INVALID_FLAGS")
            if error & (1 << 8):
                result.add("RD_ERROR_INVALID_DATA")
            if error & (1 << 9):
                result.add("RD_ERROR_DATA_SIZE")
            if error & (1 << 10):
                result.add("RD_ERROR_TIMEOUT")
            if error & (1 << 11):
                result.add("RD_ERROR_NULL")
            if error & (1 << 12):
                result.add("RD_ERROR_FORBIDDEN")
            if error & (1 << 13):
                result.add("RD_ERROR_INVALID_ADDR")
            if error & (1 << 14):
                result.add("RD_ERROR_BUSY")
            if error & (1 << 15):
                result.add("RD_ERROR_RESOURCES")
            if error & (1 << 16):
                result.add("RD_ERROR_NOT_IMPLEMENTED")
            if error & (1 << 16):
                result.add("RD_ERROR_SELFTEST")
            if error & (1 << 18):
                result.add("RD_STATUS_MORE_AVAILABLE")
            if error & (1 << 19):
                result.add("RD_ERROR_NOT_INITIALIZED")
            if error & (1 << 20):
                result.add("RD_ERROR_NOT_ACKNOWLEDGED")
            if error & (1 << 21):
                result.add("RD_ERROR_NOT_ENABLED")
            if error & (1 << 31):
                result.add("RD_ERROR_FATAL")
        return result
    """
    Copy Pasta, rename one to connect_to_mac_command
    connect_to_mac_command handels sending commands to tag, like activate deactivate Logging. 
    And handle recieving data from sensor in handle sensor command.

    For connect_to_mac use hanle_data. Use the process_sensor_data functions to interpret the values.

    """
    async def connect_to_mac_command(self, command_string, specific_mac = ""):
        # Second Funktion -> Connect to Ruuvitag and send commands
        if specific_mac != "":
            mac = [specific_mac]
        else:
            mac = self.mac
        for i in mac:
            try:
                async with BleakClient(i) as client:
                    #Send the command (Wait for Response must be True)
                    await client.write_gatt_char("6e400002-b5a3-f393-e0a9-e50e24dcca9e",
                                                 bytearray.fromhex(command_string), True)
                    self.logger.info('Message send to MAC: %s' % (i))
                    await client.start_notify(UART_RX, self.handle_sensor_commands)
                    await asyncio.sleep(1)
                    self.logger.info('Stop notify: %s' % (i))
                    await client.stop_notify(UART_RX)
                    self.logger.info('Stop notify: %s' % (i))
            except Exception as e:
                self.logger.warning('Connection faild at MAC %s' %(i))
                self.logger.error("Error: {}".format(e))
                
            self.logger.info("")   

    # Reciving and Handling of Callbacks
    def callback(self, sender: int, value: bytearray):
        self.logger.info("Received %s" % hexlify(value))
        try:
            self.data.append((sender, value))
            self.logger.info('Callback saved in self.data')
        except Exception as e:
            self.logger.warning('Error while handling data: ' + str(e))    

    #-------------------------------------------------------------------------
    
    #------------------------Activate/Deactivate Logging----------------------
    def activate_logging_at_sensor(self, specific_mac=""):
        """
        Loop funktion zum aufrufen in eigene Funktion, die activate Logging aufruft.
        Async
        """
        my_loop = asyncio.get_running_loop() #?
        
        # Command send to the Ruuvitag
        command_string = "FAFA0a0100000000000000"
        
        if specific_mac != "":
            if re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", specific_mac.lower()):
                mac = [specific_mac]
                self.logger.info('MAC set to specific Mac-Address')
            else:
                self.logger.error("Mac is not valid!")
                return
        try:
            taskobj = my_loop.create_task(self.connect_to_mac_command(command_string))
            my_loop.run_until_complete(taskobj)
        except RuntimeError as e:
            print("Error: {}".format(e))
        print("logging activated")
        
    """
    Bug: Befehl wird 2X pro sensor ausgeführt
    """
    def deactivate_logging_at_sensor(self, specific_mac=""):
        my_loop = asyncio.get_running_loop()  # ?
        if specific_mac != "":
            if re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", specific_mac.lower()):
                mac = [specific_mac]
                self.logger.info('MAC set to specific Mac-Address')
            else:
                self.logger.error("Mac is not valid!")
                return
        else:
            mac = self.mac
        # Stop Logging Command
        command_string = "FAFA0a0000000000000000"
        for i in mac:
            try:
                taskobj = my_loop.create_task(self.connect_to_mac_command(command_string))
                my_loop.run_until_complete(taskobj)
            except RuntimeError as e:
                print("Error: {}".format(e))

    #----------------------------Acceleration Logging-------------------------    
    def get_acceleration_data(self,specific_mac=""):
        #global readAllString #? Wofür ist dieser String
        self.data = []
        self.ConnectionError=False
        readAllString = "FAFA050000000000000000"
        my_loop = asyncio.get_running_loop()
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
            #mac = self.find_tags_mac()

        """Read acceleration samples for each sensor"""
        for i in mac:

            taskobj = my_loop.create_task(self.connect_to_mac(readAllString))
            my_loop.run_until_complete(taskobj)
            self.reading_done=False
            # if adapter._running.is_set() == False:
            #     print("Need to start adapter")
            #     adapter = pygatt.GATTToolBackend()
            #     adapter.start()
          # self.connect_to_mac(readAllString)

            """Wait  until all reading is done. We can only read one sensor at the time"""
            while not self.reading_done:
                time.sleep(1)

        #adapter.reset()
        try:
            recieved_data = self.data
            """Exit function if recieved data is empty"""
            if(len(self.data[0][0])==0):
                print("No data stored")
                return
            """Write data into csv file"""
            for i in range(0, len(recieved_data)):
                data = list(zip(recieved_data[i][0]))
                current_mac = recieved_data[i][1]
                for i in data:
                    with open("acceleration-{}.csv".format(data[0][0][3]), 'a') as f:
                        f.write("{},{}".format(str(i[0])[1:-1], current_mac))
                        f.write("\n")
        except Exception as e:
            self.logger.error("Error: {}".format(e))
        return self.data


    
