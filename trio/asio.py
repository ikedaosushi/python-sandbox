import asyncio

seconds = [
    ("first", 5),
    ("second", 0),
    ("third", 3)
]

async def sleeping(order, second, hook=None):
    await asyncio.sleep(second)
    if hook:
        hook(order)
    return order

async def basic_async(seconds):
    for s in seconds:
        r = await sleeping(*s)
        print(f"{r} is finished")

loop = asyncio.get_event_loop()
loop.run_until_complete(basic_async(seconds))