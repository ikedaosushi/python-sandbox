from requests_html import HTMLSession

session = HTMLSession()

resp = session.get("https://www.python.jp/")
resp.html.url