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
        sampleratestr = f'{config.samplerate:x}'
        if config.resolution not in Config.AllowedValues.sample_resolution.value:
            config.resolution = 0xff
        resolutionstr = f'{config.resolution:x}'
        if config.scale not in Config.AllowedValues.scale.value:
            config.scale = 0xff
        scalestr = f'{config.scale:x}'
        if config.divider > 254:
            self.logger.warn("divider overflowed (max 0xff), resetting to 0xff")
            config.divider = 0xff
        dividerstr = f'{config.divider:x}'
        command = Config.Commands.set_tag_config_substr.value + sampleratestr + resolutionstr + scalestr + "ffffff" + dividerstr + "00"
        self.logger.info("Set sensor config {}".format(command))
        return command

    def encode_time(self, time: float = None) -> str:
        now = struct.pack("<Q", int(time * 1000)).hex()
        command = Config.Commands.set_tag_time_substr.value + now
        self.logger.info("Set sensor time {}".format(command))
        return command