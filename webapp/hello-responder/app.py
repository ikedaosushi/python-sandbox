import responder 
import time

api = responder.API()

@api.route("/")
def hello_world(req, resp):
  resp.text = "hello, world!"

@api.route("/hello/{who}")
def hello_to(req, resp, *, who):
    resp.text = f"Hello, {who}!"

@api.route("/hello/{who}/json")
def hello_to(req, resp, *, who):
    foo = req.params.get('foo', None)
    resp.headers['X-Pizza'] = '42'
    resp.status_code = 200
    resp.media = {
      "Hello": who,
      "Foo": foo
    }

@api.route("/hello/{who}/html")
def hello_html(req, resp, *, who):
    resp.content = api.template('hello.html', who=who)

@api.route("/pizza")
def pizza_pizza(req, resp):
    resp.headers['X-Pizza'] = '42'

@api.route("/incoming")
async def receive_incoming(req, resp):

    @api.background.task
    def process_data(data):
        """Just sleeps for three seconds, as a demo."""
        time.sleep(3)

    # Parse the incoming data as form-encoded.
    # Note: 'json' and 'yaml' formats are also automatically supported.
    data = await req.media()

    # Process the data (in the background).
    process_data(data)

    # Immediately respond that upload was successful.
    resp.media = {'success': True}

@api.route("/{greeting}")
class GreetingResource:
    def on_request(self, req, resp, *, greeting):   # or on_get...
        resp.text = f"{greeting}, world!"
        resp.headers.update({'X-Life': '42'})
        resp.status_code = api.status_codes.HTTP_416

@api.route("/background")
def hello(req, resp):

    @api.background.task
    def sleep(s=10):
        time.sleep(s)
        print("slept!")

    sleep()
    resp.content = "processing"


import graphene

class Query(graphene.ObjectType):
    hello = graphene.String(name=graphene.String(default_value="stranger"))

    def resolve_hello(self, info, name):
        return f"Hello {name}"

schema = graphene.Schema(query=Query)
view = responder.ext.GraphQLView(api=api, schema=schema)

api.add_route("/graph", view)

api.run()