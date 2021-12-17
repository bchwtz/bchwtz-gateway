from gateway import hub
import time
import argparse
from enum import Enum

# define command line arguments with flags
parser = argparse.ArgumentParser()
parser.add_argument("-srate", "--sample-rate", dest = "samplerate", default = 1, help="defines sample rate")
parser.add_argument("-reso", "--sample-resolution", dest = "resolution", default = 8, help="defines sample resolution")
parser.add_argument("-mrange", "--measuring_range", dest = "measurerange", default = 4, help="defines measure range/scale")
#parser.add_argument("-div", "--divider", dest = "divider", default = 0, help="defines divider", type=int)

args = parser.parse_args()

# find tags
myhub = hub.hub()
myhub.discover()

# Pick one of the tags
sensor1 = myhub.sensorlist[0]
print(type(sensor1))

# Reset logging status 
sensor1.deactivate_accelerometer_logging()
time.sleep(5)

# Start logging
sensor1.activate_accelerometer_logging()
time.sleep(5)

# Get basic sensor configurations
sensor1.get_config()
print(sensor1.sensor_data)

# set config 
sensor1.set_config(sampling_rate = args.samplerate, sampling_resolution = args.resolution, measuring_range = args.measurerange)

# get config - did it work?
sensor1.get_config()
print(sensor1.sensor_data)

# Deactivate logging
sensor1.deactivate_accelerometer_logging()
time.sleep(5)

print("Exit")


