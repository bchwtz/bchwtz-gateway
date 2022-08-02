from enum import Enum

class Config:
    class Commands(Enum):
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

    class CommunicationChannels(Enum):
        srv: str = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
        tx: str = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
        rx: str = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"
        advertisements_rx: str = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
        dfu_control_pt: str = "8EC90001-F315-4F60-9FB8-838830DAEA50"
        dfu_data_pt: str = "8EC90002-F315-4F60-9FB8-838830DAEA50"
    
    class GlobalConfig(Enum):
        bluetooth_manufacturer_id: int = 1177

    class ReturnSignals(Enum):
        # These are configs for the sigscanner-class from drivers. Keys are the required offset in the bytearray, values are the values required at the offsets to get a match.
        samplerate: list[dict] = [{0: 0x4a, 3: 0x00}]
        status: list[dict] = [{0: 0x22, 2: 0xF2}]
        heartbeat: list[dict] = [{0: 0x22, 2: 0xF3}]
        time: list[dict] = [{0: 0x21, 2: 0x09}, {0: 0x4A, 2: 0x09}]
