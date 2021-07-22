from ruuvitag_sensor.ruuvi import RuuviTagSensor, RunFlag
from datetime import timezone
import datetime
import time
from interruptingcow import timeout
import pygatt
import logging
from binascii import hexlify

logging.basicConfig()
#logging.getLogger('pygatt').setLevel(logging.DEBUG)

macSet=set()
macList=[]
readAllString="FAFA090000000000000000"
uuIdWrite="6e400002-b5a3-f393-e0a9-e50e24dcca9e"
uuIdRead="6e400003-b5a3-f393-e0a9-e50e24dcca9e"
waitTime=1
test=RuuviTagSensor._get_ruuvitag_datas(search_duratio_sec=2)
cnt=0

dt = datetime.datetime.now()
print(dt)
timestamp = dt.replace(tzinfo=timezone.utc).timestamp()
print(hex(int(timestamp)))
hexUnixTime=hex(int(timestamp))[2:]
