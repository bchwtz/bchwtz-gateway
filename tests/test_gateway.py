import pytest
import warnings
from bleak.exc import BleakDBusError, BleakError

def test_import_gateway():
    try:
        import gateway
    except ModuleNotFoundError:
        raise ModuleNotFoundError("""Can't import gateway library""")

def test_import_hub():
    try:
        from gateway import hub
    except ModuleNotFoundError:
        raise ModuleNotFoundError("""Can't import hub package""")

def test_function_discover():
    from gateway import hub
    myhub = hub.hub()
    try:
        myhub.discover()
    except BleakDBusError:
        warnings.warn(UserWarning("""BleakDBusError"""))

def test_import_sensor():
    from gateway import sensor
    s1 = sensor.sensor('Guenter', '6C:5D:7F:8G:9H')

def test_call_acceleration_data_list():
    from gateway import sensor
    s1 = sensor.sensor('Guenter','6C:5D:7F:8G:9H')
    assert len(s1.data) == 0
    assert isinstance(s1.data, list)

def test_call_callback_data_list():
    from gateway import sensor
    s1 = sensor.sensor('Guenter','6C:5D:7F:8G:9H')
    assert len(s1.sensor_data) == 0
    assert isinstance(s1.sensor_data, list)

def test_sensor_interface_config_channels():
    from gateway import sensor
    conf = sensor.sensor_interface['communication_channels']
    assert len(conf.keys()) == 4
    assert conf['UART_SRV'] == '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'
    assert conf['UART_TX'] ==  '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'
    assert conf['UART_RX'] ==  '6E400003-B5A3-F393-E0A9-E50E24DCCA9E' 
    assert conf['Adv_UART_RX'] == '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'

def test_sensor_interface_config_commands():
    print("Lorem Ipsum")


#def test_debug_test():
#    assert(2==2)
