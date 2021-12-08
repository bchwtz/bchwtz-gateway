import AdvertisementLogging
from sensor import sensor
from bleak import BleakScanner
#import re
import logging
import asyncio

#Logger
Log_sensor_hub = logging.getLogger('sensor_hub')
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
Log_sensor_hub.addHandler(console_handler)

class sensor_hub(object):
    def __init__(self):
        self.main_loop = asyncio.get_event_loop()
        self.sensorlist = list()
        return
    
    def discover_neighborhood(self):
        self.sensorlist = list()
        #taskobj = self.main_loop.create_task(self.find_tags())
        #self.sensorlist.append(self.main_loop.run_until_complete(taskobj))
        self.sensorlist.append(asyncio.run(self.find_tags()))
    
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
            if ("Ruuvi" in i.name) & (i.address not in self.mac):
                self.logger.info('Device: %s with Address %s saved in MAC list!' % (i.name, i.address))
                return (i.name, i.address)
    
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
        devices = await BleakScanner.discover(timeout=5.0)
        self.__validate_mac(devices)
        
        if len(self.mac) == 0:
            self.logger.warning("No RuuviTags were found.")
            return False
        return True
        devices = await BleakScanner.discover(timeout=5.0)
        name, adress = self.__validate_mac(devices)
        return sensor(name=name, mac=adress)
        
    def listen_advertisements():
        """
        Start listening to advertisements

        Returns
        -------
        None.

        """
        Log_sensor_hub.warn("Warning: To stop the advertisementlogging, you need to interrupt the kernel!")
        input("Press any key to confirm!")
        AdvertisementLogging.advertisement_logging()



class Event_ts(asyncio.Event):
    """Custom event loop class for sensorhub
    """
    def clear(self):
        self._loop.call_soon_threadsafe(super().clear)

    def set(self):
        self._loop.call_soon_threadsafe(super().set)    
    
    """Configure the interface between the sensorhub and other services
    """
