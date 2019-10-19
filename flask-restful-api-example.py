from flask import Flask, jsonify
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

class Hello(Resource):
    def __init__(self):
        super().__init__()
    def get(self):
        return jsonify(message="Hello world")


api.add_resource(Hello, '/')

if __name__ == '__main__':
    app.run(debug=True)
