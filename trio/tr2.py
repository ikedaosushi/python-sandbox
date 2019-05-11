import trio

async def double_sleep(x):
    await trio.sleep(2 * x)

trio.run(double_sleep, 3)  # does nothing for 6 seconds then returns
print('after run')