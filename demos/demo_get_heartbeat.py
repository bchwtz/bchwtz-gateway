from gateway import hub
import time

#find tags
myhub = hub.Hub()
myhub.discover()

#pick one of the tags
sensor1 = myhub.sensorlist[0]

#Get heartbeat
sensor1.get_heartbeat()

print("finish")

#set heartbeat
# sensor1.set_heartbeat(1000) # 1 second