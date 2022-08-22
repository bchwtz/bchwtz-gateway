from random import sample

from gatewayn.config import Config
import logging


class TagConfig:

    def __init__(self) -> None:
        self.samplerate: int = 0
        self.resolution: int = 0
        self.scale: int = 0
        self.dsp_function: int = 0
        self.dsp_parameter: int = 0
        self.mode: str = ""
        self.divider: int = 0
        self.logger = logging.getLogger("TagConfig")
        self.logger.setLevel(logging.INFO)

    def set_samplerate(self, samplerate: int) -> None:
        if samplerate not in Config.AllowedValues.samplerate.value:
            self.logger.error("defined samplerate not allowed")
            return
        self.samplerate = samplerate

    def set_resolution(self, resolution: int) -> None:
        if resolution not in Config.AllowedValues.sample_resolution.value:
            self.logger.error("defined samplerate not allowed")
            return
        self.resolution = resolution

    def set_scale(self, scale: int) -> None:
        if scale not in Config.AllowedValues.scale.value:
            self.logger.error("defined scale not allowed")
            return
        self.scale = scale

    def set_divider(self, divider: int) -> None:
        if divider > 254 or divider < 0:
            self.logger.error("divider is too big or too small (0-254)")
            return
        self.divider = divider