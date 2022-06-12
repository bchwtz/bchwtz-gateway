import asyncio # third-pary

class Event_ts(asyncio.Event):
    """Custom event loop class for the sensor().

    :param asyncio: None
    :type asyncio: Event_ts inherit asyncio.Event functions.
    """

    def clear(self):     
        self._loop.call_soon_threadsafe(super().clear)

    def set(self):    
        self._loop.call_soon_threadsafe(super().set)