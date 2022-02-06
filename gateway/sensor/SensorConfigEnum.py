"""This submodule is used to check the arguments of 
sensor.set_config()
"""
from enum import Enum


class SamplingRate(Enum):
    """For validation of the arguments set in `sensor.set_config()`

    :param Enum: Enumeration
    :type Enum: Enumeratione
    """
    x01 = 1
    x0A = 10
    x19 = 25
    x32 = 50
    x64 = 100
    xC8 = 200
    xC9 = 400


class SamplingResolution(Enum):
    """For validation of the arguments set in `sensor.set_config()`

    :param Enum: Enumeration
    :type Enum: Enumeratione
    """
    x08 = 8
    x0A = 10
    x0C = 12


class MeasuringRange(Enum):
    """For validation of the arguments set in `sensor.set_config()`

    :param Enum: Enumeration
    :type Enum: Enumeratione
    """
    x02 = 2
    x04 = 4
    x08 = 8
    x10 = 16
