from gateway.hub.hub import Hub
import time
import asyncio

#find tags
main_loop = asyncio.get_event_loop()
hub = Hub()
main_loop.run_until_complete(hub.discover_tags(timeout=5))

#pick one of the tags
tag = hub.get_tag_by_address("C1:FC:9B:69:04:8B")

#Get heartbeat
main_loop.run_until_complete(tag.set_heartbeat(1000))

main_loop.run_until_complete(tag.get_heartbeat())

print("finish")

#set heartbeat
# sensor1.set_heartbeat(1000) # 1 second