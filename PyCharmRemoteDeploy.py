import SensorGatewayBleak
import time
test= SensorGatewayBleak.RuuviTagAccelerometerCommunicationBleak()
print("--------------------------\n")

test.get_config_from_sensor()

# test.get_time_from_sensor("D2:79:15:52:1F:19")
#test.get_time_from_sensor()
#time.sleep(20)
#test.set_config_sensor(sampling_rate=400,sampling_resolution=12,measuring_range=4, divider=10)
#test.get_time_from_sensor()
#test.set_sensor_time()
#test.get_time_from_sensor()
"D2:79:15:52:1F:19"