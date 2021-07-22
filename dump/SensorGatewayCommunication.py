from ruuvitag_sensor.ruuvi import RuuviTagSensor, RunFlag
import time
import struct
from interruptingcow import timeout
import pygatt
import logging
import crcmod
import datetime
import re
from enum import Enum
from binascii import hexlify

logging.basicConfig()
logging.getLogger('pygatt').setLevel(logging.INFO)
data = []
macSet = set()
macList = []
readAllString = "FAFA030000000000000000"
uuIdWrite = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
uuIdRead = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"
waitTime = 1
crcfun = crcmod.mkCrcFun(0x11021, rev=False, initCrc=0xffff, xorOut=0)
test = RuuviTagSensor._get_ruuvitag_datas(search_duratio_sec=2)
cnt = 0

#region enums for sensor config
class SamplingRate(Enum):
    x01 = 1
    x0A = 10
    x19 = 25
    x32 = 50
    x64 = 100
    xC8 = 200
    xC9 = 400


class SamplingResolution(Enum):
    x08 = 8
    x0A = 10
    x0C = 12


class MeasuringRange(Enum):
    x02 = 2
    x04 = 4
    x08 = 8
    x10 = 16
#endregion

class RuuviTagAccelerometerCommunication:

    def __init__(self):
        global mac
        global adapter
        self.data = []
        self.reading_done=False
        self.ConnectionError = False
        print("ini start")

        mac = self.find_tags_mac()
        adapter = pygatt.GATTToolBackend()
        adapter.start()
        print("ini done")

    '''
    Activate acceleration logging.
    '''

    def activate_logging_at_sensor(self, specific_mac=""):
        global mac
        global adapter
        command_string = "FAFA0a0100000000000000"
        if specific_mac != "":
            if re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", specific_mac.lower()):
                mac = [specific_mac]
            else:
                print("Mac is not valid")
                return
        else:
            mac = self.find_tags_mac()
        try:
            self.connect_to_mac_command(command_string)
           # print("logging activated")
            adapter.reset()
        except RuntimeError as e:
            print("Error: {}".format(e))
        print("logging activated")

    '''
    Deactivate acceleration logging.
    Deletes ringbuffer.
    '''

    def deactivate_logging_at_sensor(self, specific_mac=""):
        global mac
        global adapter
        if specific_mac != "":
            if re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", specific_mac.lower()):
                mac = [specific_mac]
            else:
                print("Mac is not valid")
                return
        else:
            mac = self.find_tags_mac()
        command_string = "FAFA0a0000000000000000"
        try:
            self.connect_to_mac_command(command_string)
            adapter.reset()
        except RuntimeError as e:
            print("Error: {}".format(e))

    def set_config_sensor(self, specific_mac="", sampling_rate='FF', sampling_resolution='FF', measuring_range='FF'):
        global mac
        global adapter
        """Check if arguments are given and valid"""
        if sampling_rate == 'FF':
            hex_sampling_rate = 'FF'
        elif sampling_rate in SamplingRate._value2member_map_:
            hex_sampling_rate = SamplingRate(sampling_rate).name[1:]
        else:
            print("Wrong sampling rate")
            hex_sampling_rate = 'FF'
        """Check if arguments are given and valid"""
        if sampling_resolution == 'FF':
            hex_sampling_resolution = 'FF'
        elif sampling_resolution in SamplingResolution._value2member_map_:
            hex_sampling_resolution = SamplingResolution(sampling_resolution).name[1:]
        else:
            print("Wrong sampling resolution")
            hex_sampling_resolution = 'FF'
        """Check if arguments are given and valid"""
        if measuring_range == 'FF':
            hex_measuring_range = 'FF'
        elif measuring_range in MeasuringRange._value2member_map_:
            hex_measuring_range = MeasuringRange(measuring_range).name[1:]
        else:
            hex_measuring_range = 'FF'
        """Exit function if no changes are made"""
        if (hex_sampling_rate == "FF") and (hex_sampling_resolution == "FF") and (hex_measuring_range == "FF"):
            print("No changes are made. Try again with correct values")
            adapter.reset()
            return
        """Check if mac address is valid"""
        if specific_mac != "":
            if re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", specific_mac.lower()):
                mac = [specific_mac]
            else:
                print("Mac is not valid")
                return
        else:
            mac = self.find_tags_mac()
        """Create command string and send it to targets"""
        command_string = "FAFA06" + hex_sampling_rate + hex_sampling_resolution + hex_measuring_range + "FFFFFF0000"
        self.connect_to_mac_command(command_string)
        """Adapter reset is required, to connect to other sensors without restart everything """
        adapter.reset()

    """Get configuration from sensors"""
    def get_config_from_sensor(self, specific_mac=""):
        global mac
        global adapter
        """Check if mac address is valid"""
        if specific_mac != "":
            if re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", specific_mac.lower()):
                mac = [specific_mac]
            else:
                print("Mac is not valid")
                return
        else:
            mac = self.find_tags_mac()
        command_string = "FAFA070000000000000000"
        self.connect_to_mac_command(command_string)
        adapter.reset()

    """Get time from sensors"""
    def get_time_from_sensor(self,specific_mac=""):
        global mac
        global adapter
        if specific_mac != "":
            if re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", specific_mac.lower()):
                mac = [specific_mac]
            else:
                print("Mac is not valid")
        else:
            mac = self.find_tags_mac()
        command_string = "FAFA090000000000000000"
        self.connect_to_mac_command(command_string)
        adapter.reset()

    """Set sensor time"""
    def set_sensor_time(self,specific_mac=""):
        global mac
        global adapter
        if specific_mac != "":
            if re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", specific_mac.lower()):
                mac = [specific_mac]
            else:
                print("Mac is not valid")
                return
        else:
            mac = self.find_tags_mac()
        """Time has to be little endian and 16 bit long"""
        timestamp = struct.pack("<Q", int(time.time() * 1000)).hex()

        command_string = "FAFA08" + timestamp
        self.connect_to_mac_command(command_string)
        adapter.reset()

    """Gets the last 32 acceleration samples"""
    def get_last_sample_acceleration_data(self,specific_mac=""):
        global mac
        global adapter
        global readAllString
        self.data = []
        self.ConnectionError = False

        readAllString = "FAFA030000000000000000"
        if specific_mac != "":
            if re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", specific_mac.lower()):
                mac = [specific_mac]
            else:
                print("Mac is not valid")
                return
        else:
            mac = self.find_tags_mac()
        """Read acceleration samples for each sensor"""
        for i in mac:
            self.reading_done = False
            if adapter._running.is_set() == False:
                print("Need to start adapter")
                adapter = pygatt.GATTToolBackend()
                adapter.start()
            self.connect_to_mac(adapter, i, readAllString)
            """Wait  until all reading is done. We can only read one sensor at the time"""
            while not self.reading_done:
                time.sleep(1)

        print(self.data)
        adapter.reset()

    """Gets all acceleration samples and store them in a csv file"""
    def get_acceleration_data(self,specific_mac=""):
        global mac
        global adapter
        global readAllString
        self.data = []
        self.ConnectionError=False
        readAllString = "FAFA050000000000000000"
        if specific_mac != "":
            if re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", specific_mac.lower()):
                mac = [specific_mac]
            else:
                print("Mac is not valid")
                return
        else:
            mac = self.find_tags_mac()

        """Read acceleration samples for each sensor"""
        for i in mac:
            self.reading_done=False
            if adapter._running.is_set() == False:
                print("Need to start adapter")
                adapter = pygatt.GATTToolBackend()
                adapter.start()
            self.connect_to_mac(adapter, i, readAllString)

            """Wait  until all reading is done. We can only read one sensor at the time"""
            while not self.reading_done:
                time.sleep(1)

        adapter.reset()
        recieved_data = self.data
        """Exit function if recieved data is empty"""
        if(len(self.data[0][0])==0):
            print("No data stored")
            return
        """Write data into csv file"""
        for i in range(0, len(recieved_data)):
            data = list(zip(recieved_data[i][0]))
            current_mac = recieved_data[i][1]
            for i in data:
                with open("acceleration-{}.csv".format(data[0][0][3]), 'a') as f:
                    f.write("{},{}".format(str(i[0])[1:-1], current_mac))
                    f.write("\n")
        return self.data

    """Error messages"""
    @staticmethod
    def ri_error_to_string(error):
        result = set()
        if error == 0:
            result.add("RD_SUCCESS")
        else:
            if error & (1 << 0):
                result.add("RD_ERROR_INTERNAL")
            if error & (1 << 1):
                result.add("RD_ERROR_NO_MEM")
            if error & (1 << 2):
                result.add("RD_ERROR_NOT_FOUND")
            if error & (1 << 3):
                result.add("RD_ERROR_NOT_SUPPORTED")
            if error & (1 << 4):
                result.add("RD_ERROR_INVALID_PARAM")
            if error & (1 << 5):
                result.add("RD_ERROR_INVALID_STATE")
            if error & (1 << 6):
                result.add("RD_ERROR_INVALID_LENGTH")
            if error & (1 << 7):
                result.add("RD_ERROR_INVALID_FLAGS")
            if error & (1 << 8):
                result.add("RD_ERROR_INVALID_DATA")
            if error & (1 << 9):
                result.add("RD_ERROR_DATA_SIZE")
            if error & (1 << 10):
                result.add("RD_ERROR_TIMEOUT")
            if error & (1 << 11):
                result.add("RD_ERROR_NULL")
            if error & (1 << 12):
                result.add("RD_ERROR_FORBIDDEN")
            if error & (1 << 13):
                result.add("RD_ERROR_INVALID_ADDR")
            if error & (1 << 14):
                result.add("RD_ERROR_BUSY")
            if error & (1 << 15):
                result.add("RD_ERROR_RESOURCES")
            if error & (1 << 16):
                result.add("RD_ERROR_NOT_IMPLEMENTED")
            if error & (1 << 16):
                result.add("RD_ERROR_SELFTEST")
            if error & (1 << 18):
                result.add("RD_STATUS_MORE_AVAILABLE")
            if error & (1 << 19):
                result.add("RD_ERROR_NOT_INITIALIZED")
            if error & (1 << 20):
                result.add("RD_ERROR_NOT_ACKNOWLEDGED")
            if error & (1 << 21):
                result.add("RD_ERROR_NOT_ENABLED")
            if error & (1 << 31):
                result.add("RD_ERROR_FATAL")
        return result

    """Find all mac addresses in range"""
    @staticmethod
    def find_tags_mac():
        mac_set = set()

        try:
            """We have to kill the search after 10 seconds or we search endless"""
            with timeout(10, exception=RuntimeError):
                while True:
                    tags = RuuviTagSensor._get_ruuvitag_datas(search_duratio_sec=3)
                    for tag in tags:
                        mac_set.add(tag[0])
                    return mac_set
        except RuntimeError:
            return mac_set
            pass
#region process data
    """Parse the received data"""
    def process_sensor_data_8(self, bytes, scale, rate):
        j = 0
        pos = 0
        koords = ["\nx", "y", "z"]
        x_vector = list()
        y_vector = list()
        z_vector = list()
        timestamp_list = list()
        time_between_samples = 1 / rate

        if (scale == 2):
            print("Scale: 2G")
            faktor = 16 / (256 * 1000)
        elif (scale == 4):
            print("Scale: 4G")
            faktor = 32 / (256 * 1000)
        elif (scale == 8):
            print("Scale: 8G")
            faktor = 64 / (256 * 1000)
        elif (scale == 16):
            print("Scale: 16G")
            faktor = 192 / (256 * 1000)

        while (pos < len(bytes)):
            """Read and store timestamp. This is little endian again"""
            t = bytes[pos:pos + 8]
            inv_t = t[::-1]
            timestamp = int(hexlify(inv_t), 16) / 1000
            #
            # dt = datetime.datetime.utcfromtimestamp(int(hexlify(inv_t), 16) / 1000).strftime('%Y-%m-%d %H:%M:%S.%f')
            # print(dt)
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

                print(timestamp)
                if j % 3 == 0:
                    x_vector.append(value)
                if j % 3 == 1:
                    y_vector.append(value)
                if j % 3 == 2:
                    z_vector.append(value)
                    timestamp += time_between_samples
                    print(datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f'))
                    timestamp_list.append(
                        datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f'))
                print("%d: %s = %f%s" % (j, koords[j % 3], value, "\n" if (j % 3 == 2) else ""))
                j += 1

        print("%d Werte entpackt" % (j,))
        print(len(x_vector))
        return x_vector, y_vector, z_vector, timestamp_list

    def process_sensor_data_10(self, bytes, scale, rate):
        j = 0
        pos = 0
        koords = ["\nx", "y", "z"]

        x_vector = list()
        y_vector = list()
        z_vector = list()
        timestamp_list = list()
        time_between_samples = 1 / rate

        if (scale == 2):
            print("Scale: 2G")
            faktor = 4 / (64 * 1000)
        elif (scale == 4):
            print("Scale: 4G")
            faktor = 8 / (64 * 1000)
        elif (scale == 8):
            print("Scale: 8G")
            faktor = 16 / (64 * 1000)
        elif (scale == 16):
            print("Scale: 16G")
            faktor = 48 / (64 * 1000)

        while (pos < len(bytes)):
            print("Timestamp: %s" % hexlify(bytes[pos + 7:pos:-1]))
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
                print("%d: %s = %f%s" % (j, koords[j % 3], value, "\n" if (j % 3 == 2) else ""))
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
                print("%d: %s = %f%s" % (j, koords[j % 3], value, "\n" if (j % 3 == 2) else ""))
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
                print("%d: %s = %f%s" % (j, koords[j % 3], value, "\n" if (j % 3 == 2) else ""))
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
                print("%d: %s = %f%s" % (j, koords[j % 3], value, "\n" if (j % 3 == 2) else ""))
                j += 1

        print("%d Werte entpackt" % (j,))
        print(len(x_vector))
        return x_vector, y_vector, z_vector, timestamp_list

    def process_sensor_data_12(self, bytes, scale, rate):
        j = 0
        pos = 0
        koords = ["x", "y", "z"]
        x_vector = list()
        y_vector = list()
        z_vector = list()
        timestamp_list = list()
        time_between_samples = 1 / rate

        if (scale == 2):
            print("Scale: 2G")
            faktor = 1 / (16 * 1000)
        elif (scale == 4):
            print("Scale: 4G")
            faktor = 2 / (16 * 1000)
        elif (scale == 8):
            print("Scale: 8G")
            faktor = 4 / (16 * 1000)
        elif (scale == 16):
            print("Scale: 16G")
            faktor = 12 / (16 * 1000)

        while (pos < len(bytes)):
            print("Timestamp: %s" % hexlify(bytes[pos + 7:pos:-1]))
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
                print("%d: %s = %f%s" % (j, koords[j % 3], value, "\n" if (j % 3 == 2) else ""))
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
                print("%d: %s = %f%s" % (j, koords[j % 3], value, "\n" if (j % 3 == 2) else ""))
                j += 1

        print("%d Werte entpackt" % (j,))
        return x_vector, y_vector, z_vector, timestamp_list
#endregion
    """"handle the received messages from manipulating the sensor state"""
    def handle_sensor_commands(self, handle, value):
        """
        handle -- integer, characteristic read handle the data was received on
        value -- bytearray, the data returned in the notification
        """
        print("handle sensor commands")
        if value[0] == 0xFB:
            if (value[1] == 0x00):
                print("Status: %s" % str(self.ri_error_to_string(value[2])))
            elif (value[1] == 0x07):
                print("Status: %s" % str(self.ri_error_to_string(value[2])))
                print("Received data: %s" % hexlify(value[3:]))
                print(value[3])
                print(type(value[3]))
                print("Samplerate:    %s Hz" % value[3])
                print("Resolution:    %s Bits" % (int(value[4])))
                print("Scale:         %xG" % value[5])
                print("DSP function:  %x" % value[6])
                print("DSP parameter: %x" % value[7])
                print("Mode:          %x" % value[8])
            elif (value[1] == 0x09):
                print("Status: %s" % str(self.ri_error_to_string(value[2])))
                # die Daten sind little-endian (niegrigwertigstes Bytes zuerst) gespeichert
                # die menschliche lesart erwartet aber big-endian (höchstwertstes Bytes zuerst)
                # deswegen Reihenfolge umdrehen
                print("Received data: %s" % hexlify(value[:-9:-1]))
                print(time.strftime('%D %H:%M:%S', time.gmtime(int(hexlify(value[:-9:-1]), 16) / 1000)))

            else:
                print("Antwort enthält falschen Typ")
        self.reading_done=True
    """"Connect to specific mac and send command string  to manipulate sensor state"""
    def connect_to_mac_command(self, command_string):
        global mac
        global adapter
        """Check if mac has values"""
        if mac is None:
            mac = self.find_tags_mac
            adapter = pygatt.GATTToolBackend()
            adapter.start()
        for i in mac:
            print(i)
            if adapter._running.is_set() is False:
                print("Need to start adapter")
                adapter = pygatt.GATTToolBackend()
                adapter.start()
            self.reading_done = False
            try:
                time.sleep(2)
                device = adapter.connect(i, address_type=pygatt.BLEAddressType.random)
            except Exception as e:
                print(e)
                print("Adapter stoppen")
                adapter.stop()
                continue
            print("Connection established")

            # Sending command to Tag
            device.char_write(uuid=uuIdWrite, value=bytearray.fromhex(command_string))
            # Handle received message
            device.subscribe(uuIdRead, callback=self.handle_sensor_commands)
            device.disconnect()
            while not self.reading_done:
                time.sleep(2)

    """"Connect to specific mac and send get request for logged acceleration"""
    def connect_to_mac(self, adapter, i, readCommand):
        try:
            print(adapter._running.is_set())

            print(i)
            device = adapter.connect(i, address_type=pygatt.BLEAddressType.random)
        except Exception as e:
            print(e)
            print(i)
            self.ConnectionError = True
            self.reading_done = True
            print(self.taskrun)
            print("No connection Available")
            adapter.stop()
            return None
        print("Connection established")

        # Sending command to Tag
        device.char_write(uuid=uuIdWrite, value=bytearray.fromhex(readCommand))

        # Storage for received data
        sensordaten = bytearray();
        #data = []
        """Handle received data"""
        def handle_data(handle, value):

            """
            handle -- integer, characteristic read handle the data was received on
            value -- bytearray, the data returned in the notification
            """

            if (value.startswith(b'\xfc')):
                # Daten
                sensordaten.extend(value[1:])
                print("Received data block: %s" % hexlify(value[1:]))
            # Marks end of data stream
            elif (value.startswith(b'\xfb')):
                # Status
                print("Status: %s" % str(self.ri_error_to_string(value[2])))

                crc = value[11:13];
                print("Received CRC: %s" % hexlify(crc))

                # CRC validation
                ourcrc = crcfun(sensordaten)
                print("Recalculated CRC: %x" % ourcrc)

                print("Received %d bytes" % len(sensordaten))
                print(hexlify(crc))
                if hexlify(crc) == bytearray():
                    print("No crc Received")
                    device.disconnect
                    self.reading_done = True
                    self.taskrun = False
                    adapter.reset()
                    return None

                if int(hexlify(crc), 16) != ourcrc:
                    print("CRC are unequal")
                    device.disconnect
                    self.reading_done = True
                    self.taskrun = False
                    adapter.reset()
                    return None
                #
                device.disconnect()


                self.taskrun = False                

                timeStamp = hexlify(sensordaten[7::-1])

                # Start data
                if (value[4] == 12):
                    # 12 Bit

                    AccelorationData = self.process_sensor_data_12(sensordaten, value[5], value[3])
                elif (value[4] == 10):
                    # 10 Bit

                    AccelorationData = self.process_sensor_data_10(sensordaten, value[5], value[3])
                elif (value[4] == 8):
                    # 8 Bit

                    AccelorationData = self.process_sensor_data_8(sensordaten, value[5], value[3])
                else:
                    print("Unknown Resolution")
                if AccelorationData != None:
                    self.data.append([list(map(list, zip(AccelorationData[0], AccelorationData[1], AccelorationData[2],
                                                         AccelorationData[3]))), i])
                    print(self.data)
                self.reading_done = True

        device.subscribe(uuIdRead, callback=handle_data)