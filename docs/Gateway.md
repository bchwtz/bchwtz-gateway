# Gateway 
The gateway has three different tasks:

1. Manipulate the state of one or more sensors via control messages
2.	Receive acceleration data from one or more sensors, parse and store them
3.	Logging Bluetooth advertisements from sensors

For the first two tasks there is the “SensorGatewayBleak” library. All Code is written in python. You need the following libraries to run the “SensorGatewayBleak” library:

	asyncio
	nest_asyncio
	bleak 
	bluez 
	crcmod

The “AdvertisementLogging” function need the following libraries:

    ruuvitag_sensor
    bluez    
    pygatt

## Sensor Gateway Communication Library ##
This library is used for communication between the gateway and the sensors. It sends messages to the sensor to change their state or to get their data. The library has the following functions. This functions take message objects as argument. This message object must fit the needed message object to be processed.


### Activate acceleration logging 

The “activate_logging_at_sensor()” function activates logging at all sensors in Bluetooth range of the gateway. It takes a send_activate_logging_object as argument. To activate the logging, the gateway sends a control acceleration logging (\@ref(control-acceleration-logging)) message to the target sensor via the send_activate_logging_object. The message content is `0x4A 0x4A 0x08 0x01`. If Logging is already activated an error message (\@ref(status-response)) will be received as a status_object. 

### Deactivate acceleration logging 

The “deactivate_logging_at_sensor()” function deactivates logging at all sensors in Bluetooth range. It takes a send_deactivate_logging_object as argument. To deactivate the logging, the gateway sends a control acceleration logging (\@ref(control-acceleration-logging)) message to the target sensor via the send_deactivate_logging_object. The message content is `0x4A 0x4A 0x08 0x00`. Stopping the logging cause a deletion of all flash pages. If Logging is not activated an error message (\@ref(status-response)) will be received a status_object.


### Set sensor configuration 
With the “set_config_sensor()” function three sensor properties can be manipulated:

1. Sampling rate (sampling_rate): Measuring interval of the sensor. Allowed values can be found in Chapter (\@ref(set-configuration-of-acceleration-sensor)). 
2. Sampling resolution (sampling_resolution): Resolution of the measured values. Allowed values can be found in Chapter (\@ref(set-configuration-of-acceleration-sensor)).
3. Measuring range(measuring_range): Measuring range. Allowed values can be found in Chapter (\@ref(set-configuration-of-acceleration-sensor)). The returned message will be saved in a status message object.
4. Frequenzy divider(divider): The divider is used to get sample frequencies that are not supported by the sampling rate.


The configuration will be sent via a “Set configuration of acceleration sensor” (\@ref(set-configuration-of-acceleration-sensor)) message to all sensors in Bluetooth range. It takes a send_set_config_object as argument.
Only arguments with allowed values will be set. All others stay as they are. After setting the configuration all flash pages will be deleted. This can cause a loss of data. The Sensor send a status response message (\@ref(status-response)) to the gateway if the configuration was set successful or not. The returned message will be saved as a status_object.


### Set sensor time 

With the “set_sensor_time() “ function all sensors in Bluetooth range will be set to the current time in UTC. It takes a send_set_sensor_time_object as argument. To set the sensor time a “Set system time” (\@ref(set-system-time)) message, with the current time, will be send via send_set_sensor_time_object. After setting the sensor time all flash pages will be deleted. This can cause a loss of data. The Sensor send a response message (\@ref(ble-gatt-messages.html#status-response)) to the gateway if the time was set successful or not. The returned message will be saved in a status_object.


### Get sensor configuration 
The “get_config_from_sensor()”send a “Read configuration of acceleration sensor” (\@ref(read-configuration-of-acceleration-sensor)) message to the target sensor via a send_get_config_object. The sensor returns with a “Configuration response” (\@ref(configuration-response)) message which is storred in config_object.


### Get sensor time 
The “get_time_from_sensor()” function returns the current time from all sensors in Bluetooth range as a time_object. It takes a send_get_senor_time_object as argument. The function sends a “Read system time” (\@ref(read-system-time)) message to all targets and receives “Timestamp response” (\@ref(timestamp-response)) messages which is stored in a time_object.


### Get acceleration data 
The “get_acceleration_data()” collect all samples from the defined mac adresses in the send_get_acceleration_data_object in Bluethooth range. It returns a advertisement_data_object. To do this, the gateway sends a “Start transmitting logged data” (\@ref(start-transmitting-logged-data) Message to all targets and receives the data which are followed by an “End of data message” (\@ref(end-of-data-message)). The returned Message will be saved in an acceloration_data_object.

### Get flash statistics
With the “get_flash_statistic()” function you can access important information from the internal flash memory of the sensor (\@ref(query-flash-statistic)). It takes a send_get_flash_statistics_object as argument.The returned message will be saved in a flash_statistics_object.

### Get logging status
The “get_logging_status()” function is used to identify if a sensor is currently logging or if logging is deactivated. It returns a status_object. It takes a send_get_logging_status_object as argument.

	1 = logging is active
	0 = logging is not active


## Advertisement logging 
This executable is used for logging all advertisements that are send from any sensor in the Bluetooth rang. It parses the messages the gateway receives in a human readable design and stores it in a Csv file. The “decode_data()” function from the ruuvitag_sensor library is used to parse the received messages from the sensors.

## Data storage format 
For an easy access, the received advertisement data is stored in csv files. 
Acceleration data can be saved in csv as well or store the acceleration data message object. We recommend the following structure to save the files: 

### Csv file acceleration Logging 
Five values will be stored in these Csv files. These values are:

    •	Acceleration in X directory
    •	Acceleration in Y directory
    •	Acceleration in Z directory
    •	Timestamp
    •	Mac address
The name of the Csv file will be “acceleration” plus the observation time.

### Csv file advertisement  Logging 
Fourteen values will be stored in these Csv files. These values are:

    •	Data format
    •	Humidity
    •	Temperature in °C
    •	Pressure in Pa
    •	Acceleration
    •	Acceleration in X directory
    •	Acceleration in Y directory
    •	Acceleration in Z directory
    •	Tx power in dBm
    •	Battery in mV
    •	Movement counter
    •	Measurement sequence
    •	Mac address
    •	Timestamp
    
The name of the Csv file is the date of the observation. One Csv file will only include observations from one day. 
