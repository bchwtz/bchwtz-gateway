"""
An object of type sensor is an digital twin of a hardware sensor.
For this module to work properly, all dependencies must be installed 
and the `communication_interface. yml` must be recorded during the installation process.
Hint: The logging level can be changed with sensor.Log_sensor.setLevel(logging.warning)
"""
import binascii
import struct # built-in
import logging # built-in
import os.path # built-in
from functools import partial # built-in
from binascii import hexlify # built-in
import datetime # built-in
import yaml # third-party
import asyncio # third-pary
from bleak import BleakClient # third-party
import time # built-in
import crcmod # third-party

from gateway.sensor.SensorConfigEnum import SamplingRate, SamplingResolution, \
     MeasuringRange # internal
from gateway.sensor.MessageObjects import return_values_from_sensor # internal

with open(os.path.dirname(__file__) + '/../communication_interface.yml') as ymlfile:
    # load interface specifications
    sensor_interface = yaml.safe_load(ymlfile)
    ymlfile.close()


# Creat a named logger 'sensor' and set it on INFO level
Log_sensor = logging.getLogger('sensor')
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
Log_sensor.addHandler(console_handler)

class Event_ts(asyncio.Event):
    """Custom event loop class for the sensor().

    :param asyncio: None
    :type asyncio: Event_ts inherit asyncio.Event functions.
    """

    def clear(self):     
        self._loop.call_soon_threadsafe(super().clear)

    def set(self):    
        self._loop.call_soon_threadsafe(super().set)

class SensorConfig():
    def __init__(self, sample_rate=None, resolution=None, scale=None, dsp_function=None, dsp_parameter=None, mode=None, divider=None, mac=None):
        """Storage dto for the sensor's config. It is used to store all important parameters.

        :param sample_rate: [description], defaults to None
        :type sample_rate: [type], optional
        :param resolution: [description], defaults to None
        :type resolution: [type], optional
        :param scale: [description], defaults to None
        :type scale: [type], optional
        :param dsp_function: [description], defaults to None
        :type dsp_function: [type], optional
        :param dsp_parameter: [description], defaults to None
        :type dsp_parameter: [type], optional
        :param mode: [description], defaults to None
        :type mode: [type], optional
        :param divider: [description], defaults to None
        :type divider: [type], optional
        :param mac: [description], defaults to None
        :type mac: [type], optional
        """
        self.sample_rate = sample_rate
        self.resolution = resolution
        self.scale = scale
        self.dsp_funtion = dsp_function
        self.dsp_parameter = dsp_parameter
        self.mode = mode
        self.divider = divider
        self.mac = mac

    def from_dict(dct):
        """ Converts a dictionary with the correct key-value-set to a sensor config object.

        :param dct: [description]
        :type dct: [type]
        :return: [description]
        :rtype: [type]
        """
        self = SensorConfig()
        for key in dct:
            setattr(self, key, dct[key])
        print("set new config")
        return self
    def __repr__(self) -> str:
        return str(self.__dict__)

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
        self.sensor_data = list()  # command callbacks
        self.data = list()  # accelerometer
        self.crcfun = crcmod.mkCrcFun(0x11021, rev=False, 
                                        initCrc=0xffff, xorOut=0)
        self.sensordaten = bytearray()
        self.stopevent = Event_ts()
        self.config = SensorConfig()
        return

    def clear(self):
        """Function to manually recreate the sensor_data
        and data variable.
        """
        self.sensor_data = list()
        self.data = list()
        Log_sensor.info('sensor variables have been cleared!')
        return

    async def timeout_for_commands(self):
        """Timeout function to prevent endless loops
        """        
        Log_sensor.info("Start timeout function")
        while time.time() - self.start_time < 10:
            Log_sensor.info("Timeout timer running {}".format(
                time.strftime("%H:%M:%S", time.localtime(self.start_time)))
                )
            await asyncio.sleep(1)
            if self.notification_done:
                #self.notification_done = False
                break
        try:
            self.stopEvent.set()
        except:
            pass
    
    def work_loop(self, command, write_channel, accelerom=False):
        """Initialize and start workloops for specific tasks.

        :param command: Command from sensor_interface
        :type command: str
        :param write_channel: Channel from sensor_interface.
        :type write_channel: str
        :param accelerom: Indicate which callback function has to be used. Defaults to False
        :type accelerom: bool, optional
        """
        self.taskobj = self.main_loop.create_task(self.connect_ble_sensor(command, write_channel, accelerom))
        try:
            self.main_loop.run_until_complete(self.taskobj)
        except Exception as e:
            Log_sensor.error("Exception occured: {}".format(e))
        return
    
    async def connect_ble_sensor(self, command_string, write_channel, accelerom):
        """Starts GATT connection. Listen to callbacks and send commands.

        :param command_string: Command from sensor_interface.
        :type command_string: str
        :param write_channel: Channel from sensor_interdace.
        :type write_channel: str
        :param accelerom: Indicates which callback function has to be used.
        :type accelerom: bool
        """
        Log_sensor.info("Send {} to MAC {} ".format(self.mac, command_string))
        try:
            async with BleakClient(self.mac) as client:
                if accelerom:
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
                        partial(self.handle_ble_callback, client)
                        )
                    await client.write_gatt_char(
                        write_channel, bytearray.fromhex(command_string), True
                        )
                Log_sensor.info('Message send to MAC: %s' % (self.mac))

                self.start_time = time.time()
                Log_sensor.info("Set Processtimer")
                await self.timeout_for_commands()
                Log_sensor.info("timeout starts monitoring")
                await self.stopEvent.wait()
                Log_sensor.warning("Abort workloop task via timeout()!")
                await client.stop_notify(
                    sensor_interface["communication_channels"]["UART_RX"]
                    )
                self.stopEvent.clear()
                Log_sensor.info('Stop notify: %s' % (self.mac))
                Log_sensor.info("Task done connect_to_mac_command!")
        except Exception as e:
            Log_sensor.warning('Connection failed at MAC %s' % (self.mac))
            Log_sensor.error("Error: {}".format(e))
        return
    
    def handle_ble_callback(self, client: BleakClient, sender: int, value: bytearray):
        """Parse incomming messages and save it into sensor_data

        :param client: Object with connection specifications to a specific.
        :type client: BleakClient
        :param sender: [description]
        :type sender: int
        :param value: callbacks
        :type value: bytearray
        """

        if value[0] == 0x22 and value[2] == 0xF2:
            status_string = str(self.ri_error_to_string(value[3]), )
            Log_sensor.info("Status: %s" % status_string)
            self.notification_done=True
            self.stopEvent.set()

        if value[0] == 0x22 and value[2] == 0xF3:
            print("Received heartbeat: {}".format(
                int.from_bytes(value[4:6], byteorder='big', signed=False))
                )
            status_string = str(self.ri_error_to_string(value[3]), )
            Log_sensor.info("Status: %s" % status_string)
            self.notification_done = True
            self.stopEvent.set()

        if value[0] == 0x4A or value[0] == 0x21:
            message_return_value = return_values_from_sensor()
            Log_sensor.info("Received: %s" % hexlify(value))
            status_string = str(self.ri_error_to_string(value[3]), )
            Log_sensor.info("Status: %s" % status_string)
            if len(value) == 4:
                test = message_return_value.form_get_status(status=int(value[3]), mac=client.address)
                self.sensor_data.append([test.returnValue.__dict__])
                self.stopEvent.set()
                self.notification_done = True

            elif value[2] == 0x09:

                Log_sensor.info("Received time: %s" % hexlify(value[:-9:-1]))
                received_time=time.strftime('%D %H:%M:%S', time.gmtime(int(hexlify(value[:-9:-1]), 16) / 1000))
                Log_sensor.info(received_time)
                self.sensor_data.append(message_return_value.from_get_time(status=status_string, received_time=received_time,
                                                   mac=client.address).returnValue.__dict__)
                self.stopEvent.set()
                self.notification_done = True

            elif value[0] == 0x4a and value[3] == 0x00:
                sample_rate = ""
                if value[4] == 201:
                    Log_sensor.info("Samplerate: 400 Hz")
                    sample_rate = 400
                else:
                    Log_sensor.info("Samplerate:    %d Hz" % value[4])
                    sample_rate=int(value[4])
                received_config=message_return_value.from_get_config(status=status_string,sample_rate=sample_rate,resolution= int(value[5]),
                                                    scale=int(value[6]),dsp_function=int(value[7]), dsp_parameter=int(value[8]),
                                                    mode="%x"% value[9],divider=int(value[10]), mac=client.address)
                self.sensor_data.append(received_config.returnValue.__dict__)
                self.config = SensorConfig.from_dict(received_config.returnValue.__dict__)
                self.notification_done=True
                self.stopEvent.set()

        elif value[0] == 0xfb and value[1] == 0x0d:
            message_return_value = return_values_from_sensor()
            Log_sensor.info("Received: %s" % hexlify(value))
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
            Log_sensor.info("Last Status %s" % (str(self.ri_error_to_string(logging_status)),))
            Log_sensor.info("Ringbuffer start %d" % (ringbuffer_start,))
            Log_sensor.info("Ringbuffer end %d" % (ringbuffer_end,))
            Log_sensor.info("Ringbuffer size %d" % (ringbuffer_size,))
            Log_sensor.info("Valid records %d" % (valid_records,))
            Log_sensor.info("Dirty records %d" % (dirty_records,))
            Log_sensor.info("Words reserved %d" % (words_reserved,))
            Log_sensor.info("Words used %d" % (words_used,))
            Log_sensor.info("Largest continuos %d" % (largest_contig,))
            Log_sensor.info("Freeable words %d\n" % (freeable_words,))
            self.stopEvent.set()
            self.notification_done = True
    
    def activate_accelerometer_logging(self):
        """Activate accelerometer logging at sensor.
        """        
        Log_sensor.info('Try activate accelerometer logging at {}'.format(self.mac))
        self.work_loop(sensor_interface["commands"]["activate_logging_at_sensor"], sensor_interface["communication_channels"]["UART_TX"])
        return

    def deactivate_accelerometer_logging(self):
        """Deactivate accelerometer logging at sensor.
        """        
        Log_sensor.info('Try deactivate accelerometer logging at {}'.format(self.mac))
        self.work_loop(sensor_interface["commands"]["deactivate_logging_at_sensor"], sensor_interface["communication_channels"]["UART_TX"])
        return 
    
    def get_acceleration_data(self):
        """Get accelerometer data from sensor.
        """         
        Log_sensor.info('Try to get acceleration data from {}'.format(self.mac))
        self.work_loop(sensor_interface["commands"]["get_acceleration_data"] , sensor_interface["communication_channels"]["UART_TX"], True )  
        self.sensordaten = bytearray()      
        return
    
    async def handle_data(self, handle, value):
        """Special callback function to handle incomming accelerometer data.

        :param handle: Artefact of SensorGatewayBleak library. Not in use
        :type handle: [type]
        :param value: Callbacks as bytearray.
        :type value: bytearray
        :return: x,y,z,timestamp
        :rtype: int, int, int, timestamp
        """
              
        if value[0] == 0x11:
            # Daten
            self.sensordaten.extend(value[1:])
            self.start_time = time.time()
            Log_sensor.debug("Received data block: %s" % hexlify(value[1:]))
            # Marks end of data stream
        elif value[0] == 0x4a and value[3] == 0x00:
            message_return_value = return_values_from_sensor()
            self.start_time = time.time()
            self.end_time = time.time()
            print(len(self.sensordaten))
            self.delta = len(self.sensordaten) / (self.end_time - self.start_time)

            Log_sensor.debug('Bandwidth : {} Bytes/Second'.format(self.delta))
            self.stopEvent.set()
            # Status
            Log_sensor.debug("Status: %s" % str(self.ri_error_to_string(value[3])))

            crc = value[12:14]
            Log_sensor.debug("Received CRC: %s" % hexlify(crc))

            # CRC validation
            ourcrc = self.crcfun(self.sensordaten)

            if hexlify(crc) == bytearray():
                Log_sensor.info("No crc received")
                return None

            if int(hexlify(crc), 16) != ourcrc:
                Log_sensor.warning("CRC are unequal")
                return None

            print('Divider: {}'.format(value[10]))
            
            # Start data
            if (value[5] == 12):
                # 12 Bit
                Log_sensor.info("Start processing reveived data with process_sensor_data_12")
                AccelorationData = self.process_data_12(self.sensordaten, value[6], value[4])
            elif (value[5] == 10):
                # 10 Bit
                Log_sensor.info("Start processing reveived data with process_sensor_data_10")
                AccelorationData = self.process_data_10(self.sensordaten, value[6], value[4])
            elif (value[5] == 8):
                # 8 Bit
                Log_sensor.info("Start processing reveived data with process_sensor_data_10")
                AccelorationData = self.process_data_8(self.sensordaten, value[6], value[4])
            else:
                Log_sensor.error('Cant process bytearray! Unknwon sensor resolution!')
            if AccelorationData != None:
                Log_sensor.info("Run in Funktion AccelorationData != None")
                dataList=message_return_value.from_get_accelorationdata(accelorationdata=AccelorationData,mac=self.mac)
                self.data.append(dataList.returnValue.__dict__)
        return
    
    def process_data_8(self, bytes, scale, rate):
        """Parse acceleration data with an resolution of 8 Bit.

        :param bytes: Samples from bytearray
        :type bytes: bytes
        :param scale: Sensor specific scale
        :type scale: int
        :param rate: Sensor specific sampling rate.
        :type rate: int
        :return: x_vector, y_vector, z_vector, timestamp_list
        :rtype: list
        """
        j = 0
        pos = 0
        koords = ["\nx", "y", "z"]
        x_vector = list()
        y_vector = list()
        z_vector = list()
        timestamp_list = list()
        time_between_samples = 1 / rate

        if (scale == 2):
            Log_sensor.info("Scale: 2G")
            faktor = 16 / (256 * 1000)
        elif (scale == 4):
            Log_sensor.info("Scale: 4G")
            faktor = 32 / (256 * 1000)
        elif (scale == 8):
            Log_sensor.info("Scale: 8G")
            faktor = 64 / (256 * 1000)
        elif (scale == 16):
            Log_sensor.info("Scale: 16G")
            faktor = 192 / (256 * 1000)

        while (pos < len(bytes)):
            """Read and store timestamp. This is little endian again"""
            t = bytes[pos:pos + 8]
            inv_t = t[::-1]
            timestamp = int(hexlify(inv_t), 16) / 1000
            pos += 8
            """Read values"""
            for i in range(96):
                value = bytes[pos] << 8
                pos += 1
                if (value & 0x8000 == 0x8000):
                    # negative Zahl
                    # 16Bit Zweierkomplement zurückrechnen
                    value = value ^ 0xffff
                    value += 1
                    # negieren
                    value = -value
                value *= faktor

                Log_sensor.info(timestamp)
                if j % 3 == 0:
                    x_vector.append(value)
                if j % 3 == 1:
                    y_vector.append(value)
                if j % 3 == 2:
                    z_vector.append(value)
                    timestamp_list.append(timestamp)
                    timestamp += time_between_samples
                    Log_sensor.info(datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f'))
                    Log_sensor.info("%d: %s = %f%s" % (j, koords[j % 3], value, "\n" if (j % 3 == 2) else ""))
                j += 1

        Log_sensor.info("%d Werte entpackt" % (j,))
        Log_sensor.info(len(x_vector))
        return x_vector, y_vector, z_vector, timestamp_list

    def process_data_10(self, bytes, scale, rate):
        """Parse acceleration data with an resolution of 10 Bit.

        :param bytes: Samples from bytearray
        :type bytes: bytes
        :param scale: Sensor specific scale
        :type scale: int
        :param rate: Sensor specific sampling rate.
        :type rate: int
        :return: x_vector, y_vector, z_vector, timestamp_list
        :rtype: list
        """
        j = 0
        pos = 0
        koords = ["\nx", "y", "z"]

        x_vector = list()
        y_vector = list()
        z_vector = list()
        timestamp_list = list()
        time_between_samples = 1 / rate

        if (scale == 2):
            Log_sensor.info("Scale: 2G")
            faktor = 4 / (64 * 1000)
        elif (scale == 4):
            Log_sensor.info("Scale: 4G")
            faktor = 8 / (64 * 1000)
        elif (scale == 8):
            Log_sensor.info("Scale: 8G")
            faktor = 16 / (64 * 1000)
        elif (scale == 16):
            Log_sensor.info("Scale: 16G")
            faktor = 48 / (64 * 1000)

        while (pos < len(bytes)):
            Log_sensor.info("Timestamp: %s" % hexlify(bytes[pos + 7:pos:-1]))
            t = bytes[pos:pos + 8]
            inv_t = t[::-1]
            timestamp = int(hexlify(inv_t), 16) / 1000

            pos += 8

            for i in range(24):
                value = bytes[pos] & 0xc0
                value |= (bytes[pos] & 0x3f) << 10
                pos += 1
                value |= (bytes[pos] & 0xc0) << 2
                if (value & 0x8000 == 0x8000):
                    # negative Zahl
                    # 16Bit Zweierkomplement zurückrechnen
                    value = value ^ 0xffff
                    value += 1
                    # negieren
                    value = -value
                value *= faktor
                if j % 3 == 0:
                    x_vector.append(value)
                if j % 3 == 1:
                    y_vector.append(value)
                if j % 3 == 2:
                    timestamp_list.append(timestamp)
                    timestamp += time_between_samples
                    z_vector.append(value)
                Log_sensor.info("%d: %s = %f%s" % (j, koords[j % 3], value, "\n" if (j % 3 == 2) else ""))
                j += 1
                value = (bytes[pos] & 0x30) << 2
                value |= (bytes[pos] & 0x0f) << 12
                pos += 1
                value |= (bytes[pos] & 0xf0) << 4
                if (value & 0x8000 == 0x8000):
                    # negative Zahl
                    # 16Bit Zweierkomplement zurückrechnen
                    value = value ^ 0xffff
                    value += 1
                    # negieren
                    value = -value
                value *= faktor
                if j % 3 == 0:
                    x_vector.append(value)
                if j % 3 == 1:
                    y_vector.append(value)
                if j % 3 == 2:
                    timestamp_list.append(timestamp)
                    timestamp += time_between_samples
                    z_vector.append(value)
                Log_sensor.info("%d: %s = %f%s" % (j, koords[j % 3], value, "\n" if (j % 3 == 2) else ""))
                j += 1
                value = (bytes[pos] & 0x0c) << 4
                value |= (bytes[pos] & 0x03) << 14
                pos += 1
                value |= (bytes[pos] & 0xfc) << 6
                if (value & 0x8000 == 0x8000):
                    # negative Zahl
                    # 16Bit Zweierkomplement zurückrechnen
                    value = value ^ 0xffff
                    value += 1
                    # negieren
                    value = -value
                value *= faktor
                if j % 3 == 0:
                    x_vector.append(value)
                if j % 3 == 1:
                    y_vector.append(value)
                if j % 3 == 2:
                    timestamp_list.append(timestamp)
                    timestamp += time_between_samples
                    z_vector.append(value)
                Log_sensor.info("%d: %s = %f%s" % (j, koords[j % 3], value, "\n" if (j % 3 == 2) else ""))
                j += 1
                value = (bytes[pos] & 0x03) << 6
                pos += 1
                value |= (bytes[pos]) << 8
                pos += 1
                if (value & 0x8000 == 0x8000):
                    # negative Zahl
                    # 16Bit Zweierkomplement zurückrechnen
                    value = value ^ 0xffff
                    value += 1
                    # negieren
                    value = -value
                value *= faktor
                if j % 3 == 0:
                    x_vector.append(value)
                if j % 3 == 1:
                    y_vector.append(value)
                if j % 3 == 2:
                    timestamp_list.append(timestamp)
                    timestamp += time_between_samples
                    z_vector.append(value)
                Log_sensor.info("%d: %s = %f%s" % (j, koords[j % 3], value, "\n" if (j % 3 == 2) else ""))
                j += 1
        Log_sensor.info("%d Werte entpackt" % (j,))
        Log_sensor.info(len(x_vector))
        return x_vector, y_vector, z_vector, timestamp_list

    def process_data_12(self, bytes, scale, rate):
        """Parse acceleration data with an resolution of 12 Bit.

        :param bytes: Samples from bytearray
        :type bytes: bytes
        :param scale: Sensor specific scale
        :type scale: int
        :param rate: Sensor specific sampling rate.
        :type rate: int
        :return: x_vector, y_vector, z_vector, timestamp_list
        :rtype: list
        """
        j = 0
        pos = 0
        koords = ["x", "y", "z"]
        x_vector = list()
        y_vector = list()
        z_vector = list()
        timestamp_list = list()
        time_between_samples = 1 / rate

        if (scale == 2):
            Log_sensor.info("Scale: 2G")
            faktor = 1 / (16 * 1000)
        elif (scale == 4):
            Log_sensor.info("Scale: 4G")
            faktor = 2 / (16 * 1000)
        elif (scale == 8):
            Log_sensor.info("Scale: 8G")
            faktor = 4 / (16 * 1000)
        elif (scale == 16):
            Log_sensor.info("Scale: 16G")
            faktor = 12 / (16 * 1000)

        while (pos < len(bytes)):
            Log_sensor.info("Timestamp: %s" % hexlify(bytes[pos + 7:pos:-1]))
            t = bytes[pos:pos + 8]
            inv_t = t[::-1]
            timestamp = int(hexlify(inv_t), 16) / 1000
            pos += 8

            for i in range(48):
                value = bytes[pos] & 0xf0
                value |= (bytes[pos] & 0x0f) << 12
                pos += 1
                value |= (bytes[pos] & 0xf0) << 4
                if (value & 0x8000 == 0x8000):
                    # negative Zahl
                    # 16Bit Zweierkomplement zurückrechnen
                    value = value ^ 0xffff
                    value += 1
                    # negieren
                    value = -value
                value *= faktor
                if j % 3 == 0:
                    x_vector.append(value)
                if j % 3 == 1:
                    y_vector.append(value)
                if j % 3 == 2:
                    timestamp_list.append(timestamp)
                    timestamp += time_between_samples
                    z_vector.append(value)
                Log_sensor.info("%d: %s = %f%s" % (j, koords[j % 3], value, "\n" if (j % 3 == 2) else ""))
                j += 1
                value = (bytes[pos] & 0x0f) << 4
                pos += 1
                value |= bytes[pos] << 8
                pos += 1
                if (value & 0x8000 == 0x8000):
                    # negative Zahl
                    # 16Bit Zweierkomplement zurückrechnen
                    value = value ^ 0xffff
                    value += 1
                    # negieren
                    value = -value
                value *= faktor
                if j % 3 == 0:
                    x_vector.append(value)
                if j % 3 == 1:
                    y_vector.append(value)
                if j % 3 == 2:
                    timestamp_list.append(timestamp)
                    timestamp += time_between_samples
                    z_vector.append(value)
                Log_sensor.info("%d: %s = %f%s" % (j, koords[j % 3], value, "\n" if (j % 3 == 2) else ""))
                j += 1

        Log_sensor.info("%d unpacked values" % (j,))
        return x_vector, y_vector, z_vector, timestamp_list

        
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
        Log_sensor.info("Setting new config for sensor {}".format(self.mac))
        if sampling_rate == 'FF':
            hex_sampling_rate = 'FF'
        elif sampling_rate in SamplingRate._value2member_map_:
            hex_sampling_rate = SamplingRate(sampling_rate).name[1:]
            Log_sensor.debug("decimal sampling rate is: {}".format(sampling_rate))
            Log_sensor.debug("hex sampling rate is: {}".format(hex_sampling_rate))
        else:
            Log_sensor.warning("Wrong sampling rate! Sampling rate set to 'FF'!")
            hex_sampling_rate = 'FF'
        # Check if arguments are given and valid
        if sampling_resolution == 'FF':
            hex_sampling_resolution = 'FF'
        elif sampling_resolution in SamplingResolution._value2member_map_:
            hex_sampling_resolution = SamplingResolution(sampling_resolution).name[1:]
            Log_sensor.debug("decimal sampling resolution is: {}".format(sampling_resolution))
            Log_sensor.debug("hex sampling resolution is: {}".format(hex_sampling_resolution))
        else:
            Log_sensor.warning("Wrong sampling resolution! Sampling resolution set to 'FF'!")
            hex_sampling_resolution = 'FF'
        # Check if arguments are given and valid
        if measuring_range == 'FF':
            hex_measuring_range = 'FF'
        elif measuring_range in MeasuringRange._value2member_map_:
            hex_measuring_range = MeasuringRange(measuring_range).name[1:]
            Log_sensor.debug("decimal measuring range is: {}".format(measuring_range))
            Log_sensor.debug("hex measuring range is: {}".format(hex_measuring_range))
        else:
            Log_sensor.warning("Wrong measuring range! Measuring range set to 'FF'!")
            hex_measuring_range = 'FF'
        if divider == 'FF':
            hex_divider = 'FF'
            Log_sensor.debug("divider is: {}".format(hex_divider))
        elif int(divider) > 254:
           Log_sensor.error("Divider value too high! (max. 254)") 
           hex_divider = 'FF'
        else:
            div=""
            try:
               div= int(divider)
               Log_sensor.debug("decimal divider is: {}".format(div))
            except Exception as ex :
                Log_sensor.error(str(ex))
                Log_sensor.error("Divider must be an int value")
            if isinstance(div,int):
                hex_divider =hex(div)[2:]
                if len(hex_divider) < 2:
                    hex_divider = '0' + hex_divider
                Log_sensor.debug("hex divider is: {}".format(hex_divider))
            else:
                hex_divider='FF'
        Log_sensor.info("Set sensor configuration {}".format(self.mac))
        command_string = sensor_interface['commands']['substring_set_config_sensor'] + hex_sampling_rate + hex_sampling_resolution + hex_measuring_range + "FFFFFF" + hex_divider + "00"
        self.work_loop(command_string,sensor_interface["communication_channels"]["UART_TX"])
        return
    
    def set_time(self):
        """Set sensor time.
        """        
        now = struct.pack("<Q", int(time.time() * 1000)).hex()
        command=sensor_interface['commands']['substring_set_sensor_time'] + now
        Log_sensor.info("Set sensor time {}".format(self.mac))
        self.work_loop(command,sensor_interface["communication_channels"]["UART_TX"])
        return

    def set_heartbeat(self, heartbeat : int):
        """Change the frequency in which advertisements will be sent.
        The unit of the heartbeet is millisecond [ms]. Just values between 100 ms and
        65.000 ms are permitted.

        :param heartbeat: Frequency of the advertisements in milliseconds.
        :type heartbeat: int
        """
        Log_sensor.info("set heartbeat to: {}".format(heartbeat))
        hex_beat = hex(heartbeat)[2:]
        hex_msg = f"2200F2{'0000'[:4 - len(hex_beat)]}{hex_beat}000000000000"
        self.work_loop(hex_msg, sensor_interface["communication_channels"]["UART_TX"])


    
    def get_flash_statistic(self):
        """Get flash statistic from sensor.
        """        
        Log_sensor.info("Reading flash statistic from {}".format(self.mac))
        self.work_loop(sensor_interface["commands"]["get_flash_statistic"],sensor_interface["communication_channels"]["UART_TX"])
        return
    
    def get_logging_status(self):
        """Get the status of the accelerometer logging.
        """        
        Log_sensor.info("Reading acceleration statistic from {}".format(self.mac))
        self.work_loop(sensor_interface["commands"]["get_logging_status"],sensor_interface["communication_channels"]["UART_TX"])
        return
    
    def get_config(self):
        """Get sensor configurations.
        """        
        Log_sensor.info("Reading config from {}".format(self.mac))
        self.work_loop(sensor_interface["commands"]["get_config_from_sensor"],sensor_interface["communication_channels"]["UART_TX"])
        return    
    
    def get_time(self):
        """Get time from sensor
        """        
        Log_sensor.info("Reading time from {}".format(self.mac))
        self.work_loop(sensor_interface["commands"]["get_time_from_sensor"],sensor_interface["communication_channels"]["UART_TX"])
        return

    def get_heartbeat(self):
        """Get the actuall frequency in which the sensor sends advertisements.
        """        
        Log_sensor.info("get heartbeat...")
        self.work_loop(sensor_interface["commands"]["get_heartbeat"], sensor_interface["communication_channels"]["UART_TX"])
        return
    
    def ri_error_to_string(self, error):
        """Decodes the Tag error, if it was raised.

        :param error: Error value in hex.
        :type error: byte
        :return: Result with decoded error code
        :rtype: [type]
        """
        result = set()
        if (error == 0):
            Log_sensor.info("RD_SUCCESS")
            result.add("RD_SUCCESS")
            self.success = True
        elif(error == 1):
            Log_sensor.error("RD_ERROR_INTERNAL")
            result.add("RD_ERROR_INTERNAL")
        elif(error == 2):
            Log_sensor.error("RD_ERROR_NO_MEM")
            result.add("RD_ERROR_NO_MEM")
        elif(error == 3):
            Log_sensor.error("RD_ERROR_NOT_FOUND")
            result.add("RD_ERROR_NOT_FOUND")
        elif(error == 4):
            Log_sensor.error("RD_ERROR_NOT_SUPPORTED")
            result.add("RD_ERROR_NOT_SUPPORTED")
        elif(error == 5):
            Log_sensor.error("RD_ERROR_INVALID_PARAM")
            result.add("RD_ERROR_INVALID_PARAM")
        elif(error == 6):
            Log_sensor.error("RD_ERROR_INVALID_STATE")
            result.add("RD_ERROR_INVALID_STATE")
        elif(error == 7):
            Log_sensor.error("RD_ERROR_INVALID_LENGTH")
            result.add("RD_ERROR_INVALID_LENGTH")
        elif(error == 8):
            Log_sensor.error("RD_ERROR_INVALID_FLAGS")
            result.add("RD_ERROR_INVALID_FLAGS")
        elif(error == 9):
            Log_sensor.error("RD_ERROR_INVALID_DATA")
            result.add("RD_ERROR_INVALID_DATA")
        elif(error == 10):
            Log_sensor.error("RD_ERROR_DATA_SIZE")
            result.add("RD_ERROR_DATA_SIZE")
        elif(error == 11):
            Log_sensor.error("RD_ERROR_TIMEOUT")
            result.add("RD_ERROR_TIMEOUT")
        elif(error == 12):
            Log_sensor.error("RD_ERROR_NULL")
            result.add("RD_ERROR_NULL")
        elif(error == 13):
            Log_sensor.error("RD_ERROR_FORBIDDEN")
            result.add("RD_ERROR_FORBIDDEN")
        elif(error == 14):
            Log_sensor.error("RD_ERROR_INVALID_ADDR")
            result.add("RD_ERROR_INVALID_ADDR")
        elif(error == 15):
            Log_sensor.error("RD_ERROR_BUSY")
            result.add("RD_ERROR_BUSY")
        elif(error == 16):
            Log_sensor.error("RD_ERROR_RESOURCES")
            result.add("RD_ERROR_RESOURCES")
        elif(error == 17):
            Log_sensor.error("RD_ERROR_NOT_IMPLEMENTED")
            result.add("RD_ERROR_NOT_IMPLEMENTED")
        elif(error == 18):
            Log_sensor.error("RD_ERROR_SELFTEST")
            result.add("RD_ERROR_SELFTEST")
        elif(error == 19):
            Log_sensor.error("RD_STATUS_MORE_AVAILABLE")
            result.add("RD_STATUS_MORE_AVAILABLE")
        elif(error == 20):
            Log_sensor.error("RD_ERROR_NOT_INITIALIZED")
            result.add("RD_ERROR_NOT_INITIALIZED")
        elif(error == 21):
            Log_sensor.error("RD_ERROR_NOT_ACKNOWLEDGED")
            result.add("RD_ERROR_NOT_ACKNOWLEDGED")
        elif(error == 22):
            Log_sensor.error("RD_ERROR_NOT_ENABLED")
            result.add("RD_ERROR_NOT_ENABLED")
        elif(error == 31):
            Log_sensor.error("RD_ERROR_FATAL")
            result.add("RD_ERROR_FATAL")
        return result

    
    def unpack8(self, bytes, samplingrate, scale):
        j = 0
        pos = 0
        accvalues = [0, 0, 0]
        timestamp = 0
        timeBetweenSamples = 1000/samplingrate

        if(scale == 2):
            faktor = 16/(256*1000)
        elif(scale == 4):
            faktor = 32/(256*1000)
        elif(scale == 8):
            faktor = 64/(256*1000)
        elif(scale == 16):
            faktor = 192/(256*1000)

        while(pos < len(bytes)):
            # Ein Datenblock bei 8 Bit Auflösung ist 104 Bytes lang
            # Jeder Datenblock beginnt mit einem Zeitstempel
            if pos % 104 == 0:
                timestamp = int.from_bytes(
                    bytes[pos:pos+7], byteorder='little', signed=False)
                pos += 8
                j = 0

            value = bytes[pos] << 8
            pos += 1
            if(value & 0x8000 == 0x8000):
                # negative Zahl
                # 16Bit Zweierkomplement zurückrechnen
                value = value ^ 0xffff
                value += 1
                # negieren
                value = -value

            # save value
            accvalues[j] = value * faktor

            # Write to CSV
            if(filepointer.csvfile != None and j % 3 == 2):
                if(filepointer.csvfile != None):
                    filepointer.csvfile.write("%d;%f;%f;%f\n" % (
                        timestamp, accvalues[0], accvalues[1], accvalues[1]))
                else:
                    print("%d;%f;%f;%f\n" %
                        (timestamp, accvalues[0], accvalues[1], accvalues[1]))
                timestamp += timeBetweenSamples
                j = 0
            else:
                j += 1

    def unpack10(self, bytes, samplingrate, scale):
        i = 0
        j = 0
        pos = 0
        accvalues = [0, 0, 0]
        timestamp = 0
        timeBetweenSamples = 1000/samplingrate

        if(scale == 2):
            faktor = 4/(64*1000)
        elif(scale == 4):
            faktor = 8/(64*1000)
        elif(scale == 8):
            faktor = 16/(64*1000)
        elif(scale == 16):
            faktor = 48/(64*1000)

        while(pos < len(bytes)-1):
            # Ein Datenblock bei 10 Bit Auflösung ist 128 Bytes lang
            # Jeder Datenblock beginnt mit einem Zeitstempel
            if pos % 128 == 0:
                timestamp = int.from_bytes(
                    bytes[pos:pos+7], byteorder='little', signed=False)
                pos += 8
                i = 0
                j = 0

            else:
                if i == 0:
                    value = bytes[pos] & 0xc0
                    value |= (bytes[pos] & 0x3f) << 10
                    pos += 1
                    value |= (bytes[pos] & 0xc0) << 2
                    i += 1

                elif i == 1:
                    value = (bytes[pos] & 0x30) << 2
                    value |= (bytes[pos] & 0x0f) << 12
                    pos += 1
                    value |= (bytes[pos] & 0xf0) << 4
                    i += 1

                elif i == 2:
                    value = (bytes[pos] & 0x0c) << 4
                    value |= (bytes[pos] & 0x03) << 14
                    pos += 1
                    value |= (bytes[pos] & 0xfc) << 6
                    i += 1

                elif i == 3:
                    value = (bytes[pos] & 0x03) << 6
                    pos += 1
                    value |= (bytes[pos]) << 8
                    pos += 1
                    i = 0

                if(value & 0x8000 == 0x8000):
                    # negative Zahl
                    # 16Bit Zweierkomplement zurückrechnen
                    value = value ^ 0xffff
                    value += 1
                    # negieren
                    value = -value

                # save value
                accvalues[j] = value * faktor

                j += 1

                # Write to CSV
                if(j == 3):
                    if(filepointer.csvfile != None):
                        filepointer.csvfile.write("%d;%f;%f;%f\n" % (
                            timestamp, accvalues[0], accvalues[1], accvalues[2]))
                    else:
                        print("%d;%f;%f;%f" %
                            (timestamp, accvalues[0], accvalues[1], accvalues[2]))
                    timestamp += timeBetweenSamples
                    j = 0


    def unpack12(self, bytes, samplingrate, scale):
        i = 0
        j = 0
        pos = 0
        accvalues = [0, 0, 0]
        timestamp = 0
        timeBetweenSamples = 1000/samplingrate

        if(scale == 2):
            faktor = 1/(16*1000)
        elif(scale == 4):
            faktor = 2/(16*1000)
        elif(scale == 8):
            faktor = 4/(16*1000)
        elif(scale == 16):
            faktor = 12/(16*1000)

        while(pos < len(bytes)-1):
            # Ein Datenblock bei 12 Bit Auflösung ist 152 Bytes lang
            # Jeder Datenblock beginnt mit einem Zeitstempel
            if pos % 152 == 0:
                timestamp = int.from_bytes(
                    bytes[pos:pos+7], byteorder='little', signed=False)
                pos += 8
                i = 0
                j = 0

            else:
                if i == 0:
                    value = bytes[pos] & 0xf0
                    value |= (bytes[pos] & 0x0f) << 12
                    pos += 1
                    value |= (bytes[pos] & 0xf0) << 4
                    i += 1

                elif i == 1:
                    value = (bytes[pos] & 0x0f) << 4
                    pos += 1
                    value |= bytes[pos] << 8
                    pos += 1
                    i = 0

                if(value & 0x8000 == 0x8000):
                    # negative Zahl
                    # 16Bit Zweierkomplement zurückrechnen
                    value = value ^ 0xffff
                    value += 1
                    # negieren
                    value = -value

                # save value
                accvalues[j] = value * faktor

                j += 1

                # Write to CSV
                if(j == 3):
                    if(filepointer.csvfile != None):
                        filepointer.csvfile.write("%d;%f;%f;%f\n" % (
                            timestamp, accvalues[0], accvalues[1], accvalues[2]))
                    else:
                        print("%d;%f;%f;%f" %
                            (timestamp, accvalues[0], accvalues[1], accvalues[2]))
                    timestamp += timeBetweenSamples
                    j = 0

        
    def callback(self, sender: int, value: bytearray):
        # self.process_data_12(sensordaten, value[6], value[4])
        print("Received: %s" % binascii.hexlify(value, "-"))
        if value[0] == 0x4A:
            print("Sender: %s" % sender)
            print("Status: %s" % (str(self.ri_error_to_string(value[3]),)))
            self.stopevent.set()
        elif value[0] == 0x11:
            # self.sensor_data
            if self.config.resolution == 8:
                self.unpack8(value[1:], self.config.sample_rate, self.config.scale)
            elif self.config.resolution == 10:
                self.unpack10(value[1:], self.config.sample_rate, self.config.scale)
            elif self.config.resolution == 12:
                self.unpack12(value[1:], self.config.sample_rate, self.config.scale)
                
    async def setup_for_streaming(self):
        """Change mode to gatt streaming.
        """
        UART_RX = sensor_interface["communication_channels"]["UART_RX"]
        UART_TX = sensor_interface["communication_channels"]["UART_TX"]
        async with BleakClient(self.config.mac) as client:
            await client.start_notify(UART_RX, self.callback)
            await client.write_gatt_char(UART_TX, bytearray.fromhex("4a4a03%02x%02x%02xFFFFFF0000" % (self.config.sample_rate, self.config.resolution, self.config.scale)))
            await asyncio.sleep(10)
            await self.stopevent.wait()
            print("Samplerate set")
            await client.stop_notify(UART_RX)
            self.stopevent.clear()

    async def activate_streaming(self):
        """Start streaming and receive data.
        """
        UART_RX = sensor_interface["communication_channels"]["UART_RX"]
        UART_TX = sensor_interface["communication_channels"]["UART_TX"]
        async with BleakClient(self.config.mac) as client:
            await client.start_notify(UART_RX, self.callback)
            await client.write_gatt_char(UART_TX, bytearray.fromhex(sensor_interface["commands"]["activate_streaming"]))
            print("Streaming activated")
            await self.stopevent.wait()
            await client.stop_notify(UART_RX)

    async def listen_for_data(self, samplingtime=10*60, filename = str(int(time.time()))+".csv"):
        """Listens for incoming data and writes them to a specified csv file.

        :param samplingtime: hearbeat time
        :type samplingtime: int
        :param filename: name of csv
        :type filename: string
        """
        UART_RX = sensor_interface["communication_channels"]["UART_RX"]
        UART_TX = sensor_interface["communication_channels"]["UART_TX"]
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
