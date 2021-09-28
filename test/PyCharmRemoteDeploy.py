import asyncio
from gateway import SensorGatewayBleak, AdvertisementLogging

#AdvertisementLogging.start_advertisement_logging()



test= SensorGatewayBleak.RuuviTagAccelerometerCommunicationBleak()
# print("--------------------------\n")
test.activate_debug_logger()
#test.activate_logging_at_sensor()
"""
All command functions can take a mac address as string or as a list of strings.
"""
dfg=test.get_config_from_sensor()
print(dfg)
# abc=test.get_acceleration_data()
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