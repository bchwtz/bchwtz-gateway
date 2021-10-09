import json
import struct


class return_values_from_sensor(object):
    def __init__(self,returnValue=None):
        if returnValue is not None:
            print(returnValue)
            self.returnValue=returnValue
            print(self.returnValue)
        else:self.returnValue=""


    @classmethod
    def from_get_config(cls, status, sample_rate, resolution, scale, dsp_function, dsp_parameter, mode,divider, mac):
        reval=config_Object(status, sample_rate, resolution, scale, dsp_function, dsp_parameter, mode,divider, mac)
        return cls(reval)

    @classmethod
    def from_get_time(cls, status, recieved_time, mac):
        reval=time_Object(status, recieved_time,mac)
        print("got Time")
        return cls(reval)

    @classmethod
    def from_get_flash_statistics(cls, message_status, logging_status, ringbuffer_start, ringbuffer_end, mac,
                                  ringbuffer_size, valid_records, dirty_records, words_reserved, words_used,
                                  largest_contig,
                                  freeable_words):
        reval = flash_statistics_Object( message_status, logging_status, ringbuffer_start, ringbuffer_end, mac,
                                  ringbuffer_size, valid_records, dirty_records, words_reserved, words_used,
                                  largest_contig,
                                  freeable_words)
        return cls(reval)
    @classmethod
    def form_get_logging_status(cls, status):
        reval=logging_status_object(status)
        print(reval)
        return cls(reval)

    @classmethod
    def from_get_accelorationdata(cls,accelorationdata,mac):
        reval=acceloration_data_Object(accelorationdata,mac)
        return cls(reval)
    
    @classmethod
    def from_get_advertisementdata(cls,advertisementdata,mac):
        reval=acceloration_data_Object(accelorationdata,mac)
        return cls(reval)


class time_Object(object):
    def __init__(self,status, recieved_time,mac):
        self.status = status
        self.recieved_time = recieved_time
        self.mac = mac

class config_Object(object):
    def __init__(self, status, sample_rate, resolution, scale, dsp_function, dsp_parameter, mode, divider, mac):
        self.status = status
        self.sample_rate = sample_rate
        self.resolution = resolution
        self.scale = scale
        self.dsp_function = dsp_function
        self.dsp_parameter = dsp_parameter
        self.mode = mode
        self.divider=divider
        self.mac = mac

class flash_statistics_Object(object):
    def __init__(self, message_status, logging_status, ringbuffer_start, ringbuffer_end, mac,
                                  ringbuffer_size, valid_records, dirty_records, words_reserved, words_used,
                                  largest_contig,
                                  freeable_words):
        self.message_status = message_status
        self.logging_status = logging_status
        self.ringbuffer_start = ringbuffer_start
        self.ringbuffer_end = ringbuffer_end
        self.ringbuffer_size = ringbuffer_size
        self.valid_records = valid_records
        self.dirty_records = dirty_records
        self.words_reserved = words_reserved
        self.words_used = words_used
        self.largest_contig = largest_contig
        self.freeable_words = freeable_words
        self.mac = mac

class logging_status_object(object):
    def __init__(self, status):
        print("logging status")
        if status==0:
            self.logging_is_active=1
        elif status==1:
            self.logging_is_active=0
        print(self.logging_is_active)

class acceloration_data_Object(object):
    def __init__(self, accelorationData, mac):
        self.loggingData=list(map(list, zip(accelorationData[0], accelorationData[1], accelorationData[2],
                           accelorationData[3])))
        self.mac=mac

class advertisement_data_Object(object):
    def __init__(self, data)

class send_msg_object(object):
    def __init__(self, command=None):
        if command is not None:
            print(command)
            self.command = command
            print(self.command)
        else:
            self.command = ""


    @classmethod
    def to_set_sensorTime(cls, time, mac):
        if time is isinstance(float,time):

            timestamp = struct.pack("<Q", int(time * 1000)).hex()
            command="212108" + timestamp
            reval = sensor_time_Object(mac, command)
            return cls(reval)

class sensor_time_Object(object):
        def __init__(self, mac, command):
            self.mac=mac
            self.command=command
