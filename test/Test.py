from ruuvitag_sensor.ruuvi import RuuviTagSensor, RunFlag
from datetime import timezone
import datetime
import time
from interruptingcow import timeout
import pygatt
import logging

logging.basicConfig()
logging.getLogger('pygatt').setLevel(logging.DEBUG)

dt = datetime.datetime.now()
print(dt)
timestamp = dt.replace(tzinfo=timezone.utc).timestamp()
print(hex(int(timestamp)))
hexUnixTime=hex(int(timestamp))[2:]

macSet=set()
macList=[]
readAllString="3A3A11"
endTime="0"*8
print(endTime)
uuIdWrite="6e400002-b5a3-f393-e0a9-e50e24dcca9e"
waitTime=0
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




def ConnectToMac(adapter,i):
    adapter.start()
    try: 
        device = adapter.connect(i,address_type=pygatt.BLEAddressType.random)
        print("Connection established")
        device.subscribe
        valueTime=readAllString+str(hexUnixTime).upper()+str(endTime)
        print(valueTime)
        test=device.char_write(uuid=uuIdWrite, value=bytearray.fromhex(valueTime))
        print(test)
        #value = device.char_read("a1e8f5b1-696b-4e4c-87c6-69dfe0b0093b")
    finally:
        adapter.stop()

while(taskrun):
    time.sleep(waitTime)
    print("Waitdone")    
    mac=findTagsMac()
    print("Macs found")
    adapter = pygatt.GATTToolBackend()
    for i in mac:    
        ConnectToMac(adapter,i)
    print(mac)
