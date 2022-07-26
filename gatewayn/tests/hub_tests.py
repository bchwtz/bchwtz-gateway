import pytest
from gatewayn.hub.hub import Hub

test_hub = Hub()
print(len(test_hub.sensors))
print(pytest.__version__)