from gateway import hub
import time
from enum import Enum

# find tags
myhub = hub.hub()
myhub.discover()

# Pick one of the tags
sensor1 = myhub.sensorlist[0]
print(type(sensor1))

# Get basic sensor configurations
sensor1.get_config()
print(sensor1.sensor_data)

# set config 
sensor1.set_config(sampling_rate = 100, sampling_resolution = 12, measuring_range = 16, divider = 20)
#time.sleep(2)

# get config - did it work?
sensor1.get_config()
print(sensor1.sensor_data)
# last_val = sensor1.sensor_data[0][len(sensor1.sensor_data[0]) - 1]
# print(last_val)
print("Exit")


