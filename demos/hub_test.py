from gatewayn.hub.hub import Hub

hub = Hub()
hub.discover_tags()

testtag = hub.get_tag_by_name("Ruuvi 048B")
testtag.get_config()
# testtag.get_time()
print(testtag.__dict__)
print(testtag.config.__dict__)