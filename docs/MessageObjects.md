# MessageObjects

The message classes should help to communicate with the backend via mqtt. For this task we need to decode the message into json and decode it back to a class later. Additionally, it makes the gateway library more dynamic.
There are two types:
``` 
return_values_from_sensor
send_msg_object
```
	
## return_values_from_sensor

This class takes the returning messages from the sensors and converts them in one of the following objects:
```
time_object
config_object
flash_statistics_object
status_object
acceloration_data_object
advertisement_data_object
```

Depending on the called constructor this objects can be called via return_values_from_sensor.returnValue. 

Objects:
> time_object: consist of a status, the received time from the sensor and the sensor mac.
> config_object: consist of a status, the config parameters from the sensor and the sensor mac.
> flash_statistics_object: consist of a status, the flash statistic parameters from the sensor and the sensor mac.
> status_object: consist of a status.
> acceloration_data_object: consists of the received acceleration data and the sensor mac.
> advertisement_data_object: consists of the current time, the advertisement data from the sensor and the mac address form the sensor

## send_msg_object

To communicate with the sensor, you must send the right message object. These message object must be one of the following: 
```	
send_set_sensor_time_object
send_set_config_object
send_activate_logging_object
send_deactivate_logging_object
send_get_config_object
send_get_senor_time_object
send_get_flash_statistics_object
send_get_logging_status_object
send_get_acceleration_data_object
send_activate_advertisement_logging_object
```

All these objects take the targeted mac and a command string. The targeted mac can be a single mac address, multiple macs addresses as list or an empty string. In the last case the command is send to all tags in range.  The only purpose of this class is to differentiate between the different commands which are sent to the sensors. 
To initialize this object the specific constructor in send_msg_objects must be called.  
