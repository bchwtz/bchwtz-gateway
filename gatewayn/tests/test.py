import time
from unittest.mock import AsyncMock
from gatewayn.drivers.bluetooth.ble_conn.ble_conn import BLEConn
from bleak.backends.device import BLEDevice
from gatewayn.tag.tag_interface.encoder import Encoder
from gatewayn.tag.tag_interface.decoder import Decoder
from gatewayn.tag.tag_builder import TagBuilder
import asyncio
from datetime import datetime



def create_test_conn():
    conn = BLEConn()
    conn.run_single_ble_command = AsyncMock(return_value = None)

    # creating new BLEDevice
    ble_device = BLEDevice(
            address='6C:5D:7F:8G:9H',
            name='TestDevice')

    test_tag = TagBuilder().from_device(ble_device).build()

    test_tag.ble_conn = conn

    test_tag.get_config()  # Hier kriege ich None zurück.
    
    enc = Encoder()
    testtime = datetime.now().timestamp()
  
    print(f'testtime: {testtime}')
    testtime_encoded = enc.encode_time(time = testtime)
    print(testtime_encoded)
    
    # Erste Versuch, den wir zusammen überlegt haben. Hier kriege ich None zurück,weil er kein Signal findet.
    asyncio.run(test_tag.multi_communication_callback(0, bytes.fromhex(testtime_encoded)))
    

    # Zweiter Versuch, nach Montag.
    #print('setting time to')
    #test_tag.set_time_to_now() # Das funktioniert angeblich auch
    #print('test_tag.get_config()') # Hier kommt wieder None zurück
    #print(test_tag.get_time()) # Hier kommt auch None zurück.
    #print('Done')

    # Meine Vermutung ist, dass ich einen Fehler im Mocken habe. Anders würde ich nicht sehen, warum
    # ich sobald ich Werte vom Tag hole 'None' zurück bekomme.
    # Oder das Problem liegt in der Art zugrunde, wie ich den tag erstelle. Im from_device werden nämlich
    # keine Informationen über die Config und die Zeit gesetzt. Darum sind die nicht da. Im BLEDevice sind solche
    # Attribute auch nicht direkt vorgesehen, so wie ich das verstanden habe.

    # Oder ich hab einfach‚die TAg Klasse fundamental nicht verstanden. Was auch durchaus realistisch ist.


    # Alles hier drunter ist nicht mehr so wichtig.
    # print('after asyncio.run()')
    #time.sleep(5)
    # if test_tag.time == testtime:
    #     print("success")
    # print(test_tag.get_time())
    # print('Hello')
if __name__ == "__main__":
    create_test_conn()
