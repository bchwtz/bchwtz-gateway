from gateway.hub.hub import Hub

import warnings
# https://github.com/pytest-dev/pytest-asyncio/issues/212
warnings.filterwarnings("ignore", category=DeprecationWarning) 

class TestHub:
    test_hub = Hub()

    def test_get_tag_by_mac(self):
        assert self.test_hub.get_tag_by_address() is None

    

    def test_get_tag_by_name_wrong_Mac(self):

        assert self.test_hub.get_tag_by_address(address="not_existing") is None  

    def test_get_tag_by_name(self):
        assert self.test_hub.get_tag_by_name() is None

    def test_get_tag_by_name_wrong_name(self):
        assert self.test_hub.get_tag_by_name(name="not_existing") is None

    def test_no_tags_found(self):
        assert len(self.test_hub.tags) == 0

