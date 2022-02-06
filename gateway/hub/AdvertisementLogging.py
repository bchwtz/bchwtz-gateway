from gateway.hub.nix_hci import BleCommunicationNix
from gateway.hub.decoder import get_decoder
from gateway.hub.DataFormats import DataFormats
import datetime
import time
from gateway.sensor import MessageObjects
from os.path import exists

ble = BleCommunicationNix()

def advertisement_logging():
    """Listen to advertisements from BLE devices and 
    writes it to an csv-file.
    """
    return_value_object=MessageObjects.return_values_from_sensor()
    last_measurement_number = {}
    try:
        for ble_data in ble.get_datas():
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
                        else:
                            continue
                    else:
                        last_measurement_number[mac]=decoded["measurement_sequence_number"]
                    msg_obj = return_value_object.from_get_advertisementdata(decoded, mac,
                                                                             current_time).returnValue
                    print([mac,current_time,decoded])
                    keyList = list(decoded.keys())
                    valueList = list(decoded.values())
                    s = "".join([str(x) + "," for x in valueList])
                    keys = "".join([str(key) + "," for key in keyList])
                    preamble = ""
                    date = datetime.date.today()
                    logfilename = "advertisment-{}.csv".format(date)
                    if not exists("advertisment-{}.csv".format(date)):
                        preamble = "{}{},{}".format(keys, "mac", "date")

                    with open(logfilename, 'a') as f:
                        if preamble != "":
                            f.write(preamble)
                            f.write("\n")
                        f.write("{}{},{}".format(s, mac, time.asctime(time.localtime(current_time))))
                        f.write("\n")
    except Exception as e:
        print('{}'.format(e))
