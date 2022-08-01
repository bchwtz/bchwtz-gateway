import pytest
from gatewayn.hub.hub import Hub

test_hub = Hub()
print(len(test_hub.tags))
print(pytest.__version__)