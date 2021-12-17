from gateway import hub
import time

#find tags
myhub = hub.hub()
myhub.discover()

#Pick one of the tags
sensor1 = myhub.sensorlist[0]
print(type(sensor1))

#Reset logging status 
sensor1.deactivate_accelerometer_logging()
time.sleep(5)

#Start logging
sensor1.activate_accelerometer_logging()
time.sleep(5)

#Check Status
sensor1.get_logging_status()
time.sleep(5)

input("Press enter to continue...")

# Get basic sensor configurations
sensor1.get_config()
print(sensor1.sensor_data)
input("Press enter to continue...")

#Get acceleration data
sensor1.get_acceleration_data()
time.sleep(2)

print(sensor1.data)
print("Exit")
