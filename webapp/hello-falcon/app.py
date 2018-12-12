import falcon

class HelloResource:
    def on_get(self, req, resp):
        resp.body = "Hello World!"

app = falcon.API()
app.add_route('/', HelloResource())