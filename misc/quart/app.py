from quart import Quart, websocket

app = Quart(__name__)

@app.route('/')
async def hello():
    return 'hello'

@app.websocket('/ws')
async def ws():
    while True:
        await websocket.send('hello')

app.run()