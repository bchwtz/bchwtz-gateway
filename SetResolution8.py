from ruuvitag_sensor.ruuvi import RuuviTagSensor, RunFlag
import time
from interruptingcow import timeout
import pygatt
import logging
from binascii import hexlify

logging.basicConfig()
logging.getLogger('pygatt').setLevel(logging.INFO)

macSet=set()
macList=[]
readAllString="FAFA06FF08FF0000F40000"
uuIdWrite="6e400002-b5a3-f393-e0a9-e50e24dcca9e"
uuIdRead="6e400003-b5a3-f393-e0a9-e50e24dcca9e"
waitTime=1
test=RuuviTagSensor._get_ruuvitag_datas(search_duratio_sec=2)
cnt=0

def ri_error_to_string(error):
    result = set()
    if(error==0):
        result.add("RD_SUCCESS")
    else:
        if(error & (1<<0)):
            result.add("RD_ERROR_INTERNAL")
        if(error & (1<<1)):
            result.add("RD_ERROR_NO_MEM")
        if(error & (1<<2)):
            result.add("RD_ERROR_NOT_FOUND")
        if(error & (1<<3)):
            result.add("RD_ERROR_NOT_SUPPORTED")
        if(error & (1<<4)):
            result.add("RD_ERROR_INVALID_PARAM")
        if(error & (1<<5)):
            result.add("RD_ERROR_INVALID_STATE")
        if(error & (1<<6)):
            result.add("RD_ERROR_INVALID_LENGTH")
        if(error & (1<<7)):
            result.add("RD_ERROR_INVALID_FLAGS")
        if(error & (1<<8)):
            result.add("RD_ERROR_INVALID_DATA")
        if(error & (1<<9)):
            result.add("RD_ERROR_DATA_SIZE")
        if(error & (1<<10)):
            result.add("RD_ERROR_TIMEOUT")
        if(error & (1<<11)):
            result.add("RD_ERROR_NULL")
        if(error & (1<<12)):
            result.add("RD_ERROR_FORBIDDEN")
        if(error & (1<<13)):
            result.add("RD_ERROR_INVALID_ADDR")
        if(error & (1<<14)):
            result.add("RD_ERROR_BUSY")
        if(error & (1<<15)):
            result.add("RD_ERROR_RESOURCES")
        if(error & (1<<16)):
            result.add("RD_ERROR_NOT_IMPLEMENTED")
        if(error & (1<<16)):
            result.add("RD_ERROR_SELFTEST")
        if(error & (1<<18)):
            result.add("RD_STATUS_MORE_AVAILABLE")
        if(error & (1<<19)):
            result.add("RD_ERROR_NOT_INITIALIZED")
        if(error & (1<<20)):
            result.add("RD_ERROR_NOT_ACKNOWLEDGED")
        if(error & (1<<21)):
            result.add("RD_ERROR_NOT_ENABLED")
        if(error & (1<<31)):
            result.add("RD_ERROR_FATAL")
    return result
        

def findTagsMac():
    macSet=set()
    cnt=0
    try:
        with timeout(10, exception=RuntimeError):
            while True:
                tags=RuuviTagSensor._get_ruuvitag_datas(search_duratio_sec=3)
                for tag in tags:
                    #print(tag)
                    macSet.add(tag[0])    
                    cnt+=1
                    print(cnt)
                print("Out")
                return macSet
    except RuntimeError:
        print("Out")
        return macSet
        pass
    
    
def ConnectToMac(adapter,i):

    device = adapter.connect(i,address_type=pygatt.BLEAddressType.random)
    print("Connection established")
    
    # Daten vom Tag abfragen
    test=device.char_write(uuid=uuIdWrite, value=bytearray.fromhex(readAllString))

    def handle_data(handle, value):
        """
        handle -- integer, characteristic read handle the data was received on
        value -- bytearray, the data returned in the notification
        """
        
        # Daten
        if(value[1]==0x00):
            print("Status: %s" % str(ri_error_to_string(value[2])))
        else:
            print("Antwort enthält falschen Typ")
            
        # Auslesen beenden
        device.disconnect()
        ConnectToMac.taskrun=False

    # Antwort einlesen
    device.subscribe(uuIdRead, callback=handle_data)


if __name__ == '__main__':
    mac=findTagsMac()
    print("Macs found: " + str(mac))
    adapter = pygatt.GATTToolBackend()
    adapter.start()

    for i in mac:    
        ConnectToMac(adapter,i)   

    ConnectToMac.taskrun=True
    
    while(ConnectToMac.taskrun):
        time.sleep(waitTime)
        print("Waitdone")    

    adapter.stop()
