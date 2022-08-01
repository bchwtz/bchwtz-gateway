from gatewayn.hub.hub import Hub

hub = Hub()
hub.discover_tags()
testtag = hub.get_tag_by_name("Ruuvi 048B")
testtag.get_acceleration_log()