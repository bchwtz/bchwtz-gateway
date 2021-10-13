from ruuvitag_sensor.adapters.nix_hci import BleCommunicationNix
from ruuvitag_sensor.decoder import get_decoder
from ruuvitag_sensor.data_formats import DataFormats
import time
import MessageObjects
import json
import Thing


ble = BleCommunicationNix()


def advertisement_logging():
            """
            This function listens to the advertisement messages send by devices nearby.

            :parameters:
                mf_conf_file : dict
                    mf_conf_file is needed to connect to the mqtt broker.

            :returns:
                None.

            """
            mf_client = Thing.Thing(username="a9793bed-ed85-44e5-8346-5628a392da9b", password="a1272c0c-64d7-4b8b-a85b-14e53a78ddc7")
            adv_topic = "channels/34f9ec3c-aa5b-4072-a0f1-396a932c5c31/messages/advertisement"
            mf_client.connect_to_broker("mf.sys-tem.org")
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
                            if mac in last_measurement_number:
                                if decoded["measurement_sequence_number"] != last_measurement_number[mac]:                                    
                                    last_measurement_number[mac] = decoded["measurement_sequence_number"]                                    
                                else:
                                    continue
                            else:
                                last_measurement_number[mac]=decoded["measurement_sequence_number"]                               
                            msg_obj = return_value_object.from_get_advertisementdata(decoded, mac,
                                                                                     current_time).returnValue

                            adv_msg = json.dumps(msg_obj.__dict__)
                            mf_client.pub_to_channel(topic= adv_topic, payload = adv_msg) 
                            time.sleep(10)

            except KeyboardInterrupt:
                print('Exit')