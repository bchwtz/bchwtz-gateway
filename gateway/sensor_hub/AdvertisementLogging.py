from gateway.sensor_hub.nix_hci import BleCommunicationNix
from gateway.sensor_hub.decoder import get_decoder
from gateway.sensor_hub.DataFormats import DataFormats
import datetime
import time
from gateway import MessageObjects

ble = BleCommunicationNix()


def advertisement_logging():
    """


    Returns
    -------
    None.

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
                   #Add push to mainflux here. Use msg_obj from above
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
        print('Exit')
