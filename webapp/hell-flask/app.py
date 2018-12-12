from flask import Flask, jsonify, make_response, request

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/osushi')
def osushi():
    return jsonify({
        "neta": "マグロ",
        "wasabi": True
    }), 200

@app.route('/hello/<who>')
def hello_to(who):
    foo = request.args.get('foo', '')
    body = jsonify({
        "Hello": who,
        "Foo": foo 
    })
    resp = make_response(body, 200)
    resp.headers['X-Pizza'] = "42"
    return resp