import json


class return_values_from_sensor(object):
    def __init__(self,returnValue=None):
        if returnValue is not None:
            print(returnValue)
            self.returnValue=returnValue
            print(self.returnValue)
        else:self.returnValue=""


    @classmethod
    def from_get_config(cls, status, sample_rate, resolution, scale, dsp_function, dsp_parameter, mode, mac):
        reval=config_Object(status, sample_rate, resolution, scale, dsp_function, dsp_parameter, mode, mac)
        return cls(reval)

    @classmethod
    def from_get_time(cls, status, recieved_time, mac):
        reval=time_Object(status, recieved_time,mac)
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


class time_Object(object):
    def __init__(self,status, recieved_time,mac):
        self.status = status
        self.recieved_time = recieved_time
        self.mac = mac

class config_Object(object):
    def __init__(self, status, sample_rate, resolution, scale, dsp_function, dsp_parameter, mode, mac):
        self.status = status
        self.sample_rate = sample_rate
        self.resolution = resolution
        self.scale = scale
        self.dsp_function = dsp_function
        self.dsp_parameter = dsp_parameter
        self.mode = mode
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


