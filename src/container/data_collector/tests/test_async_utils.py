from src import async_utils
import pytest
import aiohttp
import asyncio


@pytest.fixture(scope='function')
def aio_benchmark(benchmark):
    import asyncio
    import threading
    
    class Sync2Async:
        def __init__(self, coro, loop, *args, **kwargs):
            self.coro = coro
            self.args = args
            self.kwargs = kwargs
            self.custom_loop = loop
            self.thread = None
        
        def start_background_loop(self) -> None:
            asyncio.set_event_loop(self.custom_loop)
            self.custom_loop.run_forever()
        
        def __call__(self):
            evloop = None
            awaitable = self.coro(*self.args, **self.kwargs)
            try:
                evloop = asyncio.get_event_loop()
            except:
                pass
            if evloop is None:
                return asyncio.run(awaitable)
            else:
                if not self.custom_loop or not self.thread or not self.thread.is_alive():
                    #self.custom_loop = asyncio.new_event_loop()
                    self.thread = threading.Thread(target=self.start_background_loop, daemon=True)
                    self.thread.start()
                
                return asyncio.run_coroutine_threadsafe(awaitable, self.custom_loop).result()
    
    async def _wrapper(func, loop, *args, **kwargs):
        if asyncio.iscoroutinefunction(func):
            return benchmark(Sync2Async(func, loop, *args, **kwargs))
        else:
            return benchmark(func, *args, **kwargs)

    return _wrapper

@pytest.mark.asyncio
async def test_alexa_valid(aio_benchmark):
    loop = asyncio.new_event_loop()
    async with aiohttp.ClientSession(loop=loop) as session:
        assert await aio_benchmark(async_utils.alexa, loop, "google.com", session) == 1

@pytest.mark.asyncio
async def test_alexa_invalid(aio_benchmark):
    loop = asyncio.new_event_loop()
    async with aiohttp.ClientSession(loop=loop) as session:
        assert await aio_benchmark(async_utils.alexa, loop, "sdkfasdsdadafkgajlqwe.com", session) == -999


@pytest.mark.asyncio
async def test_brandable_valid(aio_benchmark):
    loop = asyncio.new_event_loop()
    async with aiohttp.ClientSession(loop=loop) as session:
        assert await aio_benchmark(async_utils.brandable, loop, "google.com", session)

@pytest.mark.asyncio
async def test_brandable_invalid(aio_benchmark):
    loop = asyncio.new_event_loop()
    async with aiohttp.ClientSession(loop=loop) as session:
        assert not await aio_benchmark(async_utils.brandable, loop, "sdkfasdsdadafkgajlqwe.com", session)

@pytest.mark.asyncio
async def test_wayback_valid(aio_benchmark):
    loop = asyncio.new_event_loop()
    async with aiohttp.ClientSession(loop=loop) as session:
        assert await aio_benchmark(async_utils.wayback, loop, "JESSEONTHEBRINK.com", session) >= 127

@pytest.mark.asyncio
async def test_wayback_invalid(aio_benchmark):
    loop = asyncio.new_event_loop()
    async with aiohttp.ClientSession(loop=loop) as session:
        assert await aio_benchmark(async_utils.wayback, loop, "sdkfasdsdadafkgajlqwe.com", session) == 0

@pytest.mark.asyncio
async def test_wikipedia_valid(aio_benchmark):
    loop = asyncio.new_event_loop()
    async with aiohttp.ClientSession(loop=loop) as session:
        assert await aio_benchmark(async_utils.wikipedia, loop, "google.com", session) == 4

@pytest.mark.asyncio
async def test_wikipedia_invalid(aio_benchmark):
    loop = asyncio.new_event_loop()
    async with aiohttp.ClientSession(loop=loop) as session:
        assert await aio_benchmark(async_utils.wikipedia, loop, "sdkfasdsdadafkgajlqwe.com", session) == 0

@pytest.mark.asyncio
async def test_fetch_details_valid(aio_benchmark):
    loop = asyncio.new_event_loop()
    async with aiohttp.ClientSession(loop=loop) as session:
        print(await aio_benchmark(async_utils.fetch_details, loop, "JESSEONTHEBRINK.com", session))

@pytest.mark.asyncio
async def test_fetch_details_invalid(aio_benchmark):
    loop = asyncio.new_event_loop()
    async with aiohttp.ClientSession(loop=loop) as session:
        print(await aio_benchmark(async_utils.fetch_details, loop, "sdkfasdsdadafkgajlqwe.com", session))


"""@pytest.fixture(scope='function')
def aio_benchmark(benchmark):
    import asyncio
    import threading
    
    class Sync2Async(asynctools.AbstractSessionContainer):
        def __init__(self, coro, *args, **kwargs):
            self.coro = coro
            self.args = args
            self.kwargs = kwargs
            self.custom_loop = None
            self.thread = None
        
        
        def start_background_loop(self) -> None:
            asyncio.set_event_loop(self.custom_loop)
            self.custom_loop.run_forever()
        
        @asynctools.attach_session
        def __call__(self, session=None):
            evloop = None
            self.args = self.args + (session,)
            awaitable = self.coro(*self.args, **self.kwargs)
            try:
                evloop = asyncio.get_running_loop()
            except:
                pass
            if evloop is None:
                return asyncio.run(awaitable)
            else:
                if not self.custom_loop or not self.thread or not self.thread.is_alive():
                    self.custom_loop = asyncio.new_event_loop()
                    self.thread = threading.Thread(target=self.start_background_loop, daemon=True)
                    self.thread.start()
                
                return asyncio.run_coroutine_threadsafe(awaitable, self.custom_loop).result()
    
    def _wrapper(func, loop, *args, **kwargs):
        if asyncio.iscoroutinefunction(func):
            return benchmark(Sync2Async(func, *args, **kwargs))
        else:
            return benchmark(func, *args, **kwargs)

    return _wrapper

def test_alexa(aio_benchmark):
    results = aio_benchmark(async_utils.alexa, "google.com")
    assert results == 1"""

