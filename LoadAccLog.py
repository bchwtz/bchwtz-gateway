from ruuvitag_sensor.ruuvi import RuuviTagSensor, RunFlag
import time
from interruptingcow import timeout
import pygatt
import logging
from binascii import hexlify
import crcmod

logging.basicConfig()
#logging.getLogger('pygatt').setLevel(logging.DEBUG)

macSet=set()
macList=[]
readAllString="FA04000000000000000000"
uuIdWrite="6e400002-b5a3-f393-e0a9-e50e24dcca9e"
uuIdRead="6e400003-b5a3-f393-e0a9-e50e24dcca9e"
waitTime=1
test=RuuviTagSensor._get_ruuvitag_datas(search_duratio_sec=2)
cnt=0
taskrun=True

crcfun = crcmod.mkCrcFun(0x11021, rev=False, initCrc=0xffff, xorOut=0)

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
        
        if(value.startswith(b'\xfc')):
            # Daten
            handle_data.sensordaten.extend(value[1:])
            print("Received data block: %s" % hexlify(value[1:]))
            
        elif(value.startswith(b'\xfb\x01\x00')):
            # Datenende
            crc = value[11:13];
            print("Received CRC: %s" % hexlify(crc))
            
            # CRC prüfen
            ourcrc = crcfun(handle_data.sensordaten)
            print("Recalculated CRC: %x" % ourcrc)
            
            # Anzahl Bytes
            print("Received %d bytes" % len(handle_data.sensordaten))
            
            # Auslesen beenden
            device.unsubscribe(uuIdRead)
            
    # Speicher für Daten
    handle_data.sensordaten = bytearray();
    
    # Antwort einlesen
    device.subscribe(uuIdRead, callback=handle_data)


if __name__ == '__main__':
    mac=findTagsMac()
    print("Macs found: " + str(mac))
    adapter = pygatt.GATTToolBackend()
    adapter.start()

    for i in mac:    
        ConnectToMac(adapter,i)

    while(taskrun):
        time.sleep(waitTime)
        print("Waitdone")    

