from gatewayn.hub.hub import Hub

hub = Hub()
hub.discover_sensors()
testtag = hub.get_sensor_by_name("Ruuvi 048B")
testtag.start_sensor_notification()