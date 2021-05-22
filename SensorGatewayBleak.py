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


    async def connect_to_mac(self, command_string, specific_mac = ""):
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
                    self.logger.info('Message send to MAC: %d' % (i))
                    await client.start_notify(UART_RX, self.callback)
                    await asyncio.sleep(1)
                    self.logger.info('Stop notify: %d' % (i))
                    await client.stop_notify(UART_RX)
                    self.logger.info('Stop notify: %d' % (i))
            except Exception as e:
                self.logger.warning('Connection faild at MAC %d' %(i))
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
            taskobj = my_loop.create_task(self.connect_to_mac(command_string))
            my_loop.run_until_complete(taskobj)
        except RuntimeError as e:
            print("Error: {}".format(e))
        print("logging activated")
        

    def deactivate_logging_at_sensor(self, specific_mac=""):
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
                self.connect_to_mac_command(command_string)
            except RuntimeError as e:
                print("Error: {}".format(e))

    #----------------------------Acceleration Logging-------------------------    
    def get_acceleration_data(self,specific_mac=""):
        #global readAllString #? Wofür ist dieser String
        self.data = []
        self.ConnectionError=False
        readAllString = "FAFA050000000000000000"
        
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
            self.reading_done=False
            # if adapter._running.is_set() == False:
            #     print("Need to start adapter")
            #     adapter = pygatt.GATTToolBackend()
            #     adapter.start()
            self.connect_to_mac(readAllString)

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


    
