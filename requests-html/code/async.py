from requests_html import AsyncHTMLSession
asession = AsyncHTMLSession()

async def get_pyconjp_2017():
    r = await asession.get(f"https://pycon.jp/2017/")
    return r

async def get_pyconjp_2018():
    r = await asession.get(f"https://pycon.jp/2018/")
    return r

async def get_pyconjp_2019():
    r = await asession.get(f"https://pycon.jp/2019/")
    return r

results = asession.run(get_pyconjp_2017, get_pyconjp_2018, get_pyconjp_2019)

for result in results:
    print(result.html.url)
# => https://pycon.jp/2018/
# => https://pycon.jp/2019/
# => https://pycon.jp/2017/ja/