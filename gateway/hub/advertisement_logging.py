"""advertisement logging."""
import datetime
import time
from os.path import exists
from gateway.hub.nix_hci import BleCommunicationNix
from gateway.hub.decoder import get_decoder
from gateway.hub.DataFormats import DataFormats
from gateway.sensor import MessageObjects


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
            (_data_format, data) = DataFormats.convert_data(ble_data[1])
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
                    _msg_obj = return_value_object.from_get_advertisementdata(decoded, mac,
                                                                        current_time).returnValue
                    print([mac,current_time,decoded])
                    key_list = list(decoded.keys())
                    value_list = list(decoded.values())
                    value_str = "".join([str(x) + "," for x in value_list])
                    keys = "".join([str(key) + "," for key in key_list])
                    preamble = ""
                    date = datetime.date.today()
                    logfilename = f"advertisment-{date}.csv"
                    if not exists(f"advertisment-{date}.csv"):
                        preamble = f"{keys}{mac},{date}"
                    with open(logfilename, 'a', encoding='utf_8') as logfile:
                        if preamble != "":
                            logfile.write(preamble)
                            logfile.write("\n")
                        # pylint: disable-next=line-too-long
                        logfile.write(f"{value_str}{mac},{time.asctime(time.localtime(current_time))}")
                        #.format(value_str, mac, time.asctime(time.localtime(current_time))))
                        logfile.write("\n")
    except Exception as exeption:
        print(f'{exeption}')
