# -*- coding: utf-8 -*-

# %% libraries
import re
import time
from unittest.mock import patch
from io import StringIO
import sys


class Testfunctions:
    def TC01_GetDataAndCheckTime(self, specific_mac):
        import SensorGatewayBleak
        print("in start_logging")
        test = SensorGatewayBleak.RuuviTagAccelerometerCommunicationBleak()
        test.deactivate_logging_at_sensor()
        time.sleep(15)
        test.activate_logging_at_sensor(specific_mac)
        time.sleep(15)
        acceleration_samples = test.get_acceleration_data()
        anz_fail = self.get_acceleration_time_differences_32_val(acceleration_samples, test)
        print("anzahl gefailter tests {}".format(anz_fail))

    def get_acceleration_time_differences(self, acceleration_samples, test):
        print("in get_acceleration_time_differences")
        time_vorher = None
        anz_korrekt = 0
        anz_fail = 0
        with patch('sys.stdout', new=StringIO()) as fake_out:
            test.get_config_from_sensor()
            # print('hallo',fake_out.getvalue())

            sys.stdout = sys.__stdout__
            # print('hallo', fake_out.getvalue())
            captured = fake_out.getvalue().splitlines()
            # print('captured',captured)
            for line in captured:
                # print('n', line)
                if re.search('Samplerate', line):
                    # print('drinnen')
                    # print(line)
                    # samplerate=(int(s) for s in line.split() if s.isdigit())

                    for s in line.split():
                        if s.isdigit():
                            samplerate = int(s)

                    print(samplerate)
                # print([int(s) for s in line.split() if s.isdigit()])
        # self.assertEqual(fake_out.getvalue(), expected_url)
        for element in acceleration_samples[0][0]:
            print(element)
            anz_elemente = len(acceleration_samples[0][0])
            time_ele = float(element[3].split(":")[2])
            if time_vorher is None:
                time_vorher = time_ele
                continue
            #            print("time_ele = {}".format(time_ele))
            #            print("time_vorher = {}".format(time_vorher))
            print("Diff = {}".format(time_ele - time_vorher))
            print("Sampling_rate = {}".format(samplerate))
            diff = round(time_ele - time_vorher, 4)
            #            print(diff)
            if (diff < 0):
                diff = round(diff + 60, 4)
                print("hier war diff negativ")
                print("diff + 60s = {}".format(diff))
            if (diff == 1 / samplerate):
                #                print("korrekt")
                anz_korrekt = anz_korrekt + 1
            else:
                print("fail")
                anz_fail = anz_fail + 1
            time_vorher = time_ele
        print("Es wurde {0} mal die Zeit Falsch  und {1} mal die Zeit richtig gesetzt".format(anz_fail, anz_korrekt))
        return anz_fail

    def get_acceleration_time_differences_32_val(self, acceleration_samples, test):
        print("in get_acceleration_time_differences_32_val")
        time_vorher = None
        anz_korrekt = 0
        anz_fail = 0
        time_index = 0
        with patch('sys.stdout', new=StringIO()) as fake_out:
            test.get_config_from_sensor()
            # print('hallo',fake_out.getvalue())
            sys.stdout = sys.__stdout__
            # print('hallo', fake_out.getvalue())
            captured = fake_out.getvalue().splitlines()
            # print('captured',captured)
            for line in captured:
                # print('n', line)
                if re.search('Samplerate', line):
                    # print('drinnen')
                    # print(line)
                    # samplerate=(int(s) for s in line.split() if s.isdigit())

                    for s in line.split():
                        if s.isdigit():
                            samplerate = int(s)

                    print(samplerate)
                # print([int(s) for s in line.split() if s.isdigit()])
        # self.assertEqual(fake_out.getvalue(), expected_url)
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
                    print("fail")
                    anz_fail = anz_fail + 1
                time_vorher = time_ele
        print("Es wurde {0} mal die Zeit Falsch  und {1} mal die Zeit richtig gesetzt".format(anz_fail, anz_korrekt))
        return anz_fail