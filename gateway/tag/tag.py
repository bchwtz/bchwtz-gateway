import asyncio
from datetime import datetime
from typing import Callable
import time
from typing_extensions import Self
from xmlrpc.client import DateTime
from bleak.backends.device import BLEDevice
from gateway.sensor.acceleration import AccelerationSensor
from gateway.sensor.barometer import BarometerSensor
from gateway.sensor.temperature import TemperatureSensor
from gateway.sensor.humidity import HumiditySensor
from gateway.sensor.battery import BatterySensor
from gateway.tag.tag_interface.encoder import Encoder
from gateway.tag.tagconfig import TagConfig
from nbformat import write
from numpy import byte
from gateway.drivers.bluetooth.ble_conn.ble_conn import BLEConn
from gateway.config import Config
import logging
from gateway.tag.tag_interface.decoder import Decoder
from bleak.backends.scanner import AdvertisementData
import aiopubsub

from gateway.sensor.sensor import Sensor
from gateway.tag.tag_interface.signals import SigScanner
import mongox


client = mongox.Client("mongodb://localhost:27017", get_event_loop=asyncio.get_running_loop)
db = client.get_database("gateway")
class Tag(object):
    """ Shadow of a hardware tag. What is a tag compared to a sensor? A tag has different kinds of sensors, a microcontroller (NRF52) and additional hardware like the battery-holder etc. A sensor is simply one device on the tag, responsible of measuring something.
    """
    def __init__(self, name: str = "", address: str = "", device: BLEDevice = None, online: bool = True, pubsub_hub: aiopubsub.Hub = None) -> None:
        """ Initializes a new tag.
            Arguments:
                name: the bluetooth-name of the tag
                address: the mac-address of the tag
                device: the bleak-device (bleak is a ble-library that helps us to wrap bluez - this is the linux ble daemon)
                online: is the device online at the moment (in reach of this gateway)
                pubsub_hub: some gateway-internal pubsub-communication for events
        """
        self.name: str = name
        self.address: str = address
        self.ble_device: BLEDevice = device
        self.ble_conn: BLEConn = BLEConn()
        self.logger = logging.getLogger("Tag")
        self.logger.setLevel(logging.ERROR)
        # TODO: add sensors as ble caps on firmware side to autoload sensor classes by names
        self.sensors: list[Sensor] = [
            AccelerationSensor(),
            BarometerSensor(),
            TemperatureSensor(),
            HumiditySensor(),
            BatterySensor(),
        ]
        self.dec: Decoder = Decoder()
        self.enc: Encoder = Encoder()
        self.config: TagConfig = None
        self.heartbeat: int = 0
        self.time: float = 0.0
        self.online: bool = online
        self.last_seen: float = time.time()
        self.pubsub_hub: aiopubsub.Hub = pubsub_hub
        self.publisher: aiopubsub.Publisher = aiopubsub.Publisher(self.pubsub_hub, prefix = aiopubsub.Key("TAG"))

    async def get_acceleration_log(self, cb: Callable[[int, bytearray], None] = None) -> None:
        """ Will get the acceleration log_data of the sensors and store it inside their measurements
            Arguments:
                cb: A callback that is invoked, once the answer to this call is received (default: multi_comm_callback)
        """
        if cb is None:
            cb = self.default_log_callback
        await self.ble_conn.run_single_ble_command(
            tag = self.ble_device,
            read_chan = Config.CommunicationChannels.rx.value,
            write_chan = Config.CommunicationChannels.tx.value,
            cmd = Config.Commands.get_acceleration_data.value,
            cb = cb
        )

    async def get_config(self, cb: Callable[[int, bytearray], None] = None) -> None:
        """ Gets the tags current config and writes it to the shadow.
            Arguments:
                cb: A callback that is invoked, once the answer to this call is received (default: multi_communication_callback)
        """
        if cb is None:
            cb = self.multi_communication_callback
        await self.ble_conn.run_single_ble_command(
            tag = self.ble_device,
            read_chan = Config.CommunicationChannels.rx.value,
            write_chan = Config.CommunicationChannels.tx.value,
            cmd = Config.Commands.get_tag_config.value,
            cb = cb
        )

    async def get_time(self, cb: Callable[[int, bytearray], None] = None) -> None:
        """ Gets the tags current time and writes it to the shadow.
            Arguments:
                cb: A callback that is invoked, once the answer to this call is received (default: multi_communication_callback)
        """
        if cb is None:
            cb = self.multi_communication_callback
        await self.ble_conn.run_single_ble_command(
            tag = self.ble_device,
            read_chan = Config.CommunicationChannels.rx.value,
            write_chan = Config.CommunicationChannels.tx.value,
            cmd = Config.Commands.get_tag_timestamp.value,
            cb = cb,
            timeout=30
        )

    async def get_flash_statistics(self, cb: Callable[[int, bytearray], None] = None) -> None:
        """ Gets the tags current flash_statistics and prints them.
            Arguments:
                cb: A callback that is invoked, once the answer to this call is received (default: default_log_callback)
        """
        if cb is None:
            cb = self.default_log_callback
        await self.ble_conn.run_single_ble_command(
            tag = self.ble_device,
            read_chan = Config.CommunicationChannels.rx.value,
            write_chan = Config.CommunicationChannels.tx.value,
            cmd = Config.Commands.get_flash_statistics.value,
            cb = cb
        )

    async def get_logging_status(self, cb: Callable[[int, bytearray], None] = None) -> None:
        """ Gets the tags current logging status and prints it.
            Arguments:
                cb: A callback that is invoked, once the answer to this call is received (default: default_log_callback)
        """
        if cb is None:
            cb = self.default_log_callback
        await self.ble_conn.run_single_ble_command(
            tag = self.ble_device,
            read_chan = Config.CommunicationChannels.rx.value,
            write_chan = Config.CommunicationChannels.tx.value,
            cmd = Config.Commands.get_logging_status.value,
            cb = cb
        )

    def test_pub(self):
        self.publisher.publish(aiopubsub.Key("command"), self)

    def default_log_callback(self, status_code: int, rx_bt: bytearray) -> None:
        """ Logs rx_bt as a message
            Arguments:
                status_code: unused status_code
                rx_bt: the bluetooth message as bytearray
        """
        res = self.dec.decode_ruuvi_msg(rx_bt)
        self.logger.info(f"status {status_code}")
        self.logger.info(f"msg: {res}")

    def multi_communication_callback(self, status_code: int, rx_bt: bytearray) -> None:
        """ Handles a message and forwards it to the correct callback. This is needed so that if a call has multiple messages that will be received, the following message to the first received message won't be ignored.
            Arguments:
                status_code: unused status_code
                rx_bt: the bluetooth message as bytearray
        """
        caught_signals = None
        caught_signals = SigScanner.scan_signals(rx_bt, Config.ReturnSignals)
        self.logger.debug(caught_signals)
        if caught_signals == None:
            return
        if "config" in caught_signals:
            self.handle_config_cb(rx_bt)
        elif "time" in caught_signals:
            self.handle_time_cb(rx_bt)
        elif "heartbeat" in caught_signals:
            self.handle_heartbeat_cb(rx_bt)
        
        self.publisher.publish(aiopubsub.Key("log"), self)

    async def get_heartbeat(self, max_retries: int = 5) -> None:
        """ Gets the tags current heartbeat
            Arguments:
                max_retries: Specifies how often the call should be retried before failure
        """
        cmd = Config.Commands.get_heartbeat_config.value
        await self.ble_conn.run_single_ble_command(
            tag = self.ble_device,
            cmd = cmd,
            read_chan = Config.CommunicationChannels.rx.value,
            write_chan = Config.CommunicationChannels.tx.value,
            cb = self.multi_communication_callback,
            max_retries=max_retries
        )

    def handle_config_cb(self, rx_bt: bytearray) -> None:
        """ Handles the result of get_config.
            Arguments:
                rx_bt: The ble-message as bytearray.
        """
        self.config = self.dec.decode_config_rx(rx_bt)
        self.publisher.publish(aiopubsub.Key("log", "CONFIG"), self)

    def handle_heartbeat_cb(self, rx_bt: bytearray) -> None:
        """ Handles the result of get_heartbeat
            Arguments:
                rx_bt: The ble-message as bytearray.
        """
        self.heartbeat = self.dec.decode_heartbeat_rx(rx_bt)
        self.publisher.publish(aiopubsub.Key("log", "HEARTBEAT"), self)
    
    def handle_time_cb(self, rx_bt: bytearray) -> None:
        """ Handles the result of get_time
            Arguments:
                rx_bt: The ble-message as bytearray.
        """
        time = self.dec.decode_time_rx(rx_bt)
        self.time = time
        print("got time - sending...")
        self.publisher.publish(aiopubsub.Key("log", "TIME"), self)
        print(self.time)

    async def set_time(self, custom_time: float = 0.0, cb: Callable[[int, bytearray], None] = None) -> None:
        """ Sets the time of the tag to a specified time or the current time of the gateway (default).
            Arguments:
                custom_time: A custom timestamp to set the tags time to
                cb: Callback that is invoked as soon as this call is answered by the tag
        """
        if cb is None:
            cb = self.multi_communication_callback
        if custom_time == 0.0:
            custom_time = datetime.now().timestamp()
        cmd = self.enc.encode_time(time = custom_time)
        self.logger.debug(cmd)
        await self.ble_conn.run_single_ble_command(
            tag = self.ble_device,
            read_chan = Config.CommunicationChannels.rx.value,
            write_chan = Config.CommunicationChannels.tx.value,
            cmd = cmd,
            cb = cb,
            timeout=30
        )

    # TODO : move to enc
    async def set_heartbeat(self, interval: int = 10):
        """ Sets the current heartbeat of the tag.
            Arguments:
                interval: the new interval that should be used.
        """
        self.logger.info("Set heartbeat interval to: {}".format(interval))
        cmd = self.enc.encode_heartbeat(interval=interval)
        await self.ble_conn.run_single_ble_command(
            tag = self.ble_device,
            read_chan = Config.CommunicationChannels.rx.value,
            write_chan = Config.CommunicationChannels.tx.value,
            cmd = cmd,
            cb = self.multi_communication_callback
        )

    async def set_config(self, config: TagConfig = None):
        """ Sets the current config of the shadow onto the tag. Please change the config first, then invoke this method of the tag.
        """
        if config is not None:
            self.config = config
        cmd = self.enc.encode_config(config = self.config)
        await self.ble_conn.run_single_ble_command(
            tag = self.ble_device,
            read_chan = Config.CommunicationChannels.rx.value,
            write_chan = Config.CommunicationChannels.tx.value,
            cmd = cmd,
            cb = self.multi_communication_callback
        )

    def read_sensor_data(self, data: AdvertisementData = None):
        """ Calls the read_data_from_advertisement on all its sensors.
            Arguments:
                data: AdvertisementData as a dict
        """
        if data is None:
            return
        tag_data = self.dec.decode_advertisement(data)
        for sensor in self.sensors:
            sensor.read_data_from_advertisement(tag_data)

    def get_sensors_props(self) -> list[dict]:
        """ Making the object's sensors serializable.
            Returns:
                all sensor properties as a list of dicts
        """
        sensors = [dict]
        for s in self.sensors:
            sensors.append(s.get_props())
        return sensors

    def get_props(self) -> dict:
        """ Making the tag serializable.
            Returns:
                self as dict
        """
        return {'name': self.name, 'address': self.address, 'sensors': self.get_sensors_props(), 'time': self.time, 'config': self.config, 'online': self.online, 'last_seen': self.last_seen}