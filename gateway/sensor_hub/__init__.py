from gateway.sensor_hub import AdvertisementLogging
from gateway.sensor import sensor
from bleak import BleakScanner
#import re
import logging
import asyncio

#Logger
Log_sensor_hub = logging.getLogger('sensor_hub')
Log_sensor_hub.setLevel("DEBUG")
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
Log_sensor_hub.addHandler(console_handler)

class Event_ts(asyncio.Event):
    """Custom event loop class for sensorhub
    """
    def clear(self):
        self._loop.call_soon_threadsafe(super().clear)

    def set(self):
        self._loop.call_soon_threadsafe(super().set)  

class sensor_hub(object):
    def __init__(self):
        #asyncio.Event = Event_ts
        self.main_loop = asyncio.get_event_loop()
        self.logger = logging.getLogger('sensor_hub.sensor_hub')
        self.sensorlist = list()
        return
    
    def discover_neighborhood(self):
        self.sensorlist = list()
        taskobj = self.main_loop.create_task(self.find_tags())
        self.main_loop.run_until_complete(taskobj)
        #self.sensorlist.append(asyncio.run(self.find_tags()))
    
    def __validate_mac(self, devices):
        """
        This funcion updates the internal mac_list. If a MAC address passed the
        checked_mac_address process, it will extend the list 'mac'.

        :parameters:
            devices : dictionary {name, address}

        :returns:
            None.
        """
        for i in devices:
            self.logger.info('Device: %s with Address %s found!' % (i.name, i.address))
            if ("Ruuvi" in i.name):
                self.logger.info('Device: %s with Address %s saved in MAC list!' % (i.name, i.address))
                self.sensorlist.append(sensor(i.name, i.address))
        return
    
    async def find_tags(self):
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
        self.sensorlist = list()
        devices = await BleakScanner.discover(timeout=5.0)
        self.__validate_mac(devices)

        
    def listen_advertisements(self):
        """
        Start listening to advertisements

        Returns
        -------
        None.

        """
        Log_sensor_hub.warn("Warning: To stop the advertisementlogging, you need to interrupt the kernel!")
        input("Press any key to confirm!")
        AdvertisementLogging.advertisement_logging()

  
    
    """Configure the interface between the sensorhub and other services
    """
