from flask import Flask, jsonify, Response, request
from flask_restful import Resource, Api
from pymongo import MongoClient
from flask_cors import CORS
import re
import json
from bson.json_util import dumps, loads

client = MongoClient("mongodb://localhost:27017")
db = client.otvrac_posudjenice
posudj = db.posudjenice

app = Flask(__name__)
api = Api(app)
CORS(app)

@app.route('/')
def Home():
    return ''

class DBSearch(Resource):
    def post(self):
        global posudj
        dataReq =  request.get_json()
        searchTerm = dataReq.get('searchTerm')
        selectedField = dataReq.get('selectedField')
        query = posudj.find({selectedField : {"$regex": f'^{searchTerm}'}})
        json_data = dumps(list(query))
        return json_data
    
api.add_resource(DBSearch, "/searchup")

if __name__ == "__main__":
    app.run(debug=True)