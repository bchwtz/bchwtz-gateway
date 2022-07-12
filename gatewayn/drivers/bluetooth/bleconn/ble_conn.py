from bleak import BleakScanner
import asyncio
import logging
from termcolor import colored
from gatewayn.drivers.bluetooth.bleconn.tag import Tag
class BLEConn():
    def __init__(self) -> None:
        self.main_loop = asyncio.get_event_loop()
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger("BLEConn")
        self.logger.setLevel(logging.INFO)

    def scan_tags(self, timeout = 5.0) -> list:
        """The function searches for bluetooth devices nearby and passes the
        MAC addresses to the __validate_mac function.

        :param timeout: timeout for the find_tags function, defaults to 5.0
        :type timeout: float, optional
        """
        sensorlist = []
        devices = self.main_loop.run_until_complete(BleakScanner.discover(timeout=timeout))
        sensorlist = self.__validate_mac(devices)
        return sensorlist

    def __validate_mac(self, devices):
        """ This funcion updates the internal mac_list. If a MAC address passed the
        checked_mac_address process, it will extend the list 'mac'.

        :param devices: device passed by the BleakScanner function
        :type devices: bleak.backends.device.BLEDevice
        """
        sensorlist = []
        for i in devices:
            self.logger.info('Device: %s with Address %s found!' % (i.name, i.address))
            if ("Ruuvi" in i.name):
                self.logger.info(colored('Device: %s with Address %s saved in MAC list!' % (i.name, i.address), "green", attrs=['bold']) )
                sensorlist.append(Tag(i.name, i.address))
        return sensorlist
    
