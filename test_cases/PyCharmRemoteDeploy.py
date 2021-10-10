import time

import asyncio
from gateway import SensorGatewayBleak, MessageObjects
from gateway import AdvertisementLogging
#

safasf=AdvertisementLogging.advertisementLogging()
print(safasf.start_advertisement_logging())
print("abs")
test= SensorGatewayBleak.RuuviTagAccelerometerCommunicationBleak()
test.set_sensor_time()
abc=test.get_time_from_sensor()
print(abc)
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