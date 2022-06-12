# from gateway import hub
# import time 
# from bleak import BleakClient
# import asyncio

# UART_RX = '6E400003-B5A3-F393-E0A9-E50E24DCCA9E' 

# class Sensor:
#     def __init__(self, name : str, mac : str):
#         self.name = name
#         self.mac = mac
#         self.client = None
    
#     async def connect(self):
#         async with BleakClient(self.mac) as client:
#             self.client = client
#             print(f"Connected: {client.is_connected}")
#             await client.start_notify(
#                 UART_RX, 
#                 self.notification_handler
#                         )
            
            

#     def getHeartbeat(self):
#         print(self.client.is_connected)

#     async def disconnect(self):
#         await self.client.stop_notify(UART_RX)
#         self.client.disconnect()

#     def notification_handler(sender, data, data_1):
#         print(str(data) + "//" + str(data_1))




# myhub = hub.Hub()
# myhub.discover()

# mac = 'DD:51:1E:E1:15:D4'
# name = 'ruvii'
# sensor = Sensor(name, mac)
# asyncio.run(sensor.connect())
# time.sleep(10)
# # sensor.getHeartbeat()
# asyncio.run(sensor.disconnect())

# input("Press a button...")


# sensors = []
# for sensor in myhub.sensorlist:
#     print(sensor.mac + "   " + sensor.name)
    
#     if sensor.mac == mac:
#         sensor.set_config(sampling_rate = 50, sampling_resolution = 12, measuring_range = 4, divider = 1 )
#         sensors.append(sensor)

# for sensor in sensors:
#     print("Will log sensor: " + sensor.mac + " // " + sensor.name)

# for sensor in sensors:
#     sensor.activate_accelerometer_logging()

# input("Press enter to continue...")

# for sensor in sensors:
#     sensor.deactivate_accelerometer_logging()


from gateway import hub

myhub = hub.Hub()

myhub.discover()

sensor1 = myhub.sensorlist[0]

print(type(sensor1))

sensor1.get_time()

myhub.listen_advertisements() # press enter to confirm

print("Exit")