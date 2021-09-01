import datetime
from gateway.AdvertisementDecoder import _get_data_format_5
import gateway.AdvertisementDecoder
from bleak import BleakClient
from functools import partial
from bleak import BleakScanner
import nest_asyncio
import asyncio


#Channel where advertisements are collected
UART_RX = '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'





mac = []
adv_data=[]
nest_asyncio.apply()
my_loop = asyncio.get_event_loop()

class Event_ts(asyncio.Event):
    def clear(self):
        self._loop.call_soon_threadsafe(super().clear)

    def set(self):
        self._loop.call_soon_threadsafe(super().set)


stopEvent = Event_ts()


def detection_callback(client: BleakClient, sender: int,data:bytearray):

    if _get_data_format_5(data):
        #get decoder and parse data
        decoder = gateway.AdvertisementDecoder.get_decoder(5)
        adv_data=decoder.decode_data(data)
        adv_data["mac"]=client.address
        date = datetime.date.today()
        current_time = datetime.datetime.now()
        with open("advertisment-{}.csv".format(date), 'a') as f:
            f.write("{},{}".format(adv_data,current_time.isoformat()))
            f.write("\n")
        print(adv_data)


def validate_mac(devices):
    print("validate")
    for i in devices:
        # self.logger.info('Device: %s with Address %s found!' % (i.name, i.address))
        if ("Ruuvi" in i.name) & (i.address not in mac):
            print("found")
            mac.append(i.address)
            print(mac)
async def start_advertisement_logging():
    my_loop.run_until_complete(advertisement_logging())

async def end__advertisement_logging():
    stopEvent.set()
    
async def advertisement_logging():
    try:
        #find devices
        devices = await BleakScanner.discover(timeout=5.0)
        validate_mac(devices)

        if len(mac) > 0:
            for i in mac:
                async with BleakClient(i) as client:
                    #start notify advertisements
                    await client.start_notify(UART_RX,partial(detection_callback, client) )
                    await stopEvent.wait()
    except Exception as e:
        print("Error: {}".format(e))
        client.stop_notify(UART_RX)
    # When Ctrl+C is pressed execution of the while loop is stopped
    except KeyboardInterrupt:
        client.stop_notify()
        stopEvent.set()
        print('Exit')
