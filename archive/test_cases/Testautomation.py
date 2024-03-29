# -*- coding: utf-8 -*-
"""
# ! This file is not functioning any more. Trademarks and product names has been removed. 


The Automation library includes part of the automated tests and all helping functions for testautomation

    You can add tests with ascending numbering (TCxc)

For all tests we usually require SensorGatewayBleak library which is included via sys path
Author: Furkan Tombul
"""

# %% libraries
import re
import time
import sys
sys.path.append("..")
from unittest.mock import patch
from io import StringIO

# %% Testcases
class Testfunctions:
    # %% Testcase 01: Get acceleration data and check time stamps
    def TC01_GetDataAndCheckTime(self, specific_mac):
        from gateway import SensorGatewayBleak
        print("in start_logging")
        test = SensorGatewayBleak.TagAccelerometerCommunicationBleak()
        test.deactivate_debug_logger()
        time.sleep(5)
        test.activate_debug_logger()
        time.sleep(5)
        acceleration_samples = test.get_acceleration_data()
        anz_fail = self.get_acceleration_time_differences_32_val(acceleration_samples, test)
        print("anzahl gefailter tests {}".format(anz_fail))

    # %% Testcase 02: Set configuration and verify application
    def TC02_SetConfigAndCheckConfig(self, specific_mac, sampling_value, resolution_value, measuring_value):
        from gateway import SensorGatewayBleak
        print("Test start")
        test = SensorGatewayBleak.TagAccelerometerCommunicationBleak()
        test.activate_debug_logger()
        test.set_config_sensor(sampling_rate=sampling_value, sampling_resolution=resolution_value, measuring_range=measuring_value)
        config_datas = test.get_config_from_sensor()
        if (config_datas['Samplerate'] == sampling_value):
            print("sampling_rate = {}".format(sampling_value))
        else:
            print("set sampling_rate is not equal to the sampling_value: {} != {}".format(config_datas['Samplerate'], sampling_value))

        if (config_datas['Resolution'] == resolution_value):
            print("sampling_resolution = {}".format(resolution_value))
        else:
            print("set sampling_resolution is not equal to the resolution_value: {} != {}".format(config_datas['Resolution'], resolution_value))

        if (config_datas['Scale'] == measuring_value):
            print("measuring_range = {}".format(measuring_value))
        else:
            print("set measuring_range is not equal to the measuring_value: {} != {}".format(config_datas['Scale'], measuring_value))

    # %% Testcase 03: Set all configuration combinations and verify application
    def TC03_SetAndCheckAllConfigValues(self, specific_mac):
        from gateway import SensorGatewayBleak
        print("Test start")
        sampling_values = [1, 10, 25, 50, 100, 200, 400]
        resolution_values = [8, 10, 12]
        measuring_values = [2, 4, 8, 16]
        wrong_values = 0
        test = SensorGatewayBleak.TagAccelerometerCommunicationBleak()
#        test.activate_debug_logger()
        for sampling_value in sampling_values:
                for resolution_value in resolution_values:
                        for measuring_value in measuring_values:
                            test.set_config_sensor(sampling_rate=sampling_value, sampling_resolution=resolution_value, measuring_range=measuring_value)
                            config_datas = test.get_config_from_sensor()
                            if (config_datas['Samplerate'] == sampling_value):
                                print("sampling_rate = {}".format(sampling_value))
                            else:
                                print("set sampling_rate is not equal to the sampling_value: {} != {}".format(config_datas['Samplerate'], sampling_value))

                            if (config_datas['Resolution'] == resolution_value):
                                print("sampling_resolution = {}".format(resolution_value))
                            else:
                                print("set sampling_resolution is not equal to the resolution_value: {} != {}".format(config_datas['Resolution'], resolution_value))
                                wrong_values += 1

                            if (config_datas['Scale'] == measuring_value):
                                print("measuring_range = {}".format(measuring_value))
                            else:
                                print("set measuring_range is not equal to the measuring_value: {} != {}".format(config_datas['Scale'], measuring_value))
                                wrong_values += 1
        print("{} config values are not set correctly!".format(wrong_values))

    # %% Helping functions
    """
    include here all functions which are not explicitly Testcases, but are necessary test steps
    """

    # %% Calculate time differences and count - used for TC01
    def get_acceleration_time_differences_32_val(self, acceleration_samples, test):
        print("in get_acceleration_time_differences_32_val")
        time_vorher = None
        anz_korrekt = 0
        anz_fail = 0
        time_index = 0
        config_datas = test.get_config_from_sensor()
        samplerate=config_datas['Samplerate']
        for element in acceleration_samples[0][0]:
            print(element)
            time_index = time_index + 1
            #            anz_elemente = len(acceleration_samples[0][0])
            if time_vorher is None:
                time_vorher = float(element[3].split(":")[2])
                continue
            if time_index == 32:
                time_ele = float(element[3].split(":")[2])
                print("time_ele = {}".format(time_ele))
                print("time_vorher = {}".format(time_vorher))
                time_index = 0
                print("Diff = {}".format(time_ele - time_vorher))
                print("Sampling_rate = {}".format(samplerate))
                diff = round(time_ele - time_vorher, 4)
                #            print(diff)
                if (diff < 0):
                    diff = diff + 60
                    print("hier war diff negativ")
                if (diff >= 31 / samplerate and diff <= 33 / samplerate):
                    print("korrekt")
                    anz_korrekt = anz_korrekt + 1
                else:
                    print("falsch")
                    anz_fail = anz_fail + 1
                time_vorher = time_ele
        print("Es wurde {0} mal die Zeit Falsch  und {1} mal die Zeit richtig gesetzt".format(anz_fail, anz_korrekt))
        return anz_fail
