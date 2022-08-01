class Config:
    def __init__(self) -> None:
        self.commands = Config.Commands()
        self.channels = Config.CommunicationChannels()
        self.global_config = Config.GlobalConfig()

    class Commands:
        def __init__(self) -> None:
            self.read_all: str = "4a4a110100000000000000"
            self.activate_logging_at_tag: str = "4a4a080100000000000000"
            self.deactivate_logging_at_tag: str = "4a4a080000000000000000"
            self.get_acceleration_data: str = "4a4a110100000000000000"
            self.set_tag_config_substr: str = "4a4a02"
            self.get_tag_config: str = "4a4a030000000000000000"
            self.get_tag_timestamp: str = "2121090000000000000000"
            self.set_tag_time_substr: str = "212108"
            self.get_flash_statistics: str = "FAFA0d0000000000000000"
            self.get_logging_status: str = "4A4A090000000000000000"
            self.activate_acc_streaming: str = "4a4a080200000000000000"
            self.get_heartbeat_config: str = "2200F30000000000000000"

    class CommunicationChannels:
        def __init__(self) -> None:
            self.srv = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
            self.tx = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
            self.rx = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"
            self.advertisements_rx = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
            self.dfu_control_pt = "8EC90001-F315-4F60-9FB8-838830DAEA50"
            self.dfu_data_pt = "8EC90002-F315-4F60-9FB8-838830DAEA50"
    
    class GlobalConfig:
        def __init__(self) -> None:
            self.bluetooth_manufacturer_id = 1177