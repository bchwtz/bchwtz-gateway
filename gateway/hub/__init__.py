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

# %% Event_ts
class Event_ts(asyncio.Event):
    """Custom event loop class for hub
    """
    def clear(self):
        self._loop.call_soon_threadsafe(super().clear)

    def set(self):
        self._loop.call_soon_threadsafe(super().set)  

# %% hub
class hub(object):
    def __init__(self):
        self.main_loop = asyncio.get_event_loop()
        self.logger = logging.getLogger('hub.hub')
        self.sensorlist: list[sensor] = list()
        return
    
    def discover(self, timeout = 5.0):
        """
        Calls the find_tags function in async workloop.

        :returns:
            None.

        """
        self.sensorlist = list()
        taskobj = self.main_loop.create_task(self.find_tags(timeout))
        self.main_loop.run_until_complete(taskobj)
    
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
    
    async def find_tags(self, timeout = 5.0):
        """
        The function searches for bluetooth devices nearby and passes the
        MAC addresses to the __validate_mac function.        

        Returns
        -------
        None.

        """   
        self.sensorlist = list()
        devices = await BleakScanner.discover(timeout=timeout)
        self.__validate_mac(devices)

        
    def listen_advertisements(self):
        """
        Start logging advertisement.

        Returns
        -------
        None.

        """
        Log_hub.warn("Warning: To stop the advertisementlogging, you need to interrupt the kernel!")
        input("Press any key to confirm!")
        AdvertisementLogging.advertisement_logging()

  
    
    """Configure the interface between the sensorhub and other services
    """

    def get_sensor_by_mac(self, mac = None) -> sensor:
        if mac is not None:
            for sensor in self.sensorlist:
                if sensor.mac == mac:
                    return sensor
        else:
            return None