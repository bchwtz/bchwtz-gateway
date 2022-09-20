from logging import Logger
import logging
from random import sample
import struct
from time import time
from gatewayn.config import Config
from gatewayn.tag.tagconfig import TagConfig


class Encoder():
    def __init__(self) -> None:
        self.logger: Logger = logging.getLogger("Encoder")
        self.logger.setLevel(logging.INFO)
    
    def encode_config(self, config: TagConfig) -> str:
        if config.samplerate not in Config.AllowedValues.samplerate.value:
            config.samplerate = 0xff
        if config.samplerate >= 255:
            config.samplerate = 0xc9
        sampleratestr = "{:02x}".format(config.samplerate)
        if config.resolution not in Config.AllowedValues.sample_resolution.value:
            config.resolution = 0xff
        resolutionstr = "{:02x}".format(config.resolution)
        if config.scale not in Config.AllowedValues.scale.value:
            config.scale = 0xff
        scalestr = "{:02x}".format(config.scale)
        # TODO : make another class that checks the combination of divider and samplerate and calculates a valid config
        if config.divider > 254:
            self.logger.warn("divider overflowed (max 0xff), resetting to 0xff")
            config.divider = 0xff
        dividerstr = "{:02x}".format(config.divider)
        command = Config.Commands.set_tag_config_substr.value + sampleratestr + resolutionstr + scalestr + "ffffff" + dividerstr + "00"
        self.logger.debug("Set sensor config {}".format(command))
        return command

    def encode_time(self, time: float = None) -> str:
        now = struct.pack("<Q", int(time * 1000)).hex()
        command = Config.Commands.set_tag_time_substr.value + now
        self.logger.debug("Set sensor time {}".format(command))
        return command

    def encode_heartbeat(self, interval: int = 0) -> str:
        hex_beat = hex(interval)[2:]
        hex_msg = f"{Config.Commands.set_heartbeat_substr.value}{'0000'[:4 - len(hex_beat)]}{hex_beat}000000000000"
        return hex_msg