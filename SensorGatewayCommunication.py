from ruuvitag_sensor.ruuvi import RuuviTagSensor, RunFlag
import time
from interruptingcow import timeout
import pygatt
import logging
import crcmod
from binascii import hexlify

logging.basicConfig()
logging.getLogger('pygatt').setLevel(logging.INFO)

macSet = set()
macList = []
readAllString = "FAFA030000000000000000"
uuIdWrite = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
uuIdRead = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"
waitTime = 1
crcfun = crcmod.mkCrcFun(0x11021, rev=False, initCrc=0xffff, xorOut=0)
test = RuuviTagSensor._get_ruuvitag_datas(search_duratio_sec=2)
cnt = 0


class RuuviTagAccelerometerCommunication:
    def __init__(self):
        global mac
        global adapter
        print("ini start")
        mac = self.find_tags_mac()
        adapter = pygatt.GATTToolBackend()
        adapter.start()
        print("ini done")

    '''
    Activate ringbuffer.
    '''

    def activate_logging_at_sensor(self):
        global mac
        global adapter
        command_string = "FAFA0a0100000000000000"
        # print("Activate")
        # print(mac)
        if mac is None:
            mac = self.find_tags_mac
            adapter = pygatt.GATTToolBackend()
            adapter.start()
        if adapter is None:
            adapter = pygatt.GATTToolBackend()
            adapter.start()

        for i in mac:
            self.connect_to_mac_command(adapter, i, command_string)
        adapter.stop()
        adapter.kill()

    '''
    Delete ringbuffer.
    '''

    def deactivate_logging_at_sensor(self):
        global mac
        global adapter

        command_string = "FAFA0a0000000000000000"
        if mac is None:
            mac = self.find_tags_mac
            adapter = pygatt.GATTToolBackend()
            adapter.start()
        print(type(adapter))
        if adapter is None:
            adapter = pygatt.GATTToolBackend()
            adapter.start()
        for i in mac:
            self.connect_to_mac_command(adapter, i, command_string)
        adapter.stop()
        adapter.kill()

    def get_config_from_sensor(self):
        global mac
        global adapter

        command_string = "FAFA070000000000000000"
        if mac is None:
            mac = self.find_tags_mac
            adapter = pygatt.GATTToolBackend()
            adapter.start()
        print(type(adapter))
        if adapter is None:
            print("no Adapter")
            adapter = pygatt.GATTToolBackend()
            adapter.start()
        for i in mac:
            self.connect_to_mac_command(adapter, i, command_string)
        adapter.stop()

    def get_time_from_sensor(self):
        global mac
        global adapter

        command_string = "FAFA090000000000000000"
        if mac is None:
            mac = self.find_tags_mac
            adapter = pygatt.GATTToolBackend()
            adapter.start()
        print(type(adapter))
        if adapter is None:
            adapter = pygatt.GATTToolBackend()
            adapter.start()
        for i in mac:
            self.connect_to_mac_command(adapter, i, command_string)
        adapter.stop()

    def get_acceleration_data(self):
        global mac
        global adapter
        global readAllString

        readAllString = "FAFA030000000000000000"

        for i in mac:
            self.connect_to_mac(adapter, i, readAllString)
        print("Taskrun")
        self.taskrun = True
        # print("Taskrun true")
        while self.taskrun:
            time.sleep(1)
            print("Waitdone")

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

    @staticmethod
    def find_tags_mac():
        mac_set = set()

        try:
            with timeout(10, exception=RuntimeError):
                while True:
                    tags = RuuviTagSensor._get_ruuvitag_datas(search_duratio_sec=3)
                    for tag in tags:
                        mac_set.add(tag[0])

                    print("Out")
                    return mac_set
        except RuntimeError:
            print("Out")
            return mac_set
            pass

    @staticmethod
    def process_sensor_data(bytes, scale):
        j = 0;
        koords = ["\nx", "y", "z"]

        if scale == 2:
            print("Scale: 2G")
            faktor = 4 / (64 * 1000)
        elif scale == 4:
            print("Scale: 4G")
            faktor = 8 / (64 * 1000)
        elif scale == 8:
            print("Scale: 8G")
            faktor = 16 / (64 * 1000)
        elif scale == 16:
            print("Scale: 16G")
            faktor = 48 / (64 * 1000)

        for i in range(int(len(bytes) / 5)):
            value = bytes[i * 5] & 0xc0
            value |= (bytes[i * 5] & 0x3f) << 10
            value |= (bytes[1 + i * 5] & 0xc0) << 2
            if value & 0x8000 == 0x8000:
                # negative Zahl
                # 16Bit Zweierkomplement zurückrechnen
                value = value ^ 0xffff
                value += 1
                # negieren
                value = -value
            value *= faktor
            print("%s = %f" % (koords[j % 3], value))
            j += 1
            value = (bytes[1 + i * 5] & 0x30) << 2
            value |= (bytes[1 + i * 5] & 0x0f) << 12
            value |= (bytes[2 + i * 5] & 0xf0) << 4
            if value & 0x8000 == 0x8000:
                # negative Zahl
                # 16Bit Zweierkomplement zurückrechnen
                value = value ^ 0xffff
                value += 1
                # negieren
                value = -value
            value *= faktor
            print("%s = %f" % (koords[j % 3], value))
            j += 1
            value = (bytes[2 + i * 5] & 0x0c) << 4
            value |= (bytes[2 + i * 5] & 0x03) << 14
            value |= (bytes[3 + i * 5] & 0xfc) << 6
            if value & 0x8000 == 0x8000:
                # negative Zahl
                # 16Bit Zweierkomplement zurückrechnen
                value = value ^ 0xffff
                value += 1
                # negieren
                value = -value
            value *= faktor
            print("%s = %f" % (koords[j % 3], value))
            j += 1
            value = (bytes[3 + i * 5] & 0x03) << 6
            value |= (bytes[4 + i * 5]) << 8
            if value & 0x8000 == 0x8000:
                # negative Zahl
                # 16Bit Zweierkomplement zurückrechnen
                value = value ^ 0xffff
                value += 1
                # negieren
                value = -value
            value *= faktor
            print("%s = %f" % (koords[j % 3], value))
            j += 1
        print("\n%d Werte entpackt" % (j,))

    def handle_sensor_commands(self, handle, value):
        """
        handle -- integer, characteristic read handle the data was received on
        value -- bytearray, the data returned in the notification
        """
        print("handle sensor commands")
        if (value[1] == 0x00):
            print("Status: %s" % str(self.ri_error_to_string(value[2])))
        if (value[1] == 0x07):
            print("Status: %s" % str(self.ri_error_to_string(value[2])))
            print("Received data: %s" % hexlify(value[3:]))
            print("Samplerate:    %x" % value[3])
            print("Resolution:    %x" % value[4])
            print("Scale:         %x" % value[5])
            print("DSP function:  %x" % value[6])
            print("DSP parameter: %x" % value[7])
            print("Mode:          %x" % value[8])
        if (value[1] == 0x09):
            print("Status: %s" % str(self.ri_error_to_string(value[2])))
            # die Daten sind little-endian (niegrigwertigstes Bytes zuerst) gespeichert
            # die menschliche lesart erwartet aber big-endian (höchstwertstes Bytes zuerst)
            # deswegen Reihenfolge umdrehen
            print("Received data: %s" % hexlify(value[:-9:-1]))
        else:
            print("Antwort enthält falschen Typ")

    def connect_to_mac_command(self, adapter, i, commandString):
        print(adapter)
        print(type(adapter))
        print(pygatt.BLEAddressType.random)
        try:
            device = adapter.connect(i, address_type=pygatt.BLEAddressType.random)
        except Exception as e:
            print(e)
        print("Connection established")

        # Sending command to Tag
        device.char_write(uuid=uuIdWrite, value=bytearray.fromhex(commandString))
        # Handle received message
        device.subscribe(uuIdRead, callback=self.handle_sensor_commands)

        device.disconnect()

    def connect_to_mac(self, adapter, i, readCommand):

        device = adapter.connect(i, address_type=pygatt.BLEAddressType.random)
        print("Connection established")

        # Sending command to Tag
        device.char_write(uuid=uuIdWrite, value=bytearray.fromhex(readCommand))

        # Storage for received data
        sensordaten = bytearray();

        def handle_data(handle, value):
            """
            handle -- integer, characteristic read handle the data was received on
            value -- bytearray, the data returned in the notification
            """

            # Daten
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

                #
                device.disconnect()

                self.taskrun = False

                # Der Timestamp ist little-endian (niegrigwertigstes Bytes zuerst) gespeichert
                # die menschliche Lesart erwartet aber big-endian (höchstwertigstes Bytes zuerst)
                # deswegen Reihenfolge umdrehen
                print("Timestamp: %s" % hexlify(sensordaten[7::-1]))

                # Start data
                if (value[4] == 12):
                    # 12 Bit
                    print("12 Bit Resolution")
                elif (value[4] == 10):
                    # 10 Bit
                    print("10 Bit Resolution")
                    self.process_sensor_data(sensordaten[8:], value[5])
                elif (value[4] == 8):
                    # 8 Bit
                    print("8 Bit Resolution")
                else:
                    print("unbekannte Resolution")

        device.subscribe(uuIdRead, callback=handle_data)
