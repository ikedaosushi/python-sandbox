import asyncio, collections

v = asyncio.sleep(1)
print(isinstance(v, collections.abc.Generator))
print(getattr(v, "_asyncio_future_blocking", None))
print(v.__class__.__name__ )