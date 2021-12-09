"""
An object of type sensor is an digital twin of a hardware sensor.
"""
import struct
import logging
import os.path
import yaml
import asyncio
from bleak import BleakClient
import time
from functools import partial #Ist das notwendig
from gateway.sensor import SensorConfigEnum
from functools import hexlify
import datetime
from gateway.SensorConfigEnum import SamplingRate, SamplingResolution,MeasuringRange
from gateway.MessageObjects import return_values_from_sensor
import crcmod

with open(os.path.dirname(__file__)+ '/../communication_interface.yml') as ymlfile:
    sensor_interface = yaml.safe_load(ymlfile)


# Creat a named logger 'sensor' and set it on INFO level
Log_sensor = logging.getLogger('SensorGatewayBleak')
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
Log_sensor.addHandler(console_handler)

crcfun = crcmod.mkCrcFun(0x11021, rev=False, initCrc=0xffff, xorOut=0)

class Event_ts(asyncio.Event):
    """
    Custom event loop class for the RuuviTagAccelerometerCommunicationBleak.
    """
    def clear(self):
        self._loop.call_soon_threadsafe(super().clear)

    def set(self):
        self._loop.call_soon_threadsafe(super().set)


class sensor(object):
    
    def __init__(self,name, mac):
        self.mac = mac
        self.name = name      
        self.main_loop = asyncio.get_event_loop()
        self.Event_ts = Event_ts()
        return
    
    async def killswitch(self):
        Log_sensor.info("Start timeout function")
        while time.time()-self.start_time < 2 :
            Log_sensor.warning("Timeout timer running {}".format(time.strftime("%H:%M:%S",time.localtime(self.start_time))))
            await asyncio.sleep(1)
        try:
            self.stopEvent.set()
        except:
            pass
    async def killswitch_for_commands(self):
            Log_sensor.info("Start timeout function")
            while time.time() - self.start_time < 10:
                Log_sensor.warning(
                    "Timeout timer running {}".format(time.strftime("%H:%M:%S", time.localtime(self.start_time))))
                await asyncio.sleep(1)
                if self.notification_done:
                    self.notification_done = False
                    break
            try:
                self.stopEvent.set()
            except:
                pass
    
    def work_loop(self, command):
        self.taskobj = self.my_loop.create_task(self.connect_to_mac_command(command))
        try:
            self.my_loop.run_until_complete(self.taskobj)
        except Exception as e:
            Log_sensor.error("Exception occured: {}".format(e))
        return
    
    async def connect_ble_sensor(self, command_string): #Vll muss hier noch der channel und die callback funktion rein
        Log_sensor.info("Send {} to MAC {} ".format(self.mac,command_string))
        try:
            async with BleakClient(self.mac) as client:
                # Send the command (Wait for Response must be True)
                await client.start_notify(sensor_interface["communication_channels"]["UART_RX"] , partial(self.handle_ble_callback , client))
                await client.write_gatt_char(sensor_interface["communication_channels"]["UART_RX"],
                                             bytearray.fromhex(command_string), True)
                Log_sensor.info('Message send to MAC: %s' % (self.mac))

                self.start_time = time.time()
                Log_sensor.info("Set Processtimer")
                await self.killswitch_for_commands()
                Log_sensor.info("Killswitch starts monitoring")
                await self.stopEvent.wait()
                Log_sensor.warning("Abort workloop Task via Killswtch after timeout!")
                await client.stop_notify(sensor_interface["communication_channels"]["UART_RX"])
                self.stopEvent.clear()
                Log_sensor.info('Stop notify: %s' % (self.mac))
                Log_sensor.info("Task done connect_to_mac_command!")
        except Exception as e:
            Log_sensor.warning('Connection faild at MAC %s' % (self.mac))
            Log_sensor.error("Error: {}".format(e))

        return
    
    def handle_ble_callback(self, client: BleakClient,sender: int, value: bytearray):
        if value[0] == 0x4A or value[0] == 0x21:
            message_return_value = return_values_from_sensor()
            self.logger.info("Received: %s" % hexlify(value))
            status_string=str(self.ri_error_to_string(value[3]), )
            self.logger.info("Status: %s" % status_string)
            if len(value) == 4:
                test=message_return_value.form_get_status(status=int(value[3]), mac=client.address)
                self.sensor_data.append([test.returnValue.__dict__])
                self.stopEvent.set()
                self.notification_done = True

            elif value[2] == 0x09:

                self.logger.info("Received time: %s" % hexlify(value[:-9:-1]))
                recieved_time=time.strftime('%D %H:%M:%S', time.gmtime(int(hexlify(value[:-9:-1]), 16) / 1000))
                self.logger.info(recieved_time)
                self.sensor_data.append([message_return_value.from_get_time(status=status_string, recieved_time=recieved_time,
                                                   mac=client.address).returnValue.__dict__])
                self.stopEvent.set()
                self.notification_done = True

            elif value[0] == 0x4a and value[3] == 0x00:
                sample_rate=""
                if value[4] == 201:
                    self.logger.info("Samplerate: 400 Hz")
                    sample_rate=400
                else:
                    self.logger.info("Samplerate:    %d Hz" % value[4])
                    sample_rate=int(value[4])
                recieved_config=message_return_value.from_get_config(status=status_string,sample_rate=sample_rate,resolution= int(value[5]),
                                                    scale=int(value[6]),dsp_function=int(value[7]), dsp_parameter=int(value[8]),
                                                    mode="%x"% value[9],divider=int(value[10]), mac=client.address)
                self.sensor_data.append([recieved_config.returnValue.__dict__])
                self.notification_done=True
                self.stopEvent.set()

        elif value[0] == 0xfb and value[1] == 0x0d:
            message_return_value = return_values_from_sensor()
            self.logger.info("Received: %s" % hexlify(value))
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
            recieved_flash_statistic=message_return_value.from_get_flash_statistics(
            logging_status=logging_status, ringbuffer_start=ringbuffer_start,
            ringbuffer_end=ringbuffer_end, ringbuffer_size=ringbuffer_size, valid_records=valid_records, dirty_records=dirty_records,
            words_reserved=words_reserved, words_used= words_used, largest_contig=largest_contig, freeable_words=freeable_words,
            mac=client.address)
            self.sensor_data.append([recieved_flash_statistic.returnValue.__dict__])
            self.logger.info("Last Status %s" % (str(self.ri_error_to_string(logging_status)),))
            self.logger.info("Ringbuffer start %d" % (ringbuffer_start,))
            self.logger.info("Ringbuffer end %d" % (ringbuffer_end,))
            self.logger.info("Ringbuffer size %d" % (ringbuffer_size,))
            self.logger.info("Valid records %d" % (valid_records,))
            self.logger.info("Dirty records %d" % (dirty_records,))
            self.logger.info("Words reserved %d" % (words_reserved,))
            self.logger.info("Words used %d" % (words_used,))
            self.logger.info("Largest continuos %d" % (largest_contig,))
            self.logger.info("Freeable words %d\n" % (freeable_words,))
            self.stopEvent.set()
            self.notification_done = True
    
    def activate_acceleromerter_logging(self):
        Log_sensor.info('Try activate accelerometer logging at {}'.format(self.mac))
        self.work_loop(sensor_interface["ruuvi_commands"]["activate_logging_at_sensor"])
        return

    def deactivate_acceleromerter_logging(self):
        Log_sensor.info('Try deactivate accelerometer logging at {}'.format(self.mac))
        self.work_loop(sensor_interface["ruuvi_commands"]["deactivate_logging_at_sensor"])
        return 
    
    def get_acceleration_data(self):
        global sensordaten
        Log_sensor.info('Try to get acceleration data from {}'.format(self.mac))
        taskobj = self.my_loop.create_task(self.connect_to_mac(self.mac, sensor_interface["ruuvi_commands"]["get_acceleration_data"] ))
        self.my_loop.run_until_complete(taskobj)        
        return
    
    async def handle_data(self,value):
        if value[0] == 0x11:
            # Daten
            sensordaten.extend(value[1:])
            self.start_time = time.time()
            Log_sensor.debug("Received data block: %s" % hexlify(value[1:]))
            # Marks end of data stream
        elif value[0] == 0x4a and value[3] == 0x00:
            message_return_value = return_values_from_sensor()
            self.start_time = time.time()
            self.end_time = time.time()
            print(len(sensordaten))
            self.delta = len(sensordaten) / (self.end_time - self.start_time)

            self.logger.debug('Bandwidth : {} Bytes/Second'.format(self.delta))
            self.stopEvent.set()
            # Status
            self.logger.debug("Status: %s" % str(self.ri_error_to_string(value[3])))

            crc = value[12:14];
            self.logger.debug("Received CRC: %s" % hexlify(crc))

            # CRC validation
            ourcrc = crcfun(sensordaten)

            print("Received %d bytes" % len(sensordaten))
            #print(hexlify(crc))
            if hexlify(crc) == bytearray():
                self.logger.info("No crc received")
                return None

            if int(hexlify(crc), 16) != ourcrc:
                self.logger.warning("CRC are unequal")
                return None


            timeStamp = hexlify(sensordaten[7::-1])

            # Start data
            if (value[5] == 12):
                # 12 Bit
                self.logger.info("Start processing reveived data with process_sensor_data_12")
                AccelorationData = self.process_sensor_data_12(sensordaten, value[6], value[4])
            elif (value[5] == 10):
                # 10 Bit
                self.logger.info("Start processing reveived data with process_sensor_data_10")
                AccelorationData = self.process_sensor_data_10(sensordaten, value[6], value[4])
            elif (value[5] == 8):
                # 8 Bit
                self.logger.info("Start processing reveived data with process_sensor_data_10")
                AccelorationData = self.process_sensor_data_8(sensordaten, value[6], value[4])
            else:
                print("Unknown Resolution")
            if AccelorationData != None:
                self.logger.info("Run in Funktion AccelorationData != None")
                dataList=message_return_value.from_get_accelorationdata(accelorationdata=AccelorationData,mac=self.current_mac)
                self.data.append(dataList.returnValue.__dict__)
        return
    
    def process_data_8(self, bytes, scale, rate):
        j = 0
        pos = 0
        koords = ["\nx", "y", "z"]
        x_vector = list()
        y_vector = list()
        z_vector = list()
        timestamp_list = list()
        time_between_samples = 1 / rate

        if (scale == 2):
            self.logger.info("Scale: 2G")
            faktor = 16 / (256 * 1000)
        elif (scale == 4):
            self.logger.info("Scale: 4G")
            faktor = 32 / (256 * 1000)
        elif (scale == 8):
            self.logger.info("Scale: 8G")
            faktor = 64 / (256 * 1000)
        elif (scale == 16):
            self.logger.info("Scale: 16G")
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

                self.logger.info(timestamp)
                if j % 3 == 0:
                    x_vector.append(value)
                if j % 3 == 1:
                    y_vector.append(value)
                if j % 3 == 2:
                    z_vector.append(value)
                    timestamp += time_between_samples
                    Log_sensor.info(datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f'))
                    timestamp_list.append(
                        datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f'))
                self.logger.info("%d: %s = %f%s" % (j, koords[j % 3], value, "\n" if (j % 3 == 2) else ""))
                j += 1

        self.logger.info("%d Werte entpackt" % (j,))
        self.logger.info(len(x_vector))
        return x_vector, y_vector, z_vector, timestamp_list

    def process_data_10(self, bytes, scale, rate):
        runtime = time.time() - self.start_time
        j = 0
        pos = 0
        koords = ["\nx", "y", "z"]

        x_vector = list()
        y_vector = list()
        z_vector = list()
        timestamp_list = list()
        time_between_samples = 1 / rate

        if (scale == 2):
            self.logger.info("Scale: 2G")
            faktor = 4 / (64 * 1000)
        elif (scale == 4):
            self.logger.info("Scale: 4G")
            faktor = 8 / (64 * 1000)
        elif (scale == 8):
            self.logger.info("Scale: 8G")
            faktor = 16 / (64 * 1000)
        elif (scale == 16):
            self.logger.info("Scale: 16G")
            faktor = 48 / (64 * 1000)

        while (pos < len(bytes)):
            self.logger.info("Timestamp: %s" % hexlify(bytes[pos + 7:pos:-1]))
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
                    timestamp += time_between_samples
                    timestamp_list.append(
                        datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f'))
                    z_vector.append(value)
                self.logger.info("%d: %s = %f%s" % (j, koords[j % 3], value, "\n" if (j % 3 == 2) else ""))
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
                    timestamp += time_between_samples
                    timestamp_list.append(
                        datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f'))
                    z_vector.append(value)
                self.logger.info("%d: %s = %f%s" % (j, koords[j % 3], value, "\n" if (j % 3 == 2) else ""))
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
                    timestamp += time_between_samples
                    timestamp_list.append(
                        datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f'))
                    z_vector.append(value)
                self.logger.info("%d: %s = %f%s" % (j, koords[j % 3], value, "\n" if (j % 3 == 2) else ""))
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
                    timestamp += time_between_samples
                    timestamp_list.append(
                        datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f'))

                    z_vector.append(value)
                self.logger.info("%d: %s = %f%s" % (j, koords[j % 3], value, "\n" if (j % 3 == 2) else ""))
                j += 1
        self.logger.info((j / runtime))
        self.logger.info("%d Werte entpackt" % (j,))
        self.logger.info(len(x_vector))
        return x_vector, y_vector, z_vector, timestamp_list

    def process_data_12(self, bytes, scale, rate):
        j = 0
        pos = 0
        koords = ["x", "y", "z"]
        x_vector = list()
        y_vector = list()
        z_vector = list()
        timestamp_list = list()
        time_between_samples = 1 / rate

        if (scale == 2):
            self.logger.info("Scale: 2G")
            faktor = 1 / (16 * 1000)
        elif (scale == 4):
            self.logger.info("Scale: 4G")
            faktor = 2 / (16 * 1000)
        elif (scale == 8):
            self.logger.info("Scale: 8G")
            faktor = 4 / (16 * 1000)
        elif (scale == 16):
            self.logger.info("Scale: 16G")
            faktor = 12 / (16 * 1000)

        while (pos < len(bytes)):
            self.logger.info("Timestamp: %s" % hexlify(bytes[pos + 7:pos:-1]))
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
                    timestamp_list.append(
                        datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f'))
                    timestamp += time_between_samples
                    z_vector.append(value)
                self.logger.info("%d: %s = %f%s" % (j, koords[j % 3], value, "\n" if (j % 3 == 2) else ""))
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
                    timestamp += time_between_samples
                    timestamp_list.append(
                        datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f'))
                    z_vector.append(value)
                self.logger.info("%d: %s = %f%s" % (j, koords[j % 3], value, "\n" if (j % 3 == 2) else ""))
                j += 1

        self.logger.info("%d Werte entpackt" % (j,))
        return x_vector, y_vector, z_vector, timestamp_list

        
    def set_sensor_config(self, sampling_rate='FF', sampling_resolution='FF', measuring_range='FF',
                          divider="FF"):
        if sampling_rate == 'FF':
            hex_sampling_rate = 'FF'
        elif sampling_rate in SamplingRate._value2member_map_:
            hex_sampling_rate = SamplingRate(sampling_rate).name[1:]
        else:
            Log_sensor.warning("Wrong sampling rate")
            hex_sampling_rate = 'FF'
        # Check if arguments are given and valid
        if sampling_resolution == 'FF':
            hex_sampling_resolution = 'FF'
        elif sampling_resolution in SamplingResolution._value2member_map_:
            hex_sampling_resolution = SamplingResolution(sampling_resolution).name[1:]
        else:
            Log_sensor.warning("Wrong sampling resolution")
            hex_sampling_resolution = 'FF'
        # Check if arguments are given and valid
        if measuring_range == 'FF':
            hex_measuring_range = 'FF'
        elif measuring_range in MeasuringRange._value2member_map_:
            hex_measuring_range = MeasuringRange(measuring_range).name[1:]
        else:
            Log_sensor.warning("Wrong measuring range")
            hex_measuring_range = 'FF'
        if divider == 'FF':
            hex_divider = 'FF'
        else:
            div=""
            try:
               div= int(divider)
            except Exception as ex :
                Log_sensor.error(str(ex))
                Log_sensor.warning("Divider must be an int value")
            if isinstance(div,int):
                hex_divider =hex(div)[2:]
            else:
                hex_divider='FF'
        Log_sensor.info("Set sensor configuration {}".format(self.mac))
        command_string = sensor_interface['ruuvi_commands']['substring_set_config_sensor'] + hex_sampling_rate + hex_sampling_resolution + hex_measuring_range + "FFFFFF" + hex_divider + "00"
        self.work_loop(command_string)
        return
    
    def set_sensor_time(self):
        now = struct.pack("<Q", int(time.time() * 1000)).hex()
        command=sensor_interface['ruuvi_commands']['substring_set_sensor_time'] + now
        Log_sensor.info("Reading flash statistic from {}".format(self.mac))
        self.work_loop(command)
        return
    
    def get_flash_statistic(self):
        Log_sensor.info("Reading flash statistic from {}".format(self.mac))
        self.work_loop(command=sensor_interface["ruuvi_commands"]["get_flash_statistic"])
        return
    
    def get_acceleration_status(self):
        Log_sensor.info("Reading acceleration statistic from {}".format(self.mac))
        self.work_loop(command=sensor_interface["ruuvi_commands"]["get_logging_status"])
        return
    
    def get_sensor_config(self):
        Log_sensor.info("Reading config from {}".format(self.mac))
        self.work_loop(command=sensor_interface["ruuvi_commands"]["get_time_from_sensor"])
        return    
    
    def get_sensor_time(self):
        Log_sensor.info("Reading time from {}".format(self.mac))
        self.work_loop(command=sensor_interface["ruuvi_commands"]["get_time_from_sensor"])
        return
    
    def ri_error_to_string(self, error):
        """
        Decodes the RuuviTag error, if it was raised.
        
        :returns:
            result : set
                A set of occured errors.
        """
        result = set()
        if (error == 0):
            Log_sensor.info("RD_SUCCESS")
            result.add("RD_SUCCESS")
            self.success = True
        elif(error==1):
            Log_sensor.error("RD_ERROR_INTERNAL")
            result.add("RD_ERROR_INTERNAL")
        elif(error==2):
            Log_sensor.error("RD_ERROR_NO_MEM")
            result.add("RD_ERROR_NO_MEM")
        elif(error==3):
            Log_sensor.error("RD_ERROR_NOT_FOUND")
            result.add("RD_ERROR_NOT_FOUND")
        elif(error==4):
            Log_sensor.error("RD_ERROR_NOT_SUPPORTED")
            result.add("RD_ERROR_NOT_SUPPORTED")
        elif(error==5):
            Log_sensor.error("RD_ERROR_INVALID_PARAM")
            result.add("RD_ERROR_INVALID_PARAM")
        elif(error==6):
            Log_sensor.error("RD_ERROR_INVALID_STATE")
            result.add("RD_ERROR_INVALID_STATE")
        elif(error==7):
            Log_sensor.error("RD_ERROR_INVALID_LENGTH")
            result.add("RD_ERROR_INVALID_LENGTH")
        elif(error==8):
            Log_sensor.error("RD_ERROR_INVALID_FLAGS")
            result.add("RD_ERROR_INVALID_FLAGS")
        elif(error==9):
            Log_sensor.error("RD_ERROR_INVALID_DATA")
            result.add("RD_ERROR_INVALID_DATA")
        elif(error==10):
            Log_sensor.error("RD_ERROR_DATA_SIZE")
            result.add("RD_ERROR_DATA_SIZE")
        elif(error==11):
            Log_sensor.error("RD_ERROR_TIMEOUT")
            result.add("RD_ERROR_TIMEOUT")
        elif(error==12):
            Log_sensor.error("RD_ERROR_NULL")
            result.add("RD_ERROR_NULL")
        elif(error==13):
            Log_sensor.error("RD_ERROR_FORBIDDEN")
            result.add("RD_ERROR_FORBIDDEN")
        elif(error==14):
            Log_sensor.error("RD_ERROR_INVALID_ADDR")
            result.add("RD_ERROR_INVALID_ADDR")
        elif(error==15):
            Log_sensor.error("RD_ERROR_BUSY")
            result.add("RD_ERROR_BUSY")
        elif(error==16):
            Log_sensor.error("RD_ERROR_RESOURCES")
            result.add("RD_ERROR_RESOURCES")
        elif(error==17):
            Log_sensor.error("RD_ERROR_NOT_IMPLEMENTED")
            result.add("RD_ERROR_NOT_IMPLEMENTED")
        elif(error==18):
            Log_sensor.error("RD_ERROR_SELFTEST")
            result.add("RD_ERROR_SELFTEST")
        elif(error==19):
            Log_sensor.error("RD_STATUS_MORE_AVAILABLE")
            result.add("RD_STATUS_MORE_AVAILABLE")
        elif(error==20):
            Log_sensor.error("RD_ERROR_NOT_INITIALIZED")
            result.add("RD_ERROR_NOT_INITIALIZED")
        elif(error==21):
            Log_sensor.error("RD_ERROR_NOT_ACKNOWLEDGED")
            result.add("RD_ERROR_NOT_ACKNOWLEDGED")
        elif(error==22):
            Log_sensor.error("RD_ERROR_NOT_ENABLED")
            result.add("RD_ERROR_NOT_ENABLED")
        elif(error==31):
            Log_sensor.error("RD_ERROR_FATAL")
            result.add("RD_ERROR_FATAL")
        return result    
        