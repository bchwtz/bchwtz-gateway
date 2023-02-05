from enum import Enum
from os import environ
from types import MappingProxyType
from dotenv import load_dotenv

class Config:
    """ This class represents the global config of the gateway-library. Parts of this config can be overwritten by environment variables.
    """

    def load_from_environ():
        """ Loads Config.MQTTConfig and Config.MQTT.GlobalConfig parameters from environmentfile or system environment if the keys are specified in uppercase.
        """
        load_dotenv()
        for prop in Config.MQTTConfig:
            Config.load_key_from_environ(prop)

        for prop in Config.GlobalConfig:
            Config.load_key_from_environ(prop)

    def load_key_from_environ(prop: Enum):
        """ Helper to identify and load a key form environment variables.
            Arguments:
                prop: The property of the Enum to search for.
        """
        key = prop.name.upper()

        if environ.get(key) is not None:
            prop._value_ = environ.get(key)

    class Commands(Enum):
        """ All commandstrings of a tag are specified here (default is for ruuvi tags). If you have specified own commands or added new ones, please add them here.
        """
        read_all: str = "4a4a110100000000000000"
        activate_logging_at_tag: str = "4a4a080100000000000000"
        deactivate_logging_at_tag: str = "4a4a080000000000000000"
        get_acceleration_data: str = "4a4a110100000000000000"
        set_tag_config_substr: str = "4a4a02"
        get_tag_config: str = "4a4a030000000000000000"
        get_tag_timestamp: str = "2121090000000000000000"
        set_tag_time_substr: str = "212108"
        get_flash_statistics: str = "FAFA0d0000000000000000"
        get_logging_status: str = "4A4A090000000000000000"
        activate_acc_streaming: str = "4a4a080200000000000000"
        get_heartbeat_config: str = "2200F30000000000000000"
        set_heartbeat_substr: str = "2200F2"

    class CommunicationChannels(Enum):
        """ All communication channels of a tag are specified here.
        """
        srv: str = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
        tx: str = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
        rx: str = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"
        advertisements_rx: str = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
        dfu_control_pt: str = "8EC90001-F315-4F60-9FB8-838830DAEA50"
        dfu_data_pt: str = "8EC90002-F315-4F60-9FB8-838830DAEA50"
    
    class GlobalConfig(Enum):
        """ GlobalConfig has the most important and generic config parameters for a tag and the gateway.
        """
        bluetooth_manufacturer_id: int = 1177
        forced_time_sync: bool = True
        mqtt_broker: str = "localhost"
        mqtt_user: str = "mqtt"
        mqtt_password: str = "6p449xLrC5PH3pfbkMvj/XBQt443Kg6S"
        mqtt_client_id: str = "gateway_client"

    class MQTTConfig(Enum):
        """ Specific MQTT-parameters. Please override these values using your own in an environment variable.
        """
        topic_command: str = "1"
        topic_command_res: str = "2"
        topic_log: str = "3"
        topic_listen_adv: str = "4"
        topic_tag_prefix: str = "gateway/tag/"
        topic_tag_cmd_get_acceleration_log_res: str = "/acceleration_log_res"
        tag_commands: list[str] = [
            "get_config",
            "get",
            "set_config",
            "get_time",
            "set_time",
            "get_acceleration_log",
            "set_heartbeat",
            "deactivate_logging"
        ]
        hub_commands: list[str] = [
            "get_all",
        ]

    class AllowedValues(Enum):
        """ Has allowed values for specific commandstrings. The gateway will check for non-allowed values automatically.
        """
        samplerate: list[int] = [
            1,
            10,
            25,
            50,
            100,
            200,
            400
        ]
        sample_resolution: list[int] = [
            8,
            10,
            12
        ]
        scale: list[int] = [
            2,
            4,
            8,
            16
        ]

    class ReturnSignals(Enum):
        """ These are configs for the sigscanner-class from drivers. Keys are the required offset in the bytearray, values are the values required at the offsets to get a match. Don't change this, if you are not certain what you are doing! This might lead to completely missinterpreted values from your tag.
        """
        config: list[dict] = [{0: 0x4a, 3: 0x00}]
        status: list[dict] = [{0: 0x22, 2: 0xF2}]
        heartbeat: list[dict] = [{0: 0x22, 2: 0xF3}]
        time: list[dict] = [{0: 0x21, 2: 0x09}, {0: 0x4A, 2: 0x09}]
        logging_status: list[dict] = [{0: 0xFB, 1: 0x0D}]
    class ReturnSignalsLoggingMode(Enum):
        """ These are configs for the sigscanner-class from drivers. Keys are the required offset in the bytearray, values are the values required at the offsets to get a match. Don't change this, if you are not certain what you are doing! This might lead to completely missinterpreted values from your tag.
        """
        logging_data: list[dict] = [{0: 0x11}]
        # stream_data: list[dict] = [{1: 0x11}]
        logging_data_end: list[dict] = [{0: 0x4a, 1: 0x4a, 2: 0x11, 3: 0x00}]
