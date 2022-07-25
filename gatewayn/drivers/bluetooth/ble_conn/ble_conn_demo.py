from gatewayn.drivers.bluetooth.bleconn.ble_conn import BLEConn

conn = BLEConn()

tags = conn.scan_tags()
print([tag.__dict__ for tag in tags])