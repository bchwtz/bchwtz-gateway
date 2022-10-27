"""Testing the tagconfig.py."""
from gateway.tag.tagconfig import TagConfig




class TestTagConfig:
    test_config = TagConfig()
#---------- sample rate tests -------------------
    def test_set_samplerate_invalid(self):
        self.test_config.set_samplerate(11)
        assert self.test_config.samplerate == 0

    def test_set_samplerate_invalid_check_return(self):
        assert (self.test_config.set_samplerate(11) == None)
    

    def test_set_samplerate_valid(self):
        self.test_config.set_samplerate(10)
        assert self.test_config.samplerate == 10
#------------------resolution tests---------------------
    def test_set_resolution_invalid(self):
        self.test_config.set_resolution(11)
        assert self.test_config.resolution == 0

    def test_set_resolution_invalid_check_return(self):
        assert (self.test_config.set_resolution(11) == None)
    

    def test_set_resolution_valid(self):
        self.test_config.set_resolution(10)
        assert self.test_config.resolution == 10
#---------------------- scale tests -------------------    
    def test_set_scale_invalid(self):
        self.test_config.set_scale(11)
        assert self.test_config.scale == 0

    def test_set_scale_invalid_check_return(self):
        assert (self.test_config.set_scale(11) == None)
    

    def test_set_scale_valid(self):
        self.test_config.set_scale(8)
        assert self.test_config.scale == 8
#------------divider tests------------------
    def test_set_divider_to_high(self):
        self.test_config.set_divider(255)
        assert self.test_config.divider == 0

    def test_set_divider_to_high_check_return(self):
        assert (self.test_config.set_scale(255) == None)

    def test_set_divider_to_low(self):
        self.test_config.set_divider(-1)
        assert self.test_config.divider == 0

    def test_set_divider_to_low_check_return(self):
        assert (self.test_config.set_scale(-1) == None)    

    def test_set_divider_valid(self):
        self.test_config.set_divider(250)
        assert self.test_config.divider == 250