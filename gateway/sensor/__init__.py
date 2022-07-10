"""
An object of type sensor is an digital twin of a hardware sensor.
For this module to work properly, all dependencies must be installed 
and the `communication_interface. yml` must be recorded during the installation process.
Hint: The logging level can be changed with sensor.logger.setLevel(logging.warning)
"""
import binascii
import struct # built-in
import logging # built-in
import os.path # built-in
from functools import partial # built-in
from binascii import hexlify # built-in
import yaml # third-party
import asyncio # third-pary
from bleak import BleakClient # third-party
import time # built-in
import crcmod
from gateway.event.event import Event_ts
from gateway.sensor.SensorConfig import SensorConfig # third-party
from gateway.sensor.decode_utils import process_data_8, process_data_10, process_data_12, unpack8, unpack10, unpack12
from gateway.sensor.errorcode_utils import ri_error_to_string

from gateway.sensor.sensor_config_enum import SamplingRate, SamplingResolution, \
     MeasuringRange # internal
from gateway.sensor.message_objects import ReturnValuesFromSensor # internal

with open(os.path.dirname(__file__) + '/../communication_interface.yml') as ymlfile:
    # load interface specifications
    sensor_interface = yaml.safe_load(ymlfile)
    ymlfile.close()

UART_RX = sensor_interface["communication_channels"]["UART_RX"]
UART_TX = sensor_interface["communication_channels"]["UART_TX"]

LOG_LEVEL = logging.INFO

# Redundancy check
crcfun = crcmod.mkCrcFun(0x11021, rev=False, 
                                        initCrc=0xffff, xorOut=0)

# Creat a named logger 'sensor' and set it on INFO level
logger = logging.getLogger('Sensor')
logger.setLevel(LOG_LEVEL)

class sensor(object):
    """An object of this class creates a digital twin of a sensor. Every 
    sensor has its own mac and name.

    :param sensor: This object represents a hardware ble device.
    :type sensor: sensor.sensor
    """
    def __init__(self, name : str, mac : str):
        """Initialization of a sensor object.

        :param name: Name of the BLE device.
        :type name: str
        :param mac: MAC address of the BLE device.
        :type mac: str
        """
        self.mac = mac
        self.name = name
        self.main_loop = asyncio.get_event_loop()
        self.stopEvent = Event_ts()
        self.notification_done = False  # improvement wanted

        # Trennung, weil Daten unterschiedlich geparsed werden
        self.sensor_data = list()  # command callbacks - for minor functions like getTime
        # Acceloremeter-Daten werden in Ringspeicher geschrieben (Wenn acceloremeter logging aktiviert wurde) und werden nur auf Abfrage geholt
        # Problem: Wir wissen nicht wann speicher voll wird. 
        # Problem: Speicher wird voll abh. von Samplingrate und Samplingresolution
        self.data = list()  # accelerometer - for streaming
        
        # Hilfvariable, wo raw-Data  des Sensors reingeschrieben werden
        self.sensordata = bytearray()
        self.config = SensorConfig()
        return

    def clear(self):
        """Function to manually recreate the sensor_data
        and data variable.
        """
        self.sensor_data = list()
        self.data = list()
        logger.info('sensor variables have been cleared!')
        return

    async def wait_response_or_timeout(self, timeout_sec):
        """Timeout function to prevent endless loops
        """        
        logger.info("Wait for response or check if timeout of %s seconds is exceeded", timeout_sec)
        while time.time() - self.start_time < timeout_sec:
            logger.debug("Timeout timer running {}".format(
                time.strftime("%H:%M:%S", time.localtime(self.start_time)))
                )
            await asyncio.sleep(1)
            if self.notification_done:
                break
        try:
            self.stopEvent.set()
        except:
            pass
    
    def work_loop(self, command, write_channel):
        """Initialize and start workloops for specific tasks.

        :param command: Command from sensor_interface
        :type command: str
        :param write_channel: Channel from sensor_interface.
        :type write_channel: str
        :param accelerom: Indicate which callback function has to be used. Defaults to False
        :type accelerom: bool, optional
        """
        self.taskobj = self.main_loop.create_task(self.connect_ble_sensor(command, write_channel))
        try:
            self.main_loop.run_until_complete(self.taskobj)
        except Exception as e:
            logger.error("Error during task execution. Reason: {}".format(e))
        return
    
    async def connect_ble_sensor(self, command_string, write_channel):
        """Starts GATT connection. Listen to callbacks and send commands.

        :param command_string: Command from sensor_interface.
        :type command_string: str
        :param write_channel: Channel from sensor_interdace.
        :type write_channel: str
        """
        logger.info("Send {} to MAC {} ".format(command_string, self.mac))
        self.notification_done = False
        try:
            async with BleakClient(self.mac) as client:
                logger.info('Start notify: %s' % (self.mac))
                if command_string == sensor_interface["commands"]["get_acceleration_data"]:
                    await client.start_notify(
                        sensor_interface["communication_channels"]["UART_RX"], self.handle_data
                        )
                    await client.write_gatt_char(
                        write_channel, bytearray.fromhex(command_string), True
                        )                    
                else:
                    # Send the command (Wait for Response must be True)
                    await client.start_notify(
                        sensor_interface["communication_channels"]["UART_RX"], 
                        partial(self.handle_ble_callback, client) # partial kann evtl. weg? 
                        )
                    await client.write_gatt_char(
                        write_channel, bytearray.fromhex(command_string), True
                        )

                # Codeblock sorgt dafür, dass auf Nachricht gewartet wird 
                # Wenn keine Nachricht kommt, dann Timeout
                self.start_time = time.time()
                await self.wait_response_or_timeout(10)
                # Wartet so lange bis Event-Loop thread-safe beendet wurde 
                # vorher wird in timeout_for_commands stopEvent.set() gerufen
                await self.stopEvent.wait()
                logger.info('Stop notify: %s' % (self.mac))
                logger.info("Abort workloop task...")
                await client.stop_notify(
                    sensor_interface["communication_channels"]["UART_RX"]
                    )
                self.stopEvent.clear()
        except Exception as e:
            logger.error('Connection failed at MAC %s with error %e' % (self.mac, e))
        return
    
    def handle_ble_callback(self, client: BleakClient, sender: int, value: bytearray):
        """Parse incomming messages and save it into sensor_data

        :param client: Object with connection specifications to a specific.
        :type client: BleakClient
        :param sender: internal use
        :type sender: int
        :param value: callbacks
        :type value: bytearray
        """

        # Response messages des Sensors
        if value[0] == 0x22 and value[2] == 0xF2:
            status_string = str(ri_error_to_string(value[3]), )
            logger.info("Status: %s" % status_string)
            self.notification_done=True

        if value[0] == 0x22 and value[2] == 0xF3:
            logger.info("Received heartbeat: {}".format(
                int.from_bytes(value[4:6], byteorder='big', signed=False))
                )
            status_string = str(ri_error_to_string(value[3]), )
            logger.info("Status: %s" % status_string)
            self.notification_done = True

        if value[0] == 0x4A or value[0] == 0x21:
            message_return_value = ReturnValuesFromSensor()
            logger.info("Received: %s" % hexlify(value))
            status_string = str(ri_error_to_string(value[3]), )
            logger.info("Status: %s" % status_string)
            if len(value) == 4:
                test = message_return_value.form_get_status(status=int(value[3]), mac=client.address)
                self.sensor_data.append([test.returnValue.__dict__])
                self.notification_done = True

            elif value[2] == 0x09:

                logger.info("Received time: %s" % hexlify(value[:-9:-1]))
                received_time=time.strftime('%D %H:%M:%S', time.gmtime(int(hexlify(value[:-9:-1]), 16) / 1000))
                logger.info(received_time)
                self.sensor_data.append(message_return_value.from_get_time(status=status_string, received_time=received_time,
                                                   mac=client.address).returnValue.__dict__)
                self.notification_done = True

            elif value[0] == 0x4a and value[3] == 0x00:
                sample_rate = ""
                if value[4] == 201:
                    logger.info("Samplerate: 400 Hz")
                    sample_rate = 400
                else:
                    logger.info("Samplerate:    %d Hz" % value[4])
                    sample_rate=int(value[4])
                received_config=message_return_value.from_get_config(status=status_string,sample_rate=sample_rate,resolution= int(value[5]),
                                                    scale=int(value[6]),dsp_function=int(value[7]), dsp_parameter=int(value[8]),
                                                    mode="%x"% value[9],divider=int(value[10]), mac=client.address)
                self.sensor_data.append(received_config.return_value.__dict__)
                print(received_config.return_value.__dict__)
                self.config = SensorConfig()
                self.config = self.config.from_dict(received_config.return_value.__dict__)
                self.notification_done=True

        elif value[0] == 0xfb and value[1] == 0x0d:
            message_return_value = ReturnValuesFromSensor()
            logger.info("Received: %s" % hexlify(value))
            logging_status = value[3]
            ringbuffer_start = value[4]
            ringbuffer_end = value[5]
            ringbuffer_size = value[6]
            valid_records = value[7] | (value[8] << 8)
            dirty_records = value[9] | (value[10] << 8)
            words_reserved = value[11] | (value[12] << 8)
            words_used = value[13] | (value[14] << 8)
            largest_contig = value[15] | (value[16] << 8)
            freeable_words = value[17] | (value[18] << 8)
            received_flash_statistic=message_return_value.from_get_flash_statistics(
            logging_status=logging_status, ringbuffer_start=ringbuffer_start,
            ringbuffer_end=ringbuffer_end, ringbuffer_size=ringbuffer_size, valid_records=valid_records, dirty_records=dirty_records,
            words_reserved=words_reserved, words_used= words_used, largest_contig=largest_contig, freeable_words=freeable_words,
            mac=client.address)
            self.sensor_data.append([received_flash_statistic.returnValue.__dict__])
            logger.info("Last Status %s" % (str(ri_error_to_string(logging_status)),))
            logger.info("Ringbuffer start %d" % (ringbuffer_start,))
            logger.info("Ringbuffer end %d" % (ringbuffer_end,))
            logger.info("Ringbuffer size %d" % (ringbuffer_size,))
            logger.info("Valid records %d" % (valid_records,))
            logger.info("Dirty records %d" % (dirty_records,))
            logger.info("Words reserved %d" % (words_reserved,))
            logger.info("Words used %d" % (words_used,))
            logger.info("Largest continuos %d" % (largest_contig,))
            logger.info("Freeable words %d\n" % (freeable_words,))
            self.notification_done = True
    
    def activate_accelerometer_logging(self):
        """Activate accelerometer logging at sensor.
        """        
        logger.info('Try activate accelerometer logging at {}'.format(self.mac))
        self.work_loop(sensor_interface["commands"]["activate_logging_at_sensor"], sensor_interface["communication_channels"]["UART_TX"])
        return

    def deactivate_accelerometer_logging(self):
        """Deactivate accelerometer logging at sensor.
        """        
        logger.info('Try deactivate accelerometer logging at {}'.format(self.mac))
        self.work_loop(sensor_interface["commands"]["deactivate_logging_at_sensor"], sensor_interface["communication_channels"]["UART_TX"])
        return 
    
    def get_acceleration_data(self):
        """Get accelerometer data from sensor.
        """         
        logger.info('Try to get acceleration data from {}'.format(self.mac))
        self.work_loop(sensor_interface["commands"]["get_acceleration_data"] , sensor_interface["communication_channels"]["UART_TX"])  
        self.sensordata = bytearray()      
        return
    
    async def handle_data(self, handle, value):
        """Special callback function to handle incomming accelerometer data.

        :param handle: Artefact of SensorGatewayBleak library. Not in use
        :type handle: deprecated, not in use anymore
        :param value: Callbacks as bytearray.
        :type value: bytearray
        :return: x,y,z,timestamp
        :rtype: int, int, int, timestamp
        """

        # Handling of accelerometer data
        if value[0] == 0x11:
            # Daten
            self.sensordata.extend(value[1:])
            # Time wird gesetzt um die Abfrage des Ringbuffers auf 10 Sekunden zu setzen -> Querabhängigkeit zu _timeout Funktion
            self.start_time = time.time()
            logger.info("Received data block: %s" % hexlify(value[1:]))
            # Marks end of data stream
        elif value[0] == 0x4a and value[3] == 0x00:
            self.notification_done = True
            message_return_value = ReturnValuesFromSensor()
            self.start_time = time.time()
            self.end_time = time.time()
            self.delta = len(self.sensordata) / (self.end_time - self.start_time)

            logger.info('Bandwidth : {} Bytes/Second'.format(self.delta))
            # Status
            logger.debug("Status: %s" % str(ri_error_to_string(value[3])))

            crc = value[12:14]
            logger.debug("Received CRC: %s" % hexlify(crc))

            # CRC validation
            ourcrc = crcfun(self.sensordata)

            if hexlify(crc) == bytearray():
                logger.info("No crc received")
                return None

            if int(hexlify(crc), 16) != ourcrc:
                logger.warning("CRC are unequal")
                return None

            # Start data
            # Timestamp hier wird genutzt um zu den acceleration daten die Zeit zu haben 
            # Timestamp wird vom Sensor nicht jede Nachricht mitgeschickt. 
            # Time für acceleration data ergibt sich aus letztem timestamp + sampling frequenz * anzahl samples seit letztem timestamp
            # Hier gibt noch Fehler, die beim Sensor liegen könnten -> Abweichungen zwischen Interpolierten Zeitstempel und geschickten nächsten TimeStamp
            if (value[5] == 12):
                # 12 Bit
                logger.info("Start processing reveived data with process_sensor_data_12")
                AccelorationData = process_data_12(self.sensordata, value[6], value[4])
            elif (value[5] == 10):
                # 10 Bit
                logger.info("Start processing reveived data with process_sensor_data_10")
                AccelorationData = process_data_10(self.sensordata, value[6], value[4])
            elif (value[5] == 8):
                # 8 Bit
                logger.info("Start processing reveived data with process_sensor_data_10")
                AccelorationData = process_data_8(self.sensordata, value[6], value[4])
            else:
                logger.error('Cant process bytearray! Unknwon sensor resolution!')
            if AccelorationData != None:
                logger.info("Run in Funktion AccelorationData != None")
                dataList=message_return_value.from_get_accelorationdata(accelorationdata=AccelorationData,mac=self.mac)
                self.data.append(dataList.return_value.__dict__)
        return
         
    def set_config(self, sampling_rate='FF', sampling_resolution='FF', measuring_range='FF', divider="FF"):
        """Set config function for BLE devices.

        :param sampling_rate: Frequency of the measurements, defaults to 'FF'
        :type sampling_rate: str, optional
        :param sampling_resolution: Resolution of the acceleration measurement, defaults to 'FF'
        :type sampling_resolution: str, optional
        :param measuring_range: Scale of the measurements, defaults to 'FF'
        :type measuring_range: str, optional
        :param divider: Can be set to customize the frequency, defaults to "FF"
        :type divider: str, optional
        """
        logger.info("Setting new config for sensor {}".format(self.mac))
        if sampling_rate == 'FF':
            hex_sampling_rate = 'FF'
        elif sampling_rate in SamplingRate._value2member_map_:
            hex_sampling_rate = SamplingRate(sampling_rate).name[1:]
            logger.debug("decimal sampling rate is: {}".format(sampling_rate))
            logger.debug("hex sampling rate is: {}".format(hex_sampling_rate))
        else:
            logger.warning("Wrong sampling rate! Sampling rate set to 'FF'!")
            hex_sampling_rate = 'FF'
        # Check if arguments are given and valid
        if sampling_resolution == 'FF':
            hex_sampling_resolution = 'FF'
        elif sampling_resolution in SamplingResolution._value2member_map_:
            hex_sampling_resolution = SamplingResolution(sampling_resolution).name[1:]
            logger.debug("decimal sampling resolution is: {}".format(sampling_resolution))
            logger.debug("hex sampling resolution is: {}".format(hex_sampling_resolution))
        else:
            logger.warning("Wrong sampling resolution! Sampling resolution set to 'FF'!")
            hex_sampling_resolution = 'FF'
        # Check if arguments are given and valid
        if measuring_range == 'FF':
            hex_measuring_range = 'FF'
        elif measuring_range in MeasuringRange._value2member_map_:
            hex_measuring_range = MeasuringRange(measuring_range).name[1:]
            logger.debug("decimal measuring range is: {}".format(measuring_range))
            logger.debug("hex measuring range is: {}".format(hex_measuring_range))
        else:
            logger.warning("Wrong measuring range! Measuring range set to 'FF'!")
            hex_measuring_range = 'FF'
        if divider == 'FF':
            hex_divider = 'FF'
            logger.debug("divider is: {}".format(hex_divider))
        elif int(divider) > 254:
           logger.error("Divider value too high! (max. 254)") 
           hex_divider = 'FF'
        else:
            div=""
            try:
               div= int(divider)
               logger.debug("decimal divider is: {}".format(div))
            except Exception as ex :
                logger.error(str(ex))
                logger.error("Divider must be an int value")
            if isinstance(div,int):
                hex_divider =hex(div)[2:]
                if len(hex_divider) < 2:
                    hex_divider = '0' + hex_divider
                logger.debug("hex divider is: {}".format(hex_divider))
            else:
                hex_divider='FF'
        logger.info("Set sensor configuration {}".format(self.mac))
        command_string = sensor_interface['commands']['substring_set_config_sensor'] + hex_sampling_rate + hex_sampling_resolution + hex_measuring_range + "FFFFFF" + hex_divider + "00"
        self.work_loop(command_string,sensor_interface["communication_channels"]["UART_TX"])
        return
    
    def set_time(self):
        """Set sensor time.
        """        
        now = struct.pack("<Q", int(time.time() * 1000)).hex()
        command=sensor_interface['commands']['substring_set_sensor_time'] + now
        logger.info("Set sensor time {}".format(self.mac))
        self.work_loop(command,sensor_interface["communication_channels"]["UART_TX"])
        return

    def set_heartbeat(self, heartbeat : int):
        """Change the frequency in which advertisements will be sent.
        The unit of the heartbeet is millisecond [ms]. Just values between 100 ms and
        65.000 ms are permitted.

        :param heartbeat: Frequency of the advertisements in milliseconds.
        :type heartbeat: int
        """
        logger.info("Set heartbeat to: {}".format(heartbeat))
        hex_beat = hex(heartbeat)[2:]
        hex_msg = f"2200F2{'0000'[:4 - len(hex_beat)]}{hex_beat}000000000000"
        self.work_loop(hex_msg, sensor_interface["communication_channels"]["UART_TX"])

    def get_flash_statistic(self):
        """Get flash statistic from sensor.
        """        
        logger.info("Reading flash statistic from {}".format(self.mac))
        self.work_loop(sensor_interface["commands"]["get_flash_statistic"],sensor_interface["communication_channels"]["UART_TX"])
        return
    
    def get_logging_status(self):
        """Get the status of the accelerometer logging.
        """        
        logger.info("Reading acceleration statistic from {}".format(self.mac))
        self.work_loop(sensor_interface["commands"]["get_logging_status"],sensor_interface["communication_channels"]["UART_TX"])
        return
    
    def get_config(self):
        """Get sensor configurations.
        """        
        logger.info("Reading config from {}".format(self.mac))
        self.work_loop(sensor_interface["commands"]["get_config_from_sensor"],sensor_interface["communication_channels"]["UART_TX"])
        return    
    
    def get_time(self):
        """Get time from sensor
        """        
        logger.info("Reading time from {}".format(self.mac))
        self.work_loop(sensor_interface["commands"]["get_time_from_sensor"],sensor_interface["communication_channels"]["UART_TX"])
        return

    def get_heartbeat(self):
        """Get the actuall frequency in which the sensor sends advertisements.
        """        
        logger.info("Get heartbeat...")
        self.work_loop(sensor_interface["commands"]["get_heartbeat"], sensor_interface["communication_channels"]["UART_TX"])
        return
    
#    Callback für streaming funktionalität
    def callback(self, sender: int, value: bytearray):
        """this callback is triggered on all data received in GATT-mode. It triggers the correct unpack-method to convert the raw received data into readable hex-strings and extracts the values from those strings. If the sensor reports an error, the callback is going to stop the process using the stopevent of self.
        param sender: address of the sender
        type sender: int
        param value: the bytearray that was received from the sender and needs to be forwarded to the correct unpack-method
        type value: bytearray
        """
        # self.process_data_12(sensordaten, value[6], value[4])
        logger.debug("Received: %s" % binascii.hexlify(value, "-"))
        if value[0] == 0x4A:
            logger.debug("Sender: %s" % sender)
            logger.debug("Status: %s" % (str(ri_error_to_string(value[3]),)))
            self.stopevent.set()
        elif value[0] == 0x11:
            # self.sensor_data
            if self.config.resolution == 8:
                unpack8(value[1:], self.config.sample_rate, self.config.scale, filepointer.csvfile)
            elif self.config.resolution == 10:
                unpack10(value[1:], self.config.sample_rate, self.config.scale, filepointer.csvfile)
            elif self.config.resolution == 12:
                unpack12(value[1:], self.config.sample_rate, self.config.scale, filepointer.csvfile)
                
    async def setup_for_streaming(self):
        """Change mode to gatt streaming.
        """
        async with BleakClient(self.config.mac) as client:
            await client.start_notify(UART_RX, self.callback)
            await client.write_gatt_char(UART_TX, bytearray.fromhex("4a4a03%02x%02x%02xFFFFFF0000" % (self.config.sample_rate, self.config.resolution, self.config.scale)))
            await asyncio.sleep(10)
            await self.stopevent.wait()
            await client.stop_notify(UART_RX)
            self.stopevent.clear()

    async def activate_streaming(self):
        """Start streaming and receive data.
        """
        async with BleakClient(self.config.mac) as client:
            await client.start_notify(UART_RX, self.callback)
            await client.write_gatt_char(UART_TX, bytearray.fromhex(sensor_interface["commands"]["activate_streaming"]))
            await self.stopevent.wait()
            await client.stop_notify(UART_RX)

    async def listen_for_data(self, samplingtime=10*60, filename = str(int(time.time()))+".csv"):
        """Listens for incoming data and writes them to a specified csv file.

        :param samplingtime: hearbeat time
        :type samplingtime: int
        :param filename: name of csv
        :type filename: string
        """
        filepointer.csvfile = open(filename, "w")
        async with BleakClient(self.config.mac) as client:
            await client.start_notify(UART_RX, self.callback)
            await asyncio.sleep(samplingtime)
            await client.stop_notify(UART_RX)
        filepointer.csvfile.close()
        filepointer.csvfile = None

# Pointer to file which receives data
class filepointer:
    csvfile = None
