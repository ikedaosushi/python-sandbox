import asyncio

async def child1():
    print("  child1: started! sleeping now...")
    await asyncio.sleep(1)
    print("  child1: exiting!")

async def child2():
    print("  child2: started! sleeping now...")
    await asyncio.sleep(1)
    print("  child2: exiting!")

async def parent():
    print("parent: started!")

    print("parent: spawning child1...")
    # asyncio.ensure_future(child1())

    print("parent: spawning child2...")
    # asyncio.ensure_future(child2())

    await asyncio.gather(child1(), child2())

    print("parent: waiting for children to finish...")
    # -- we exit the nursery block here --
    print("parent: all done!")

loop = asyncio.get_event_loop()
loop.run_until_complete(parent())