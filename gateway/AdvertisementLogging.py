from ruuvitag_sensor.adapters.nix_hci import BleCommunicationNix
from ruuvitag_sensor.decoder import get_decoder
from ruuvitag_sensor.data_formats import DataFormats
import datetime
import time
import nest_asyncio
import asyncio
from gateway import MessageObjects


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
ble = BleCommunicationNix()
class advertisementLogging():

    def start_advertisement_logging(self):
        my_loop.run_until_complete(self.advertisement_logging())

    def end__advertisement_logging(self):
        stopEvent.set()

    def __init__(self):
        print("init")

    async def advertisement_logging(self):

            last_measurement_number = ""
            return_value_object=MessageObjects.return_values_from_sensor()
            last_measurement_number = {}
            try:
                for ble_data in ble.get_datas():

                    #current_time = time.gmtime(time.time())
                    current_time=time.time()
                    mac = ble_data[0]
                    data = ble_data[1]

                    (data_format, data) = DataFormats.convert_data(ble_data[1])
                    if data is not None:
                        decoded = get_decoder(data).decode_data(data)
                        if decoded is not None:
                            del decoded["mac"]
                        # print(decoded)
                            if mac in last_measurement_number:
                                if decoded["measurement_sequence_number"] != last_measurement_number[mac]:
                                    last_measurement_number[mac] = decoded["measurement_sequence_number"]

                                    #print(last_measurement_number)
                                else:
                                    continue
                            else:
                                last_measurement_number[mac]=decoded["measurement_sequence_number"]
                            msg_obj = return_value_object.from_get_advertisementdata(decoded, mac,
                                                                                     current_time).returnValue
                            #print(msg_obj.__dict__)
                            print([mac,current_time,decoded])
                            keyList = list(decoded.keys())
                        #print(keyList)
                            valueList = list(decoded.values())
                        #print(valueList)
                            s = "".join([str(x) + "," for x in valueList])
                        # print(s)
                            date = datetime.date.today()
                            with open("advertisment-{}.csv".format(date), 'a') as f:
                                f.write("{}{},{}".format(s, mac, current_time))
                                f.write("\n")


            except KeyboardInterrupt:
            #     # When Ctrl+C is pressed execution of the while loop is stopped
            #     stopEvent.set()
                print('Exit')
