# -*- coding: utf-8 -*-
"""
Created on Wed Oct 13 20:19:09 2021

@author: mariu
"""

from enum import Enum


class SamplingRate(Enum):
    x01 = 1
    x0A = 10
    x19 = 25
    x32 = 50
    x64 = 100
    xC8 = 200
    xC9 = 400


class SamplingResolution(Enum):
    """
    For validation of the arguments set in set_config_sensor.
    """
    x08 = 8
    x0A = 10
    x0C = 12


class MeasuringRange(Enum):
    """
    For validation of the arguments set in set_config_sensor.
    """
    x02 = 2
    x04 = 4
    x08 = 8
    x10 = 16