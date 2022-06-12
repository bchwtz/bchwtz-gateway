from gateway import hub

myhub = hub.Hub()

myhub.discover()

sensor1 = myhub.sensorlist[0]

print(type(sensor1))

sensor1.get_time()

myhub.listen_advertisements() # press enter to confirm

print("Exit")

