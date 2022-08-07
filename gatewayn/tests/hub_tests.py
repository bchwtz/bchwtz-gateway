import pytest
from gatewayn.hub.hub import Hub

import warnings
# https://github.com/pytest-dev/pytest-asyncio/issues/212
warnings.filterwarnings("ignore", category=DeprecationWarning) 
test_hub = Hub()

def test_get_tag_by_mac():
    assert test_hub.get_tag_by_mac() is None
      
def test_get_tag_by_name():
    assert test_hub.get_tag_by_name() is None

