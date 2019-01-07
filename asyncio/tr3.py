import trio
import asyncio

async def main():
    async with trio.open_nursery() as nursery:
        nursery.start_soon(asyncio.sleep, 1)

if __name__ == "__main__":
    trio.run(main)