from gateway.hub.hub import Hub

import warnings
# https://github.com/pytest-dev/pytest-asyncio/issues/212
warnings.filterwarnings("ignore", category=DeprecationWarning) 

class TestHub:
    """This class is used to test the therotical functionality of the hub if no tag is present.
    All that is needed for that is an instance of the hub.
    """
    test_hub = Hub()

    def test_get_tag_by_mac(self):
        """Assertes that if the hub has no tag stored None is returned."""
        assert self.test_hub.get_tag_by_address() is None

    

    def test_get_tag_by_name_wrong_Mac(self):
        """Assertes that if the hub has no tag stored with the passed MAC None is returned."""
        assert self.test_hub.get_tag_by_address(address="not_existing") is None  

    def test_get_tag_by_name(self):
        """Assertes that if the hub has no tag stored None is returned."""
        assert self.test_hub.get_tag_by_name() is None

    def test_get_tag_by_name_wrong_name(self):
        """Assertes that if the hub has no tag stored with the passed name None is returned."""
        assert self.test_hub.get_tag_by_name(name="not_existing") is None

    def test_no_tags_found(self):
        """Asserts that no tags are stored in hub_tags."""
        assert len(self.test_hub.tags) == 0

