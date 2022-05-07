# %% Libraries
from gateway.hub import AdvertisementLogging
from gateway.sensor import sensor
from bleak import BleakScanner
import logging
import asyncio


# %% Logger
Log_hub = logging.getLogger('hub')
Log_hub.setLevel("DEBUG")
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
Log_hub.addHandler(console_handler)

# %% hub
class hub(object):
    def __init__(self):
        """Initialize an object from type hub.
        """
        self.main_loop = asyncio.get_event_loop()
        self.logger = logging.getLogger('hub.hub')
        self.sensorlist: list[sensor] = list()
        return
    
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
            self.logger.info('Device: %s with Address %s found!' % (i.name, i.address))
            if ("Ruuvi" in i.name):
                self.logger.info('Device: %s with Address %s saved in MAC list!' % (i.name, i.address))
                self.sensorlist.append(sensor(i.name, i.address))
        return
    
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
        Log_hub.info("Warning: To stop the advertisementlogging, you need to interrupt the kernel!")
        input("Press any key to confirm!")
        AdvertisementLogging.advertisement_logging()

  
    
    """Configure the interface between the sensorhub and other services
    """

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