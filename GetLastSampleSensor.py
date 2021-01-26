from ruuvitag_sensor.ruuvi import RuuviTagSensor, RunFlag
import time
from interruptingcow import timeout
import pygatt
import logging
from binascii import hexlify
import crcmod

logging.basicConfig()
#logging.getLogger('pygatt').setLevel(logging.INFO)

macSet=set()
macList=[]
readAllString="FAFA030000000000000000"
uuIdWrite="6e400002-b5a3-f393-e0a9-e50e24dcca9e"
uuIdRead="6e400003-b5a3-f393-e0a9-e50e24dcca9e"
waitTime=1
test=RuuviTagSensor._get_ruuvitag_datas(search_duratio_sec=2)
cnt=0

crcfun = crcmod.mkCrcFun(0x11021, rev=False, initCrc=0xffff, xorOut=0)

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
    

def unpack10(bytes, scale):
    j = 0;
    koords = [ "\nx", "y", "z" ]
    
    if(scale==2):
        print("Scale: 2G")
        faktor = 4/(64*1000)
    elif(scale==4):
        print("Scale: 4G")
        faktor = 8/(64*1000)
    elif(scale==8):
        print("Scale: 8G")
        faktor = 16/(64*1000)
    elif(scale==16):
        print("Scale: 16G")
        faktor = 48/(64*1000)
        
    for i in range(int(len(bytes)/5)):
        value = bytes[ i*5 ] & 0xc0
        value |= (bytes[ i*5 ] & 0x3f) << 10
        value |= (bytes[ 1 + i*5 ] & 0xc0) << 2
        if(value & 0x8000 == 0x8000):
            # negative Zahl
            # 16Bit Zweierkomplement zurückrechnen
            value = value ^ 0xffff
            value += 1
            # negieren
            value = -value
        value *= faktor
        print("%s = %f" % (koords[j%3], value))
        j += 1
        value = (bytes[ 1 + i*5 ] & 0x30) << 2
        value |= (bytes[ 1 + i*5 ] & 0x0f) << 12
        value |= (bytes[ 2 + i*5 ] & 0xf0) << 4
        if(value & 0x8000 == 0x8000):
            # negative Zahl
            # 16Bit Zweierkomplement zurückrechnen
            value = value ^ 0xffff
            value += 1
            # negieren
            value = -value
        value *= faktor
        print("%s = %f" % (koords[j%3], value))
        j += 1
        value = (bytes[ 2 + i*5] & 0x0c) << 4
        value |= (bytes[ 2 + i*5 ] & 0x03) << 14
        value |= (bytes[ 3 + i*5 ] & 0xfc) << 6
        if(value & 0x8000 == 0x8000):
            # negative Zahl
            # 16Bit Zweierkomplement zurückrechnen
            value = value ^ 0xffff
            value += 1
            # negieren
            value = -value
        value *= faktor
        print("%s = %f" % (koords[j%3], value))
        j += 1
        value = (bytes[ 3 + i*5 ] & 0x03) << 6
        value |= (bytes[ 4 + i*5 ]) << 8
        if(value & 0x8000 == 0x8000):
            # negative Zahl
            # 16Bit Zweierkomplement zurückrechnen
            value = value ^ 0xffff
            value += 1
            # negieren
            value = -value
        value *= faktor
        print("%s = %f" % (koords[j%3], value))
        j += 1
    print("\n%d Werte entpackt" % (j,))
    
    
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
        if(value.startswith(b'\xfc')):
            # Daten
            handle_data.sensordaten.extend(value[1:])
            print("Received data block: %s" % hexlify(value[1:]))
            
        elif(value.startswith(b'\xfb')):
            # Status
            print("Status: %s" % str(ri_error_to_string(value[2])))
            
            # Datenende
            crc = value[11:13];
            print("Received CRC: %s" % hexlify(crc))
            
            # CRC prüfen
            ourcrc = crcfun(handle_data.sensordaten)
            print("Recalculated CRC: %x" % ourcrc)
            
            # Anzahl Bytes
            print("Received %d bytes" % len(handle_data.sensordaten))
            
            # Auslesen beenden
            device.disconnect()
            ConnectToMac.taskrun=False
            
            # Der Timestamp ist little-endian (niegrigwertigstes Bytes zuerst) gespeichert
            # die menschliche Lesart erwartet aber big-endian (höchstwertigstes Bytes zuerst)
            # deswegen Reihenfolge umdrehen
            print("Timestamp: %s" % hexlify(handle_data.sensordaten[7::-1]))
            
            # Daten entpacken
            if(value[4]==12):
                # 12 Bit
                print("12 Bit Resolution")
            elif(value[4]==10):
                # 10 Bit
                print("10 Bit Resolution")
                unpack10(handle_data.sensordaten[8:], value[5])
            elif(value[4]==8):
                # 8 Bit
                print("8 Bit Resolution")
            else:
                print("unbekannte Resolution")
            
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

    ConnectToMac.taskrun=True
    
    while(ConnectToMac.taskrun):
        time.sleep(waitTime)
        print("Waitdone")    

    adapter.stop()
