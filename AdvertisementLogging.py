from ruuvitag_sensor.adapters.nix_hci import BleCommunicationNix
from ruuvitag_sensor.decoder import get_decoder
from ruuvitag_sensor.data_formats import DataFormats
import ruuvitag_sensor.log
import datetime
import time

ble = BleCommunicationNix()

while True:
    try:        
        for ble_data in ble.get_datas():
            current_time = datetime.datetime.now()
            mac=ble_data[0]
            data=ble_data[1]
            (data_format, data) = DataFormats.convert_data(ble_data[1])
            if data is not None:
                decoded=get_decoder(data).decode_data(data)
                if decoded is not None:   
                    del decoded["mac"]
                    #print(decoded)
                    keyList=list(decoded.keys())
                    #print(keyList)
                    valueList=list(decoded.values()) 
                    #print(valueList)
                    s="".join([str(x)+"," for x in valueList])
                    #print(s)
                    date=datetime.date.today()
                    with open("advertisment-{}.csv".format(date), 'a') as f:        
                        f.write("{}{},{}".format(s,mac,current_time.isoformat()))
                        f.write("\n")    
           
    except KeyboardInterrupt:
        # When Ctrl+C is pressed execution of the while loop is stopped
        print('Exit')
        break
