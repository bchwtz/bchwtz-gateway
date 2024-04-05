# Sensor

The following figure shows the high level architecture of acceleration data logging in Ruuvi Tag. All configuration is done via the gateway. It communicates with the Ruuvi Tag using the Nordic UART interface via GATT messages transported by Bluetooth Low Energy (BLE). Most logic regarding acceleration logging is implemented inside the module [app_accelerometer_logging.c](sensor.html#app_accelerometer_logging.c).

![](imgs/wrapping_of_data_get.png)

Three use cases are shown in this figure.

## Initializing acceleration logging ##
The initialization is shown with blue arrows and numbers in black circles until #4. 

To activate acceleration logging the gateway sends the [control acceleration logging message](ble-gatt-messages.html#control-acceleration-logging). In general GATT messages are handled by the function [`handle_comms()`](sensor.html#void-handle_comms-const-ri_comm_xfer_fp_t-reply_fp-const-uint8_t-const-raw_message-size_t-data_len) inside the module [app_comm.c](sensor.html#app_comms.c). Messages regarding acceleration logging are delegated to the function [`handle_lis2dh12_comms_v2()`](sensor.html#rd_status_t-handle_lis2dh12_comms_v2-const-ri_comm_xfer_fp_t-reply_fp-const-uint8_t-const-raw_message-size_t-data_len) inside the same module. After receiving the message to activate acceleration logging the function [`app_enable_sensor_logging()`](sensor.html#rd_status_t-app_enable_sensor_loggingconst-bool-use_ram_db-const-bool-format_db) inside the module [app_accelerometer_logging.c](sensor.html#app_accelerometer_logging.c) in called (1).

The first step in activation is to check if all conditions are fulfilled. The function returns an error code if acceleration logging is already active or if it is called on a sensor which does not include an LIS2DH12. This check is done by calling [`find_sensor()`](sensor.html#rt_sensor_ctx_t-app_sensor_find-const-char-name) inside of [app_sensor.c](sensor.html#app_sensor.c) (2). This function returns the sensor context. The sensor context consists of several information about the sensor. The next step associates the function [`on_fifo_full()`](sensor.html#void-on_fifo_full-const-ri_gpio_evt_t-evt) from [app_accelerometer_logging.c](sensor.html#app_accelerometer_logging.c) with the interrupt pin retrieved from the sensor context (3). The last step is to activate FIFO and interrupt generation inside the LIS2DH12. This is done by calling two functions from the sensor context. At last the function pointer to `data_get()` inside the sensor context is replaced by the pointer to the function [`lis2dh12_logged_data_get()`](sensor.html#rd_status_t-lis2dh12_logged_data_get-rd_sensor_data_t-const-data). 

## Retrieving data from FIFO ##
When FIFO is full inside LIS2DH12 the interrupt starts the function [`on_fifo_full()`](sensor.html#void-on_fifo_full-const-ri_gpio_evt_t-evt). This function does not directly handle the new data. It schedules a call to [`fifo_full_handler()`](sensor.html#void-fifo_full_handler-void-p_event_data-uint16_t-event_size). Instead of [`on_fifo_full()`](sensor.html#void-on_fifo_full-const-ri_gpio_evt_t-evt) this is called in the main thread of the application. If processing is done inside a function inside an interrupt context this prevents processing of another interrupt. This should be avoided.

Inside [`fifo_full_handler()`](sensor.html#void-fifo_full_handler-void-p_event_data-uint16_t-event_size) the FIFO from LIS2DH12 is read (5). The values are store in memory in raw format to be ready to present them to the function [`lis2dh12_logged_data_get()`](sensor.html#rd_status_t-lis2dh12_logged_data_get-rd_sensor_data_t-const-data) which is important for heartbeat. In parallel the raw values are compacted by removing all unused bits. This is done by the function [`pack()`](sensor.html#void-packconst-uint8_t-resolution-const-uint16_t-sizedata-const-uint8_t-const-data-uint8_t-const-packeddata). These values are handover to the FlashDB which writes them to flash (6).

## Using the data by heartbeat ##
This use case is shown with magenta arrows and numbers inside magenta circles in the figure above.

The heartbeat retrieves the values from all sensors by calling the function `app_sensor_get()` inside the module [app_sensors.c](sensor.html#app_sensor.c). In the original setup this function calls [`ri_lis2dh12_data_get()`](sensor.html#rd_status_t-ri_lis2dh12_data_get-rd_sensor_data_t-const-data) inside [ruuvi_interface_lis2dh12.c](sensor.html#ruuvi_interface_lis2dh12.c). During initialization this function is replaced by [`lis2dh12_logged_data_get()`](sensor.html#rd_status_t-lis2dh12_logged_data_get-rd_sensor_data_t-const-data).

[`lis2dh12_logged_data_get()`](sensor.html#rd_status_t-lis2dh12_logged_data_get-rd_sensor_data_t-const-data) retrieves the raw acceleration values from memory. Then the values are parsed by calling [`ri_lis2dh12_raw_data_parse()`](sensor.html#rd_status_t-ri_lis2dh12_raw_data_parse-rd_sensor_data_t-const-data-axis3bit16_t-raw_acceleration-uint8_t-raw_temperature) and returned to the heartbeat.

## Initialization during boot ##
All sensor initialization is done inside [`setup()`](sensor.html#void-setup-void) from [main.c](sensor.html#main.c). This function calls [`app_acc_logging_init()`](sensor.html#rd_status_t-app_acc_logging_initvoid) inside [app_accelerometer_logging.c](sensor.html#app_accelerometer_logging.c). The function checks if the ringbuffer exists. If this is true it activates acceleration logging as described earlier.

## Streaming of acceleration data ##

In case of sampling acceleration data at high sampling frequencies than storing them in flash memory may be not possible because of latency of the memory or limitations by available size of memory. As an alternative the data can be streamed. In this mode, data from the acceleration sensor will not be written to flash. Instead the data is cached in RAM. For this purpose 6k RAM are dynamically allocated using `malloc()` during enabling of streaming. At the time of writing this documentation FlashDB lacks the feature of freeing memory which is used to store a database. Because of this missing feature the only way of freeing the memory used by streaming is to reboot the firmware.

The following figure shows the difference between logging of acceleration data and streaming.

![](imgs/streaming_of_acceleration_data.png)
When logging is active, the acceleration sensor LIS2DH12 generated an interrupt every time its FIFO is full. The interrupt causes the execution of [`on_fifo_full()`](sensor.html#void-on_fifo_full-const-ri_gpio_evt_t-evt). This function schedules the execution of [`fifo_full_handler()`](sensor.html#void-fifo_full_handler-void-p_event_data-uint16_t-event_size) outside interrupt context (grey). The following process was described [earlier](sensor.html#retrieving-data-from-fifo).

When streaming is active, the process is started by the same condition. But the FIFO is read by [`on_fifo_full()`](sensor.html#void-on_fifo_full-const-ri_gpio_evt_t-evt). Instead of scheduling [`fifo_full_handler()`](sensor.html#void-fifo_full_handler-void-p_event_data-uint16_t-event_size) the function hands over the data to FlashDB which stores them in RAM. This is done inside interrupt context (blue). In case of streaming there is no explicit command to read the data by the gateway. Instead, if connected to Bluetooth GATT service, the data is automatically send. This is done by scheduling [`app_acc_log_transfer_ram_db()`](sensor.html#void-app_acc_log_transfer_ram_db-void-p_event_data-uint16_t-event_size). [`on_fifo_full()`](sensor.html#void-on_fifo_full-const-ri_gpio_evt_t-evt) schedules execution of this function if `rt_gatt_nus_is_connected()` returns true.

## Saving the config inside the flashdb ##

To be able to report different sensor-config versions to the gateway, at different times, the current config is stored in the key-value-partition of the flashdb.
The configuration can be accessed via `rt_sensor_get_from_fdb` defined in [ruuvi_task_sensor.c](sensor.html#ruuvi_task_sensor.c).
The values will then be automatically loaded onto the sensor struct.
To save a config you will have to use `rt_sensor_store_to_fdb` defined in [ruuvi_task_sensor.c](sensor.html#ruuvi_task_sensor.c).

## Heartbeat ##
The heartbeat is an interval in which the sensor communicates via Bluetooth to the outside world. One of the most important facts about the heartbeat is that this is the only point in time a device can connect to the sensor. The default interval is around 800ms. However, the heartbeat can be get and set on sensor site with static methods `get_current_heartbeat()` and `app_heartbeat_start(uint16_t heartbeat_ms)` defined in [app_heartbeat.c](sensor.html#app_heartbeat.c).
Once the heartbeat is modified by hand (either from the sensor itself or from outside via Bluetooth messages) the new value is stored and will be applied directly and on every following reboot. Therefore it is advisable to be careful with modifying the heartbeat. 

## Implementation ##

### app_heartbeat.c ###

#### `uint16_t get_current_heartbeat(void)` ####

Get the current heartbeat.

#### `rd_status_t app_heartbeat_stop(void)` ####

Stop the heartbeat.
Note: This method should always be called before `app_heartbeat_start()` is called.


#### `rd_status_t app_heartbeat_start(uint16_t heartbeat_ms)` ####

Start and store the heartbeat with the new interval.

| Parameters |||
| - | - | - |
| heartbeat_ms | in | New interval for heartbeat in milliseconds. |

### ruuvi_task_sensor.c ###
#### `rd_status_t rt_sensor_get_from_fdb(fdb_kvdb_t kvdb, rt_sensor_ctx_t *sensor)` ####

Retrieves data from fdb-kv-partition and loads it onto the sensor struct.

#### `rd_status_t rt_sensor_store_to_fdb(fdb_kvdb_t kvdb, rt_sensor_ctx_t *sensor)` ####

Stores data from the sensor-struct to the kvdb, referencing the current timestamp.


### app_accelerometer_logging.c ###

#### `rd_status_t app_enable_sensor_logging(const bool use_ram_db, const bool format_db)` ####

Enables the logging of acceleration data.

| Parameters |||
| - | - | - |
| use_ram_db | in | Database in RAM is used in case of streaming of acceleration data. |
| format_db | in | This parameter is set to true if logging is enabled by gateway to ensure the database is cleared. When re-enabling logging after reboot it is set to false. |

| Special error codes |||
| - | - | - |
| RD_ERROR_INVALID_STATE | If logging is already enabled. |
| RD_ERROR_NOT_FOUND | If LIS2DH12 is not available. |

#### `rd_status_t app_disable_sensor_logging(void)` ####

Disables the logging of acceleration data.

| Special error codes ||
| - | - |
| RD_ERROR_INVALID_STATE | If logging is already disabled. |
| RD_ERROR_NOT_FOUND | If LIS2DH12 is not available. |

#### `void on_fifo_full (const ri_gpio_evt_t evt)` ####

Callback function when FIFO full interrupt occurs at LIS2DH12. If using streaming this function reads the FIFO and writes the values to RAMDB. 

Without streaming it schedules the execution of [`void fifo_full_handler (void * p_event_data, uint16_t event_size)`](sensor.html#void-fifo_full_handler-void-p_event_data-uint16_t-event_size) to read the FIFO outside interrupt context. See ruuvi_interface_scheduler.h for parameters used in this function.

#### `void fifo_full_handler (void * p_event_data, uint16_t event_size)` ####

This function reads the FIFO and stores the data inside the timeseries database. See ruuvi_interface_scheduler.h for parameters used in this function.

#### `void pack(const uint8_t resolution, const uint16_t sizeData, const uint8_t* const data, uint8_t* const packeddata)` ####

This function stores raw accelerometer values in 8/10/12 Bit format in compact form (without unused bits). It is a frontend to the functions pack8/10/12().

| Parameters |||
| - | - | - |
| resolution | in | Resolution of the samples. |
| sizeData | in | Size of input data. |
| data | in | Input data. |
| packeddata | in/out | Memory for storing compacted data. |

#### `rd_status_t lis2dh12_logged_data_get (rd_sensor_data_t * const data)` ####

This function retrieves raw accelerometer values from memory. The values are parsed and returned inside data. It is called by `app_sensor_get()` inside [app_sensor.c](sensor.html#app_sensor.c) if accelerometer logging is active.

| Parameters |||
| - | - | - |
| raw_data | in/out | Memory for storing accelerometer values. |

#### `rd_status_t app_acc_logging_send_eof_v2(const ri_comm_xfer_fp_t reply_fp, const rd_status_t status_code, const uint16_t crc)` ####

This function is called by [`app_acc_logging_send_logged_data()`](sensor.html#rd_status_t-app_acc_logging_send_logged_dataconst-ri_comm_xfer_fp_t-reply_fp-const-bool-is_v2) after all data is sent to the requestor. This function builds the [end of data message](ble-gatt-messages.html#end-of-data-message) and sends it.

| Parameters |||
| - | - | - |
| reply_fp | in | Function pointer to reply function. |
| status_code | in | Status code of the whole operation. This code is sent to the requestor. |
| crc | in | CRC value of the data. |

#### `rd_status_t app_acc_logging_send_logged_data(const ri_comm_xfer_fp_t reply_fp)` ####

This function is called when a request to send the logged acceleration data is received by GATT/UART. The function triggers FlashDB to read data. Data from the database is read via the callback function [`callback_send_data_block()`](sensor.html#bool-callback_send_data_blockfdb_tsl_t-tsl-void-arg). Inside the callback function the data is send to the requestor.

| Parameters |||
| - | - | - |
| reply_fp | in | Function pointer to reply function. |

| Special error codes ||
| - | - |
| RD_ERROR_INVALID_STATE | If logging is not active. |

#### `rd_status_t app_acc_logging_state(void)` ####

This function is used to query the state of accelerometer logging. It is called when a control message is received by GATT/UART to return this state to the caller. If streaming is active, this will not be reported as active logging by this function.

| Special error codes ||
| - | - |
| RD_SUCCESS | If logging is active. |
| RD_ERROR_INVALID_STATE | If logging is not active. |

#### `rd_status_t app_acc_logging_configuration_set (rt_sensor_ctx_t* sensor, rd_sensor_configuration_t* new_config)` ####

This function is called when a request to update the sensor configuration is received by GATT/UART. It checks every configuration parameter if it should be changed. It also checks if the value is different than actual value. If a change is detected it clears the ringbuffer, updates the configuration and stores the configuration in flash.

| Parameters |||
| - | - | - |
| sensor | in | Sensor context of the sensor which configuration should be changed. |
| new_config | in | Structure containing the new configuration values. |

#### `rd_status_t app_acc_logging_init(void)` ####

Initialize acceleration logging during boot. If logging was active before reboot it will be activated. If logging was not active before reboot this function return `RD_SUCCESS` without activating acceleration logging.

This function is called from [`setup()`](sensor.html#void-setup-void).

#### `rd_status_t app_acc_logging_uninit(void)` ####

The uninitialization of acceleration logging disables the logging if it is actually active. If logging is not active this function return RD_SUCCESS without doing anything.

#### `void app_acc_log_transfer_ram_db (void * p_event_data, uint16_t event_size)` ####

Execution of this function is scheduled if “streaming” is active and `rt_gatt_nus_is_connected()` returns true. It starts reading currently logged data from the FlashDB and transferring the data to the gateway.

Scheduling of this function is done inside [`on_fifo_full()`](sensor.html#void-on_fifo_full-const-ri_gpio_evt_t-evt) using `ri_scheduler_event_put()`.

#### `int64_t fdb_timestamp_get (void)` ####

Callback for use by FlashDB to retrieve the timestamp of the current new entry.

#### `bool callback_send_data_block(fdb_tsl_t tsl, void *arg)` ####

Callback function for use with FlashDB. When reading the database this function will be called for every entry.

This function calls `app_comms_blocking_send()` to send the data to the gateway.

| Parameters |||
| - | - | - |
| tsl | in | Pointer to current entry in the database. |
| arg | in/out | Pointer to context. See following table. The array consists of the following elements. |

| Context parameters by `*arg` |||
| - | - | - |
| `((void**)arg)[0]` | in | Pointer to database of type `fdb_tsdb*`. |
| `((void**)arg)[1]` | in | Pointer to transfer function `app_comms_blocking_send()`. |
| `((void**)arg)[2]` | in/out | Pointer to CRC value. |

If this functions returns `true` iterating over the following entries will by aborted.

#### `rd_status_t app_acc_logging_statistic (uint8_t* const statistic)` ####

This function is called from `handle_lis2dh12_comms()` after the gateway sends the message to retrieve flash statistics.

| Parameters |||
| - | - | - |
| statistic | in/out | Memory to store the statistic values. |

#### `uint8_t ruuvi_error_code_to_uint8(rd_status_t err_code)` ####

This function converts an Ruuvi error code to a one byte value. It returns the bit index of first error it finds. It cannot return a set of multiple errors as the input value supports.

| Parameters |||
| - | - | - |
| err_code | in | Ruuvi error code. |


### app_comms.c ####

#### `void handle_comms (const ri_comm_xfer_fp_t reply_fp, const uint8_t * const raw_message, size_t data_len)` ####

Added new switch/case which forwards messages regarding configuration and control of acceleration logging to the function [`handle_lis2dh12_comms()`](sensor.html#rd_status_t-handle_lis2dh12_comms-const-ri_comm_xfer_fp_t-reply_fp-const-uint8_t-const-raw_message-size_t-data_len), [`handle_lis2dh12_comms_v2()`](sensor.html#rd_status_t-handle_lis2dh12_comms_v2-const-ri_comm_xfer_fp_t-reply_fp-const-uint8_t-const-raw_message-size_t-data_len), [`handle_rtc_comms()`](sensor.html#rd_status_t-handle_rtc_comms-const-ri_comm_xfer_fp_t-reply_fp-const-uint8_t-const-raw_message-size_t-data_len).

#### `rd_status_t handle_lis2dh12_comms (const ri_comm_xfer_fp_t reply_fp, const uint8_t * const raw_message, size_t data_len)` ####

This function handles messages using the proprietary message format by GATT/UART communication needed to control the functionality of acceleration logging.

| Parameters |||
| - | - | - |
| reply_fp | in | Function pointer to reply function. |
| raw_message | in | Message received. |
| data_len | in | Length of the received message. |

| Special error codes ||
| - | - |
| RD_ERROR_NOT_FOUND | If LIS2DH12 is not found. |
| RD_ERROR_INVALID_PARAM | If unknown or invalid message was received. |

#### `rd_status_t handle_lis2dh12_comms_v2 (const ri_comm_xfer_fp_t reply_fp, const uint8_t * const raw_message, size_t data_len)` ####

This function handles messages using version 2 message format by GATT/UART communication needed to control the functionality of acceleration logging.

| Parameters |||
| - | - | - |
| reply_fp | in | Function pointer to reply function. |
| raw_message | in | Message received. |
| data_len | in | Length of the received message. |

| Special error codes ||
| - | - |
| RD_ERROR_NOT_FOUND | If LIS2DH12 is not found. |
| RD_ERROR_INVALID_PARAM | If unknown or invalid message was received. |

#### `rd_status_t handle_rtc_comms (const ri_comm_xfer_fp_t reply_fp, const uint8_t * const raw_message, size_t data_len)` ####

This function handles messages using version 2 message format by GATT/UART communication needed to control the RTC clock.

| Parameters |||
| - | - | - |
| reply_fp | in | Function pointer to reply function. |
| raw_message | in | Message received. |
| data_len | in | Length of the received message. |

| Special error codes ||
| - | - |
| RD_ERROR_INVALID_PARAM | If unknown or invalid message was received. |

#### `rd_status_t dis_init (ri_comm_dis_init_t * const p_dis, const bool secure)` ####

This function is called during initialization of the Bluetooth protocol stack. 

Our extension to this function is executed if `app_sensor_ctx_get()` from app_sensors.c is available. It sets the hardware revision string inside `ri_comm_dis_init_t` to the list of available and initialized sensors.

### ruuvi_nrf5_sdk15_communication_ble_gatt.c ###

#### `rd_status_t ri_gatt_dis_init (const ri_comm_dis_init_t * const p_dis)` ####

This function is called during initialization of the Bluetooth protocol stack. Our extension to this function adds a buildnumber to the former unused property `sw_rev_str` of `ble_dis_init_t`. The buildnumber is generated by a pre-build script `buildnum.js` which is executed by Segger Embedded Studio before compiling the software. The pre-buold script generated `buildnum.h` which includes the buildnumber.

### app_config.h ###

- Added macro APP_SENSOR_LOGGING to control compilation of app_accelerometer_logging.*
- If APP_SENSOR_LOGGING is not defined or is defined as 0 the functionality of logging of acceleration data is not available in the application.
- Changed the definition of APP_FLASH_PAGES to include the flash pages used for acceleration logging.
- This module also contains macros for memory separation between acceleration logging and environmental logging. The relevant macros are APP_FLASH_LOG_DATA_RECORDS_NUM and RT_FLASH_RINGBUFFER_MAXSIZE.

### app_sensor.c ###

#### `rt_sensor_ctx_t* app_sensor_find (const char *name)` ####

Find sensor by its name. Works only with initialized sensors, will not return a sensor which is supported in firmware but not initialized.

This function is called by [`app_enable_sensor_logging()`](sensor.html#rd_status_t-app_enable_sensor_loggingvoid) and [`app_disable_sensor_logging()`](sensor.html#rd_status_t-app_disable_sensor_loggingvoid) to retrieve the sensor context.

| Parameters |||
| - | - | - |
| name | in | Name of the sensor. |

### main.c ###

#### `void setup (void)`  ####

Added call to [`app_acc_logging_init()`](sensor.html#rd_status_t-app_acc_logging_initvoid) to initialize acceleration logging.

### ruuvi_interface_lis2dh12.c ###

#### `rd_status_t ri_lis2dh12_acceleration_raw_get (uint8_t * const raw_data)` ####

This function reads raw acceleration values from the registers of LIS2DH12. It is called from the [interrupt handler](sensor.html#void-fifo_full_handler-void-p_event_data-uint16_t-event_size) inside [app_accelerometer_logging.c](sensor.html#app_accelerometer_logging.c) and from [`ri_lis2dh12_data_get()`](sensor.html#rd_status_t-ri_lis2dh12_data_get-rd_sensor_data_t-const-data).

| Parameters |||
| - | - | - |
| raw_data | in/out | Memory for storing raw accelerometer values. |

#### `rd_status_t ri_lis2dh12_temperature_raw_get (uint8_t * const raw_temperature)` ####

This function reads raw temperature value from the registers of LIS2DH12. It is called  [`ri_lis2dh12_data_get()`](sensor.html#rd_status_t-ri_lis2dh12_data_get-rd_sensor_data_t-const-data) and [`lis2dh12_logged_data_get()`](sensor.html#rd_status_t-lis2dh12_logged_data_get-rd_sensor_data_t-const-data).

| Parameters |||
| - | - | - |
| raw_temperature | in/out | Memory for storing raw temperature values. |

#### `rd_status_t ri_lis2dh12_data_get (rd_sensor_data_t * const data)` ####

The original function `ri_lis2dh12_data_get()` is split into retrieving raw values from the sensor and parsing these data. Parsing is done by [`ri_lis2dh12_raw_data_parse()`](sensor.html#rd_status_t-ri_lis2dh12_raw_data_parse-rd_sensor_data_t-const-data-axis3bit16_t-raw_acceleration-uint8_t-raw_temperature).

This function is used if the acceleration logging is not active. If acceleration logging is active this function is replaced by [`lis2dh12_logged_data_get()`](sensor.html#rd_status_t-lis2dh12_logged_data_get-rd_sensor_data_t-const-data).

| Parameters |||
| - | - | - |
| data | in/out | Structure for storing parsed accelerometer values. |

#### `rd_status_t ri_lis2dh12_raw_data_parse (rd_sensor_data_t * const data, axis3bit16_t *raw_acceleration, uint8_t *raw_temperature)` ####

This function parses raw values from the sensor and stores the values inside data. It is called from [`ri_lis2dh12_data_get()`](sensor.html#rd_status_t-ri_lis2dh12_data_get-rd_sensor_data_t-const-data) and from [`lis2dh12_logged_data_get()`](sensor.html#rd_status_t-lis2dh12_logged_data_get-rd_sensor_data_t-const-data).

| Parameters |||
| - | - | - |
| data | in/out | Structure for storing parsed accelerometer values. |
| raw_acceleration | in | Raw acceleration values. |
| raw_temperature | in | Raw temperature value. This parameter can be NULL. |

### ruuvi_nrf5_sdk_rtc_mcu.c ###

#### `rd_status_t ri_set_rtc_millis(uint64_t millis)` ####

Set system time by external source. Set RTC to zero.

| Parameters |||
| - | - | - |
| millis | in | External time. |

### ruuvi_nrf5_sdk15_power.c / ruuvi_nrf5_sdk15_power.h ###

#### `rd_status_t ri_power_read_boot_count (uint32_t *boot_count)` ####

This function return the boot counter.

| Parameters |||
| - | - | - |
| boot_count | out | Memory for storing the boot counter. |

### ruuvi_task_flash_ringbuffer.c ###

The ringbuffer module acts as a frontend to FlashDB. The ringbuffer functionality is provided by the timeseries database of FlashDB.

#### `rd_status_t rt_flash_ringbuffer_create(const char *partition, fdb_get_time get_time, const bool format_db)` ####

This function initializes an instance of timeseries database. 

| Parameters |||
| - | - | - |
| partition | in | Name of the partition of the FAL device where the database will be stored. |
| get_time | in | Function pointer to callback function. This function is used by timeseries database to retrieve the current timestamp. |
| format_db | in | Wether to force to create a empty database. |

#### `rd_status_t rt_flash_ringbuffer_write(const uint16_t size, const void* data)` ####

 This function writes data to FlashDB.

| Parameters |||
| - | - | - |
| size | in | Size of data |
| data | in | Data to be written  |

#### `rd_status_t rt_flash_ringbuffer_read(const fdb_tsl_cb callback, const ri_comm_xfer_fp_t reply_fp, uint16_t* crc)` ####

This function starts reading the timeseries database. Reading data from timeseries database is done by iterating all entries. For every entry a callback function is called.

| Parameters |||
| - | - | - |
| callback | in | Callback function which would be called for every entry. |
| reply_fp | in | Callback function which sends the data to the requestor. |
| crc | in/out | CRC16 value which gets calculated over all data send to the requestor. |

#### `rd_status_t rt_flash_ringbuffer_clear(void)` ####

This function clears the contents of the timeseries database. 

#### `rd_status_t rt_flash_ringbuffer_drop (void)` ####

This function de-initializes the timeseries database.

#### `rd_status_t rt_flash_ringbuffer_statistic (uint8_t* const statistic)` ####

This function reads some statistics about the usage of the internal Nordic Flash memory and returns them.

| Parameters |||
| - | - | - |
| statistic | in/out | Memory for storing statistics. |


### ruuvi_task_flashdb.c ###

This module contains supporting functions needed to integrate FlashDB into Ruuvi Firmware.

#### `rd_status_t rt_macronix_flash_exists(void)` ####

This function checks if Macronix Flash Chip is available.

| Special error codes ||
| - | - |
| RD_SUCCESS | If Macronix Flash is available. |
| RD_ERROR_NOT_FOUND | If Macronix Flash is not available. |
| RD_ERROR_NOT_INITIALIZED | If the module is currently not initialzed. |

#### `rd_status_t rt_flashdb_to_ruuvi_error(fdb_err_t fdb_err)` ####

This function converts an error code of FlashDB to an Ruuvi error code. It return the Ruuvi error code which represents the state of FlashDB.

| Parameters |||
| - | - | - |
| fdb_err | in | Error code of FlashDB. |

#### `rd_status_t rt_reset_macronix_flash(void)` ####

This functions sends the Chip Erase command to the macronix flash chip if the chip is available. This function is called during factory reset.

#### `rt_macronix_high_performance_switch(const bool enable)` ####

This function configures the high performance switch of the Macronix Flash Chip. High performance mode is used during formating the flash in order to prepare it for the database or during factory reset. 

| Parameters |||
| - | - | - |
| enable | in | Desired mode of operation. |

#### `void fdb_log (const char * const msg, ...)` ####

This function acts as a proxy between the logging mechanism of FlashDB and the log writing system of Ruvvi. It converts the parameters and passes log messages to Ruuvi's logging module.

### app_button.c ###

#### `void factory_reset (void * p_event_data, uint16_t event_size)` ####

Add call to [`rt_reset_macronix_flash()`](sensor.html#rd_status_t-rt_reset_macronix_flashvoid) to delete content of Macronix Flash in case of factory reset.


## Energy consumption ##
The following figure visualizes energy consumption of different operation states. The numbers at the measuring point are equal to the duration. All measurements are done with 3V supply voltage.

 ```{r echo=FALSE}
 energymeasurement <- openxlsx::read.xlsx("Energiemessung.xlsx", sheet="Tabelle1")

 energymeasurement <- tibble::as_tibble(energymeasurement)

 energymeasurement <- energymeasurement %>% dplyr::rename(action=Aktion,
 flash=Flash,
 resolution_bit="Resolution./.Bit",
 samplingrate_hz="Samplingrate./.Hz",
 duration_s="Dauer./.s",
 voltage_v="Spannung./.V",
 current_uA="Average.Current./.µA",
 energy_mJ="Energie./.mJ")

 energymeasurement %>% ggplot2::ggplot() +
 ggplot2::aes(x=samplingrate_hz, y=energy_mJ, color=flash) +
 ggplot2::geom_path() +
 ggplot2::geom_point(ggplot2::aes(shape=action), size=3) +
 ggplot2::geom_text(ggplot2::aes(label=duration_s), nudge_y=70, color="black") +
 ggplot2::theme_bw() +
 ggplot2::scale_y_continuous(name="energy / mJ", sec.axis=ggplot2::sec_axis(trans=~./3, name="charge / mC")) +
 ggplot2::xlab("samplingrate / Hz")
 ```

## Firmware packaging ##

To create a File which is suitable for [DFU](https://ruuvi.com/software-update/) you need [nrfutil](https://www.nordicsemi.com/Products/Development-tools/nRF-Util) from Nordic Semiconductor. The DFU Package must be signed. The [private key](https://github.com/ruuvi/ruuvi.nrf5_sdk15_bootloader.c/blob/master/ruuvi_open_private.pem) can be obtained from Ruuvi's Github repository.

The following script to create a DFU package assumes this directory structure.
```
dfu-package
 \
  | ruuvi_open_private.pem
ruuvi.firmware.c
 \
  | nRF5_SDK_15.3.0_59ac345
  | src
  | \
  |  | output
  |  | \
  |  |  | debug
  |  |  | \
  |  |  |  | exe
```

To create a DFU package execute the following commands inside directory dfu-package.
```
nrfutil settings generate --family NRF52 --application ..\ruuvi.firmware.c\src\Output\Debug\Exe\ruuvitag_b.hex --application-version 1  --bootloader-version 1 --bl-settings-version 1 output\settings.hex
mergehex -m ..\ruuvi.firmware.c\nRF5_SDK_15.3.0_59ac345\components\softdevice\s132\hex\s132_nrf52_6.1.1_softdevice.hex ruuvitag_b_s132_6.1.1_bootloader_3.1.0.hex output\settings.hex -o output\sbc.hex
mergehex -m output\sbc.hex ..\ruuvi.firmware.c\src\Output\Debug\Exe\ruuvitag_b.hex -o output\packet.hex
nrfutil pkg generate --application ..\ruuvi.firmware.c\src\Output\Debug\Exe\ruuvitag_b.hex --application-version 1 --hw-version 0xB0 --sd-req 0xB7 --key-file ruuvi_open_private.pem dfu_app.zip
```