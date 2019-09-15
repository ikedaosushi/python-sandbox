# find()でCSS Selectorで要素を探します。first=Trueにすることで最初の要素を取得できる
title = resp.html.find('h4.card-title', first=True)

title.text # => Pythonとは
title.attrs # => {'class': ('card-title',)}
title.find('a') # => [<Element 'a' href='pages/about.html'>]
title.search('{}とは')[0] # => Python