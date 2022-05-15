from tokenize import String
from gateway import hub
import time
import argparse
from enum import Enum
import asyncio
import os
import sys
import signal
import time


# define command line arguments with flags
parser = argparse.ArgumentParser()
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
print(sensor1.mac)
sensor1.get_config()
print(sensor1.sensor_data)

# initialize streamdata loop
loop = sensor1.main_loop
loop.run_until_complete(sensor1.setup_for_streaming())
print("setup completed")

# start receiving streamdata
loop.run_until_complete(sensor1.activate_streaming())
print("listening for incoming data")
def sigint_handler(signal, frame):
    print ('KeyboardInterrupt is caught - exiting gracefully')
    sensor1.stopevent.set()
    time.sleep(2)
    sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)

# write csv and wait for all data, then finish and exit 
loop.run_until_complete(sensor1.listen_for_data(10*60))
print("Exit")


