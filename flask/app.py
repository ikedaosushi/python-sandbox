from flask import Flask, jsonify

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