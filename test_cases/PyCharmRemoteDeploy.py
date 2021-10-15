import json
import time
from multiprocessing import Process, Event
import sys
import jsonpickle
from json import JSONEncoder
from gateway import SensorGatewayBleak, MessageObjects
from gateway import AdvertisementLogging



"""
Uncomment the below code to test advertisement logging and sensor communication at the same time.
This process needs multithreading to run the advertisement logging in background and not blocking the main thread.
"""
# def thr2(kill_event):
#     #AdvertisementLogging.advertisement_logging()
#     print("thread 2")
#     currentLogging=False
#     while True:
#         if kill_event.is_set():
#             print("kill2")
#             sys.exit(0)
#         if not currentLogging:
#             print("advertisements")
#             AdvertisementLogging.advertisement_logging()
#             currentLogging=True
#
# if __name__ == "__main__":
#     kill_event = Event()
#     thread2 = Process(target=thr2, args=[kill_event])
#     thread2.start()
#     cnt=0
#
#     while True:
#         if kill_event.is_set():
#             print('kill')
#             thread2.kill()
#             sys.exit(0)
#         cnt+=1
#         if cnt>200:
#             test = SensorGatewayBleak.RuuviTagAccelerometerCommunicationBleak()
#             test.set_sensor_time()
#             abc = test.get_time_from_sensor()
#             print(abc)
#             print("kill")
#             kill_event.set()
#         time.sleep(0.4)


# test= SensorGatewayBleak.RuuviTagAccelerometerCommunicationBleak()
# test.activate_debug_logger()
# msg_object=MessageObjects.send_msg_object()
# msg_object=msg_object.to_deactivate_logging()
# ret_msg=test.deactivate_logging_at_sensor(msg_object.message)
# print(ret_msg)
# time.sleep(5)
# msg_object=MessageObjects.send_msg_object()
# msg_object=msg_object.to_get_logging_status()
# ret_msg=test.get_logging_status(msg_object.message)
# print(ret_msg)
test= SensorGatewayBleak.RuuviTagAccelerometerCommunicationBleak()


msg_object=MessageObjects.send_msg_object()
msg_object=msg_object.to_set_sensorConfig(sampling_rate=30,sampling_resolution=150, measuring_range=8)
jsonStr = json.dumps(msg_object.message.__dict__)
print("Json dump: ",jsonStr)
studentJSON = jsonpickle.encode(msg_object.message)
print("Encoded msg object:",studentJSON)
studentObject = jsonpickle.decode(studentJSON)
print("Object type is: ", type(studentObject))
test.set_config_sensor(studentObject)

time.sleep(10)
msg_object=MessageObjects.send_msg_object()
msg_object=msg_object.to_get_config()
jsonStr = json.dumps(msg_object.message.__dict__)
print("Json dump: ",jsonStr)
studentJSON = jsonpickle.encode(msg_object.message)
print("Encoded msg object:",studentJSON)
studentObject = jsonpickle.decode(studentJSON)
print("Object type is: ", type(studentObject))
abc=test.get_config_from_sensor(studentObject)
print(abc)
# test=json.loads(jsonStr)
# print(type(test))
# safasf=AdvertisementLogging.advertisementLogging()
# safasf.start_advertisement_logging()
# print("abs")
# test= SensorGatewayBleak.RuuviTagAccelerometerCommunicationBleak()
# test.set_sensor_time()
# abc=test.get_time_from_sensor()
# print(abc)
# # print("-------------------------di-\n")
# #test.activate_debug_logger()
# abc=test.set_config_sensor(sampling_rate=30,sampling_resolution=150, measuring_range=8)
# print(abc)
# dcf=test.get_config_from_sensor()
# print(dcf
#       )
# time.sleep(3)
# abc=test.activate_logging_at_sensor()
# print(abc)
#test.activate_logging_at_sensor()
"""
All command functions can take a mac address as string or as a list of strings.
"""
# anc=test.get_logging_status()
# print(anc)
# dfg=test.get_time_from_sensor()
# print(dfg)
# abc=test.get_config_from_sensor()
# print(abc)
# abc=test.get_flash_statistic()
# print(abc)
# test.set_config_sensor(sampling_rate=10,sampling_resolution=10, measuring_range=4)
#["F8:D8:72:8F:83:0F","C2:0D:4D:C6:87:BE"]

# abc=test.get_config_from_sensor()
# print(abc)

# print("--------------------------\n")
# test.activate_debug_logger()
# test.set_config_sensor(sampling_rate=50,sampling_resolution=12, measuring_range=4)
#
# abc=test.get_config_from_sensor()
# print(abc)


#
#
# abc=test.get_time_from_sensor()
# print(abc)
#
# test.deactivate_debug_logger()
# abc=test.get_flash_statistic()
# print(abc)
#
# test.activate_logging_at_sensor()
# time.sleep(5)
# print("Sleep over")
# test.activate_debug_logger()
# abc=test.get_acceleration_data()
# print(abc[0])
# print("")
# print("-----------------------------------------------------")
# print("")
# print(abc[1])

# abc=test.get_logging_status()
# print(abc)
# test.get_time_from_sensor()
#test.activate_logging_at_sensor()
#test.set_config_sensor(sampling_rate=200)
# test.get_logging_status()
# test.get_flash_statistic()
# test.deactivate_logging_at_sensor()

# test.get_time_from_sensor("D2:79:15:52:1F:19")
#test.get_time_from_sensor()
#time.sleep(10)
# test.get_acceleration_data()
# print("-------------------")
# time.sleep(10)
# test.get_acceleration_data()
#+test.set_config_sensor(sampling_rate=1,sampling_resolution=12,measuring_range=4, divider=10)
#test.get_time_from_sensor()
#test.set_sensor_time()
#test.get_time_from_sensor()
"D2:79:15:52:1F:19"