from gateway import hub
import time

#find tags
myhub = hub.hub()
myhub.discover()

#Pick one of the tags
sensor1 = myhub.sensorlist[0]

#Get heardbeat
sensor1.get_heartbeat()

print("finish")