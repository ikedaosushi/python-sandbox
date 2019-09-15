from requests_html import AsyncHTMLSession
asession = AsyncHTMLSession()

async def exec_js():
    resp = await asession.get("https://pycon.jp/2019/")
    print("before:", resp.html.find("h2", first=True)) # => None
    await resp.html.arender()
    print("after:", resp.html.find("h2", first=True).text) # => {'https://pyconjp.connpass.com/event/139133/', ...}

loop = asyncio.get_event_loop() 
loop.run_until_complete(exec_js())

# => before: None
# => after: Conference