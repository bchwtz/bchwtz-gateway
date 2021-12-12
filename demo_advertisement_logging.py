from gateway import sensor_hub

myhub = sensor_hub.sensor_hub()

myhub.discover_neighborhood()

sensor1 = myhub.sensorlist[0]

print(type(sensor1))

sensor1.get_sensor_time()

myhub.listen_advertisements() # press any key to confirm

