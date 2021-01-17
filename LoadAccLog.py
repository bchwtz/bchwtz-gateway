from ruuvitag_sensor.ruuvi import RuuviTagSensor, RunFlag
import time
from interruptingcow import timeout
import pygatt
import logging
from binascii import hexlify

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



def crc16(data: bytes, poly=0x8408):
    '''
    CRC-16-CCITT Algorithm from https://gist.github.com/oysstu/68072c44c02879a2abf94ef350d1c7c6
    '''
    data = bytearray(data)
    crc = 0xFFFF
    for b in data:
        cur_byte = 0xFF & b
        for _ in range(0, 8):
            if (crc & 0x0001) ^ (cur_byte & 0x0001):
                crc = (crc >> 1) ^ poly
            else:
                crc >>= 1
            cur_byte >>= 1
    crc = (~crc & 0xFFFF)
    crc = (crc << 8) | ((crc >> 8) & 0xFF)
    
    return crc & 0xFFFF
    

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
            ourcrc = crc16(handle_data.sensordaten)
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

