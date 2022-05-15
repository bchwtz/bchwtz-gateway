from tokenize import String
from gateway import hub
import time
import argparse
from enum import Enum
import asyncio

# define command line arguments with flags
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--sampling_rate", dest = "samplerate", default = 1, help="defines sample rate, accepted values are: 1, 10, 25, 50, 100, 200, 400", type = int)
parser.add_argument("-r", "--sampling_resolution", dest = "resolution", default = 8, help="defines sample resolution, accepted values are: 8, 10, 12", type = int)
parser.add_argument("-m", "--measuring_range", dest = "measurerange", default = 4, help="defines measure range/scale, accepted values are: 2, 4, 8, 16", type = int)
parser.add_argument("-d", "--divider", dest = "divider", default = 1, help = "defines divider, any positive integer accepted", type = int)
parser.add_argument("-a", "--address", dest = "address", default = None, help = "defines specific MAC address for a sensor", type = str)
parser.add_argument("-t", "--timeout", dest = "timeout", default = 5.0, help = "defines sensor discovery timeout", type = float)

args = parser.parse_args()
print(args)

# find tags
myhub = hub.Hub()
myhub.discover(args.timeout)

# Pick one of the tags manually or automatically
if args.address is not None:
    sensor1 = myhub.get_sensor_by_mac(args.address)
    if sensor1 is None:
        print("ERROR: Sensor with address %s could not be found!" % args.address)
else:
    sensor1 = myhub.sensorlist[0]
    print(type(sensor1))

# Get basic sensor configurations
sensor1.get_config()
print(sensor1.sensor_data)

# set config 
sensor1.set_config(sampling_rate = args.samplerate, sampling_resolution = args.resolution, measuring_range = args.measurerange, divider = args.divider)

# get config - did it work?
sensor1.get_config()
print(sensor1.sensor_data[-2:])

