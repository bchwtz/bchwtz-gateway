import asyncio
from binascii import hexlify
from datetime import datetime
from typing import Callable, Type
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
from gateway.drivers.bluetooth.ble_conn.ble_conn import BLEConn
from gateway.config import Config
import logging
from gateway.tag.tag_interface.decoder import Decoder
from bleak.backends.scanner import AdvertisementData
import aiopubsub
from paho.mqtt.client import Client, MQTTMessage
import json
from gateway.util.signal_last import signal_last


from gateway.sensor.sensor import Sensor
from gateway.tag.tag_interface.signals import SigScanner

class Tag(object):
    """ Shadow of a hardware tag. What is a tag compared to a sensor? A tag has different kinds of sensors, a microcontroller (NRF52) and additional hardware like the battery-holder etc. A sensor is simply one device on the tag, responsible of measuring something.
    """
    def __init__(self, name: str = "", address: str = "", device: BLEDevice = None, online: bool = True, pubsub_hub: aiopubsub.Hub = None, mqtt_client: Client = None) -> None:
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
        self.logger.setLevel(logging.INFO)
        self.configured: bool = False
        self.logging_active: bool = False
        formatter = logging.Formatter('[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s','%m-%d %H:%M:%S')
        streamHandler = logging.StreamHandler()
        streamHandler.setFormatter(formatter)
        self.logger.addHandler(streamHandler)
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
        self.acc_log_res_topic: str = Config.MQTTConfig.topic_tag_prefix.value + "/" + self.address + Config.MQTTConfig.topic_tag_cmd_get_acceleration_log_res.value
        self.acc_log_req_id: str = ""
        self.seen_in_last_iter: bool = False
        self.last_seen: float = time.time()
        self.pubsub_hub: aiopubsub.Hub = pubsub_hub
        self.publisher: aiopubsub.Publisher = aiopubsub.Publisher(self.pubsub_hub, prefix = aiopubsub.Key("TAG"))
        self.mqtt_client: Client = mqtt_client
        if self.mqtt_client is not None:
            self.subscribe_to_mqtt_chans()

    async def get_acceleration_log(self, cb: Callable[[int, bytearray], None] = None) -> None:
        # await self.ble_conn.disconnect()
        if cb is None:
            cb = self.acceleration_log_callback
        await self.activate_logging(cb)
        await self.get_acceleration_data(cb)

    async def activate_logging(self, cb: Callable[[int, bytearray], None] = None) -> None:
        # if self.activate_logging:
            # self.logger.warn("logging already active")
            # return
        if cb is None:
            cb = self.multi_communication_callback
        await self.ble_conn.run_single_ble_command(
            tag = self.ble_device,
            read_chan = Config.CommunicationChannels.rx.value,
            write_chan = Config.CommunicationChannels.tx.value,
            cmd = Config.Commands.activate_logging_at_tag.value,
            cb = cb
        )
        self.logging_active = True


    async def deactivate_logging(self, cb: Callable[[int, bytearray], None] = None) -> None:
        if cb is None:
            cb = self.multi_communication_callback
        await self.ble_conn.run_single_ble_command(
            tag = self.ble_device,
            read_chan = Config.CommunicationChannels.rx.value,
            write_chan = Config.CommunicationChannels.tx.value,
            cmd = Config.Commands.deactivate_logging_at_tag.value,
            cb = cb
        )
        self.logging_active = False

    async def activate_streaming_mode(self, cb: Callable[[int, bytearray], None] = None, retries: int = 5) -> None:
        if cb is None:
            cb = self.acceleration_stream_callback
        if not self.configured:
            if retries < 0:
                self.logger.error("failed activate_streaming_mode: maximum retries reached")
                return
            self.logger.warn("tag was not configured yet - sleeping 20 seconds and trying again")
            time.sleep(20)
            self.activate_streaming_mode(self, cb=cb, retries=retries-1)
        await self.ble_conn.run_single_ble_command(
            tag = self.ble_device,
            read_chan=Config.CommunicationChannels.rx.value,
            write_chan=Config.CommunicationChannels.tx.value,
            cmd=Config.Commands.activate_acc_streaming.value,
            cb=cb,
            await_response=False
        )
        self.logger.info("activated streaming!")
    
    async def deactivate_streaming_mode(self) -> None:
        self.ble_conn.stopEvent.set()
        await self.ble_conn.client.disconnect()

    async def get_acceleration_data(self, cb: Callable[[int, bytearray], None] = None) -> None:
        """ Will get the acceleration log_data of the sensors and store it inside their measurements
            Arguments:
                cb: A callback that is invoked, once the answer to this call is received (default: multi_comm_callback)
        """
        if cb is None:
            cb = self.acceleration_log_callback
        await self.ble_conn.run_single_ble_command(
            tag = self.ble_device,
            read_chan = Config.CommunicationChannels.rx.value,
            write_chan = Config.CommunicationChannels.tx.value,
            cmd = Config.Commands.get_acceleration_data.value,
            timeout = 60,
            cb = cb,
            await_response = False,
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
            cb = cb,
            await_response=True
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

    async def acceleration_log_callback(self, status_code: int, rx_bt: bytearray) -> None:
        caught_signals = None
        caught_signals = SigScanner.scan_signals(rx_bt, Config.ReturnSignalsLoggingMode)
        if caught_signals == None:
            self.logger.debug("no signal caught on: %s", hexlify(rx_bt))
            return
        if "logging_data" in caught_signals:
            await self.handle_logging_data_cb(rx_bt)
        elif "logging_data_end" in caught_signals:
            await self.handle_logging_data_end_cb(rx_bt)


    def acceleration_stream_callback(self, status_code: int, rx_bt: bytearray) -> None:
        """ Handles and decodes received streaming data
        """
        caught_signals = None
        rx_bt = rx_bt[1:]
        self.logger.warn(rx_bt)

        caught_signals = SigScanner.scan_signals(rx_bt, Config.ReturnSignalsLoggingMode)
        acc: AccelerationSensor = self.get_sensor_by_type(AccelerationSensor)
        if acc is None:
            self.logger.error("No accelerometer detected - cannot log acceleration data!")
            return
        if caught_signals == None:
            self.logger.warn("no signals detected!")
            return
        if "logging_data" in caught_signals:
            self.dec.decode_acc_stream_pack(rx_bt, config=self.config, acceleration_sensor=acc)
            self.logger.error(acc.get_measurement_props())

    def multi_communication_callback(self, status_code: int, rx_bt: bytearray) -> None:
        """ Handles a message and forwards it to the correct callback. This is needed so that if a call has multiple messages that will be received, the following message to the first received message won't be ignored.
            Arguments:
                status_code: unused status_code
                rx_bt: the bluetooth message as bytearray
        """
        caught_signals = None
        caught_signals = SigScanner.scan_signals(rx_bt, Config.ReturnSignals)
        self.logger.debug(str(hexlify(rx_bt)))
        self.logger.debug(caught_signals)
        if caught_signals == None:
            return
        if "config" in caught_signals:
            self.handle_config_cb(rx_bt)
        elif "time" in caught_signals:
            self.handle_time_cb(rx_bt)
        elif "heartbeat" in caught_signals:
            self.handle_heartbeat_cb(rx_bt)
        elif "logging_status" in caught_signals:
            self.handle_logging_status_cb(rx_bt)
        else:
            self.logger.warn("got non-implemented function callback")
        self.ble_conn.stopEvent.set()
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
        self.configured = True
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
        self.logger.debug("got time - sending...")
        self.publisher.publish(aiopubsub.Key("log", "TIME"), self)
        self.logger.debug(self.time)

    def handle_logging_status_cb(self, rx_bt: bytearray):
        """ Helper to be able to determine the logging status of a tag
        """
        self.logger.debug("logging status:")
        self.logger.debug(rx_bt)

    async def handle_logging_data_cb(self, rx_bt: bytearray):
        """ attaches all logging data into crc
        """
        self.logger.debug("logging data:")
        self.logger.debug(rx_bt)
        acc: AccelerationSensor = self.get_sensor_by_type(AccelerationSensor)
        if acc is None:
            self.logger.error("No accelerometer detected - cannot log acceleration data!")
            self.ble_conn.stopEvent.set()
            return
        self.dec.build_acc_log_crc(rx_bt = rx_bt, acceleration_sensor = acc)


    async def handle_logging_data_end_cb(self, rx_bt: bytearray):
        """ The end hook for acceleration logging - is called as soon as all data has been received
        """
        self.logger.debug("logging data:")
        self.logger.debug(hexlify(rx_bt))
        acc: AccelerationSensor = self.get_sensor_by_type(AccelerationSensor)
        if acc is None:
            self.logger.error("No accelerometer detected - cannot log acceleration data!")
            return
        self.dec.decode_acc_log_crc(rx_bt = rx_bt, acceleration_sensor = acc)
        self.publisher.publish(aiopubsub.Key("log"), self)
        if self.mqtt_client is None:
            return
        for is_last, measurement in signal_last(acc.measurements):
            self.mqtt_client.publish(self.acc_log_res_topic, json.dumps({"request_id": self.acc_log_req_id,"ongoing_request": not is_last, "payload": {"status": "success", "measurement": measurement.get_props()}}))
        # await self.deactivate_logging()
        # self.logging_active = False

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
            timeout = 20
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
    
    def get_sensor_by_type(self, T: Type) -> Sensor:
        """ Gets a sensor by its type, e.g. AccelerationSensor and returns it
            Arguments:
                T: type of the searched sensor
            Returns:
                either None or the sensor object
        """
        for sensor in self.sensors:
            if type(sensor) is T:
                return sensor
        return None

    def get_props(self) -> dict:
        """ Making the tag serializable.
            Returns:
                self as dict
        """
        return {'name': self.name, 'address': self.address, 'sensors': self.get_sensors_props(), 'time': self.time, 'config': self.config, 'online': self.online, 'last_seen': self.last_seen}

    async def handle_mqtt_cmd(self, mqtt_client: Client, command: str, msg: MQTTMessage, last_in_list: bool):
        """ Handles mqtt-cmds that were redirected from hub to this tag
        """
        msg_dct: dict = json.loads(msg.payload)
        payload = msg_dct["payload"]
        req_id = msg_dct["id"]

        if command == "get":
            self.logger.info("running get on tag: %s", self.address)
            msg_dct: dict = json.loads(msg.payload)
            atch = []
            for sensor in self.sensors:
                if sensor is None or len(sensor.measurements) < 1:
                    continue
                atch.append(Config.MQTTConfig.topic_tag_prefix.value + "/" + self.address + "/" + sensor.name + "/" + req_id)
            
            mqtt_client.publish(Config.MQTTConfig.topic_command_res.value, json.dumps({
                "attachment_channels": atch,
                "object_type": "tag",
                "has_attachments": len(atch) > 0,
                "ongoing_request": True,
                "request_id": req_id,
                "payload": {
                    "status": "success",
                    "tag": self
                    }
                },
                default=lambda o: o.get_props()
                if getattr(o, "get_props", None) is not None
                else None,
                skipkeys=True,
                check_circular=False,
                sort_keys=True, indent=4)
            )
            self.logger.debug("loading measurements")
            self.__return_paged_measurements(req_id=req_id)
            return

        if command == "get_time":
            self.logger.info("running get_time on tag: %s", self.address)
            await self.get_time()
            if self.mqtt_client is not None:
                self.mqtt_client.publish(Config.MQTTConfig.topic_command_res.value, json.dumps({"request_id": req_id, "ongoing_request": False, "payload": {"status": "success"}}, default=lambda o: o.get_props() if getattr(o, "get_props", None) is not None else None, skipkeys=True, check_circular=False, sort_keys=True, indent=4))

        elif command == "set_time":
            self.logger.info("running set_time on tag: %s", self.address)
            await self.set_time()
            if self.mqtt_client is not None:
                self.mqtt_client.publish(Config.MQTTConfig.topic_command_res.value, json.dumps({"request_id": req_id, "ongoing_request": False, "payload": {"status": "success"}}, default=lambda o: o.get_props() if getattr(o, "get_props", None) is not None else None, skipkeys=True, check_circular=False, sort_keys=True, indent=4))


        elif command == "get_config":
            self.logger.info("running get_config on tag: %s", self.address)
            await self.get_config()
            if self.mqtt_client is not None:
                self.mqtt_client.publish(Config.MQTTConfig.topic_command_res.value, json.dumps({"request_id": req_id, "ongoing_request": False, "payload": {"old_config": self.config}}, default=lambda o: o.get_props() if getattr(o, "get_props", None) is not None else None, skipkeys=True, check_circular=False, sort_keys=True, indent=4))

        elif command == "set_heartbeat":
            self.logger.info("running set_heartbeat on tag: %s", self.address)
            await self.set_heartbeat(payload)
            if self.mqtt_client is not None:
                self.mqtt_client.publish(Config.MQTTConfig.topic_command_res.value, json.dumps({"request_id": req_id, "ongoing_request": False, "payload": {"status": "setting heartbeat"}}, default=lambda o: o.get_props() if getattr(o, "get_props", None) is not None else None, skipkeys=True, check_circular=False, sort_keys=True, indent=4))

        elif command == "set_config":
            self.logger.info("running set_config on tag: %s", self.address)
            resolution = payload.get("resolution", None)
            samplerate = payload.get("samplerate", None)
            scale = payload.get("scale", None)
            divider = payload.get("divider", None)
            dsp_function = payload.get("dsp_function", None)
            dsp_parameter = payload.get("dsp_parameter", None)
            mode = payload.get("mode", None)
            if resolution is not None:
                self.config.set_resolution(resolution)
            if scale is not None:
                self.config.set_scale(scale)
            if samplerate is not None:
                self.config.set_samplerate(samplerate)
            if divider is not None:
                self.config.set_divider(divider)
            if dsp_function is not None:
                self.config.set_dsp_function(dsp_function)
            if dsp_parameter is not None:
                self.config.set_dsp_parameter(dsp_parameter)
            if mode is not None:
                self.config.set_mode(mode)
            await self.set_config()
            await self.get_config()
            if self.mqtt_client is not None:
                self.mqtt_client.publish(Config.MQTTConfig.topic_command_res.value, json.dumps({"request_id": req_id, "ongoing_request": False, "payload": {"requested_config": self.config}}, default=lambda o: o.get_props() if getattr(o, "get_props", None) is not None else None, skipkeys=True, check_circular=False, sort_keys=True, indent=4))


        elif command == "get_acceleration_log":
            self.acc_log_req_id = req_id
            if self.mqtt_client is not None:
                self.mqtt_client.publish(Config.MQTTConfig.topic_command_res.value, json.dumps({"has_attachments": True, "attachment_channels": [self.acc_log_res_topic], "request_id": req_id, "ongoing_request": True, "payload": {"status": "started - wait for the results and fetch them via tags get!"}}, default=lambda o: o.get_props() if getattr(o, "get_props", None) is not None else None, skipkeys=True, check_circular=False, sort_keys=True, indent=4))
            await self.get_acceleration_log()


        # TODO: add deactivate_logging
        elif command == "deactivate_logging":
            await self.deactivate_logging()
            if self.mqtt_client is not None:
                self.mqtt_client.publish(Config.MQTTConfig.topic_command_res.value, json.dumps({"request_id": req_id, "ongoing_request": False, "payload": {"status": "deactivated logging!"}}, default=lambda o: o.get_props() if getattr(o, "get_props", None) is not None else None, skipkeys=True, check_circular=False, sort_keys=True, indent=4))

        # TODO: add streaming_data


    def subscribe_to_mqtt_chans(self):
        """ Connect callback for mqtt.
        """
        self.logger.info("connected to mqtt")
        pre = Config.MQTTConfig.topic_tag_prefix.value
        ownprefix = pre + "/" + self.address + "/commands/"
        commands = Config.MQTTConfig.tag_commands.value
        for cmd in commands:
            sub = ownprefix + cmd
            if self.mqtt_client is not None:
                self.mqtt_client.subscribe(sub, 0)
            self.logger.info(sub)

    def __return_paged_measurements(self, req_id: int):
        for sensor in self.sensors:
            measurements = []
            for idx, measurement in enumerate(sensor.measurements):
                measurements.append(measurement)
                if idx % 10 == 0 or len(sensor.measurements) - idx < 10:
                    if self.mqtt_client is not None:
                        self.mqtt_client.publish(
                            Config.MQTTConfig.topic_tag_prefix.value + "/" + self.address + "/" + sensor.name + "/" + req_id,
                            payload=json.dumps({
                                "obj_type": "measurement",
                                "ongoing_request": True,
                                "request_id": req_id,
                                "payload": {
                                    "status": "success",
                                    "tag_address": self.address,
                                    "measurement": measurements
                            }}, default=lambda o: o.get_props() if getattr(o, "get_props", None) is not None else None, skipkeys=True, check_circular=False, sort_keys=True, indent=4), retain=True)
                    measurements = []
            # print("sending success on {}", Config.MQTTConfig.topic_tag_prefix.value + "/" + self.address + "/" + sensor.name + "/" + req_id)
            # self.mqtt_client.publish(Config.MQTTConfig.topic_tag_prefix.value + "/" + self.address + "/" + sensor.name + "/" + req_id, payload=json.dumps({"ongoing_request": False, "payload": {"status": "success"}}), retain=True)

        # self.mqtt_client.
        # self.mqtt_client.publish(Config.MQTTConfig.topic_command_res.value, json.dumps({"obj_type": "empty", "ongoing_request": False, "request_id": req_id, "payload": {"status": "success"}}, default=lambda o: o.get_props() if getattr(o, "get_props", None) is not None else None, skipkeys=True, check_circular=False, sort_keys=True, indent=4))

