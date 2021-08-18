from ruuvitag_sensor.adapters.nix_hci import BleCommunicationNix
from ruuvitag_sensor.decoder import get_decoder
from ruuvitag_sensor.data_formats import DataFormats
import ruuvitag_sensor.log
import datetime
import asyncio
import time
from bleak import BleakScanner
from bleak import BleakClient
import bleak
UART_RX = '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'
#test=BleakScanner.start()

import asyncio
from bleak import BleakScanner

def detection_callback(device, advertisement_data):
    print(time.strftime("%H:%M:%S",time.localtime(time.time())),device.address,advertisement_data)


async def run():
    scanner = BleakScanner(filters={"UUIDs":["6E400001-B5A3-F393-E0A9-E50E24DCCA9E"], "DuplicateData":False})
    #scanner._scanning_mode="Passive"
    #scanner
    print(scanner._adapter)
    scanner.set_scanning_filter()
    scanner.register_detection_callback(detection_callback)
    await scanner.start()
    await asyncio.sleep(80.0)
    # await scanner.stop()
    # for d in scanner.discovered_devices:
    #     print(d)


# class Logging:
#     def __init__(self):
#         self.my_loop = asyncio.get_event_loop()
#
#
#     def listen(self):
#         self.taskobj = self.my_loop.create_task(BleakScanner.start(self))
#         self.my_loop.run_until_complete(self.taskobj)
#
#     async def loop(self):
#         print("loop")
#         while True:
#             try:
#                 print("loop")
#                 async with BleakClient("",device="hci0") as bleak:
#                     bleak.start_notify(UART_RX,callback=self.write_data)
#             except KeyboardInterrupt:
#                 # When Ctrl+C is pressed execution of the while loop is stopped
#                 print('Exit')
#                 break
#
#     def write_data(sender: int, value: bytearray):
#         print(sender)
#         print(value)

#bleak.backends.scanner.AdvertisementData

# test = BleakClient
# atest.start_notify("hci0",UART_RX,callback=write_data)
 #ble = BleCommunicationNix()
# while True:
#     try:
#         for ble_data in ble.get_datas():
#             current_time = datetime.datetime.now()
#             mac=ble_data[0]
#             data=ble_data[1]
#             (data_format, data) = DataFormats.convert_data(ble_data[1])
#             if data is not None:
#                 decoded=get_decoder(data).decode_data(data)
#                 if decoded is not None:
#                     del decoded["mac"]
#                     #print(decoded)
#                     keyList=list(decoded.keys())
#                     #print(keyList)
#                     valueList=list(decoded.values())
#                     #print(valueList)
#                     s="".join([str(x)+"," for x in valueList])
#                     #print(s)
#                     date=datetime.date.today()
#                     with open("advertisment-{}.csv".format(date), 'a') as f:
#                         f.write("{}{},{}".format(s,mac,current_time.isoformat()))
#                         f.write("\n")
#
#     except KeyboardInterrupt:
#         # When Ctrl+C is pressed execution of the while loop is stopped
#         print('Exit')
#         break
