import pytest

def import_gateway():
    gateway = pytest.importorskip('gateway')