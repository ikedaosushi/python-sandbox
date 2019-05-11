async def sync_async():
    await asyncio.sleep(0.1)
    return 'I hate event loops'

annoying_event_loop = asyncio.get_event_loop()
future = asyncio.ensure_future(sync_async(), loop=annoying_event_loop)
annoying_event_loop.run_until_complete(future)
print(future.result())