import pytest
import warnings
from bleak.exc import BleakDBusError, BleakError

def test_import_gateway():
    """This function gets called by pytest and tries to check, if the gateway library can be imported

    Raises:
        ModuleNotFoundError: If the installation wasn't successfull, a `ModuleNotFoundError` will be raised. 
    """    
    try:
        import gateway
    except ModuleNotFoundError:
        raise ModuleNotFoundError("""Can't import gateway library""")

def test_import_hub():
    """This function gets called by pytest and tries to check, if the module hub can be imported from gateway.

    Raises:
        ModuleNotFoundError: If the installation wasn't successfull, a `ModuleNotFoundError` will be raised. Other exception will raise other Error Messages, which can be seen in the test report. 
    """    
    try:
        from gateway import hub
    except ModuleNotFoundError:
        raise ModuleNotFoundError("""Can't import hub package""")

def test_function_discover():
    """This function tries to use the .discover function of the hub-object. Only the `BleakDBusError` is allowed for this test. If an other
    exception occures, there will be raised an error instead of an user warning.
    """    
    from gateway import hub
    myhub = hub.hub()
    try:
        myhub.discover()
    except BleakDBusError:
        warnings.warn(UserWarning("""BleakDBusError"""))

def test_import_sensor():
    """This function tries to initialize an object of the type sensor. No exceptions are allowed at this point.
    """    
    from gateway import sensor
    s1 = sensor.sensor('Guenter', '6C:5D:7F:8G:9H')

def test_call_acceleration_data_list():
    """This function tries to initialize an object of the type sensor and check for its class variable `data`. No exceptions are allowed at this point.
    """ 
    from gateway import sensor
    s1 = sensor.sensor('Guenter','6C:5D:7F:8G:9H')
    assert len(s1.data) == 0
    assert isinstance(s1.data, list)

def test_call_callback_data_list():
    """This function tries to initializ an object of the type sensor and check for its class variable `sensor_data`. No exceptions are allowed at this point.
    """    
    from gateway import sensor
    s1 = sensor.sensor('Guenter','6C:5D:7F:8G:9H')
    assert len(s1.sensor_data) == 0
    assert isinstance(s1.sensor_data, list)

def test_sensor_interface_config_channels():
    """This function checks, if the communications_interface.yml was successfully imported and compares the communication channels.
    """    
    from gateway import sensor
    conf = sensor.sensor_interface['communication_channels']
    assert len(conf.keys()) == 4
    assert conf['UART_SRV'] == '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'
    assert conf['UART_TX'] ==  '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'
    assert conf['UART_RX'] ==  '6E400003-B5A3-F393-E0A9-E50E24DCCA9E' 
    assert conf['Adv_UART_RX'] == '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'

def test_sensor_interface_config_commands():
    """This function checks, if the communications_interface.yml was successfully imported and compares the ruuvi_commands.
    """    
    from gateway import sensor
    conf = sensor.sensor_interface['ruuvi_commands']
    assert len(conf.keys())== 10
    assert conf['readAllString']== '4a4a110100000000000000'
    assert conf['activate_logging_at_sensor']== '4a4a080100000000000000'
    assert conf['deactivate_logging_at_sensor']== '4a4a080000000000000000'
    assert conf['get_acceleration_data']== '4a4a110100000000000000'
    assert conf['substring_set_config_sensor']== '4a4a02'
    assert conf['get_config_from_sensor']== '4a4a030000000000000000'
    assert conf['get_time_from_sensor']== '2121090000000000000000'
    assert conf['substring_set_sensor_time']== '212108'
    assert conf['get_flash_statistic']== 'FAFA0d0000000000000000'
    assert conf['get_logging_status']== '4A4A090000000000000000'

