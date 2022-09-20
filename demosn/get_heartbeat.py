import asyncio
from gatewayn.hub.hub import Hub

async def run_demo():
    await hub.discover_tags(10)
    print(hub.tags)
    my_tag = hub.get_tag_by_address('CA:A5:49:28:D8:87')
    await my_tag.get_heartbeat()
    await my_tag.set_heartbeat(1001)
    await my_tag.get_heartbeat()

hub = Hub()
main_loop = asyncio.get_event_loop()
main_loop.run_until_complete(run_demo())
