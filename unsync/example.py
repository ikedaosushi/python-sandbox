@unsync
async def unsync_async():
    await asyncio.sleep(0.1)
    return 'I like decorators'

print(unsync_async().result())