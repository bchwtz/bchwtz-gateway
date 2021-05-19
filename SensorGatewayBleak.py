# -*- coding: utf-8 -*-
import asyncio
import nest_asyncio
import re
import operator
from binascii import hexlify
from bleak import BleakScanner
from bleak import BleakClient
import logging

# -------------------Global Variables-------------------------
address = "F2:23:D0:45:E4:DD"

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

        # print(self.mac)

    def callback(self, sender: int, value: bytearray):
        print("Received %s" % hexlify(value))

    async def find_tags(self):
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

    '''
    Activate acceleration logging.
    '''

    def activate_logging_at_sensor(self, specific_mac=""):
        """
        Loop funktion zum aufrufen in eigene Funktion, die activate Logging aufruft.
        Async
        """
        my_loop = asyncio.get_running_loop()

        print(self.mac)
        command_string = "FAFA0a0100000000000000"
        if specific_mac != "":
            if re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", specific_mac.lower()):
                mac = [specific_mac]
            else:
                print("Mac is not valid")
                return
        try:
            taskobj = my_loop.create_task(self.connect_to_mac(command_string))
            my_loop.run_until_complete(taskobj)
        except RuntimeError as e:
            print("Error: {}".format(e))
        print("logging activated")

    async def connect_to_mac(self, command_string):
        for i in self.mac:
            try:
                async with BleakClient(i) as client:
                    await client.write_gatt_char("6e400002-b5a3-f393-e0a9-e50e24dcca9e",
                                                 bytearray.fromhex(command_string), True)
                    print("sended")
                    await client.start_notify(UART_RX, self.callback)
                    await asyncio.sleep(1)
                    await client.stop_notify(UART_RX)
                    print("Stopped")
            except Exception as e:
                print(e)

                print("No connection Available")

            print("Connection established")