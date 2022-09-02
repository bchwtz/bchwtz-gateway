import asyncio
import struct

from bleak import BleakScanner

timeout_seconds = 20
address_to_look_for = 'F1:D9:3B:39:4D:A2'
service_id_to_look_for = '0000feaa-0000-1000-8000-00805f9b34fb'


class AdvertismentScanner:
    def __init__(self):
        self._scanner = BleakScanner()
        self._scanner.register_detection_callback(self.detection_callback)
        self.scanning = asyncio.Event()

    def detection_callback(self, device, advertisement_data):
        # Looking for:
        # AdvertisementData(service_data={
        # '0000feaa-0000-1000-8000-00805f9b34fb': b'\x00\xf6\x00\x00\x00Jupiter\x00\x00\x00\x00\x00\x0b'},
        # service_uuids=['0000feaa-0000-1000-8000-00805f9b34fb'])
        if device.address == address_to_look_for:
            byte_data = advertisement_data.service_data.get(service_id_to_look_for)
            num_to_test, = struct.unpack_from('<I', byte_data, 0)
            if num_to_test == 62976:
                print('\t\tDevice found so we terminate')
                self.scanning.clear()

    async def run(self):
        await self._scanner.start()
        self.scanning.set()
        end_time = loop.time() + timeout_seconds
        while self.scanning.is_set():
            if loop.time() > end_time:
                self.scanning.clear()
                print('\t\tScan has timed out so we terminate')
            await asyncio.sleep(0.1)
        await self._scanner.stop()


if __name__ == '__main__':
    my_scanner = AdvertismentScanner()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(my_scanner.run())