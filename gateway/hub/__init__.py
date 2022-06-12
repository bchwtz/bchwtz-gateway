"""Docstring for Pylint"""
# %% Libraries
import logging
import asyncio
from bleak import BleakScanner
from gateway.hub import advertisement_logging
from gateway.sensor import sensor



LOG_LEVEL = logging.INFO

# %% Logger
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('Hub')
logger.setLevel(LOG_LEVEL)

# %% hub
class Hub():
    """Class representing a Hub"""
    def __init__(self):
        """Initialize an object from type hub.
        """
        self.main_loop = asyncio.get_event_loop()
        self.sensorlist: list[sensor] = list()

    def discover(self, timeout = 5.0):
        """Calls the find_tags function in an async workloop.

        :param timeout: timeout for the discover function, defaults to 5.0
        :type timeout: float, optional
        """
        self.sensorlist = list()
        taskobj = self.main_loop.create_task(self.find_tags(timeout))
        self.main_loop.run_until_complete(taskobj)

    def __validate_mac(self, devices):
        """ This funcion updates the internal mac_list. If a MAC address passed the
        checked_mac_address process, it will extend the list 'mac'.

        :param devices: device passed by the BleakScanner function
        :type devices: bleak.backends.device.BLEDevice
        """
        for i in devices:
            logger.info('Device: %s with Address %s found!' % (i.name, i.address))
            if ("Ruuvi" in i.name):
                logger.info('Device: %s with Address %s saved in MAC list!' % (i.name, i.address))
                self.sensorlist.append(sensor(i.name, i.address))

    async def find_tags(self, timeout = 5.0):
        """The function searches for bluetooth devices nearby and passes the
        MAC addresses to the __validate_mac function.

        :param timeout: timeout for the find_tags function, defaults to 5.0
        :type timeout: float, optional
        """
        self.sensorlist = list()
        devices = await BleakScanner.discover(timeout=timeout)
        self.__validate_mac(devices)


    def listen_advertisements(self):
        """Start logging advertisements
        """
        logger.info("Warning: To stop the advertisementlogging, you need to interrupt the kernel!")
        input("Press any key to confirm!")
        advertisement_logging.advertisement_logging()

    # Configure the interface between the sensorhub and other services

    def get_sensor_by_mac(self, mac = None) -> sensor:
        """Get a sensor object by an known mac adress.

        :param mac: mac adress from a BLE device, defaults to None
        :type mac: str, optional
        :return: Returns a sensor object.
        :rtype: sensor.sensor
        """
        if mac is not None:
            for sensor in self.sensorlist:
                if sensor.mac == mac:
                    return sensor
        else:
            return None
