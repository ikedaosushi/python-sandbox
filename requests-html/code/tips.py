# linksで「そのページからリンクされているURLの一覧」が取得できる
resp.html.links # => {'http://www.google.com/calendar/...

# HTMLのパースのみを使うことも可能
from requests_html import HTML
doc = """<a href='https://pyconjp/2019'>"""
html = HTML(html=doc)
html.links # => {"https://pyconjp/2019"}