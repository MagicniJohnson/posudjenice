from flask import Flask, jsonify, Response, request, send_file
from flask_restful import Resource, Api
from pymongo import MongoClient
from flask_cors import CORS
import re
import pandas as pd
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
        if selectedField == 'wildcard':
            columns_to_search = [
                "word.word_cro",
                "word.word_orig_lang",
                "definition.definition_cro",
                "definition.definition_orig_lang",
                "type",
                "type_word",
                "gender"
            ]
            queriedSearch =posudj.find({"$or" : [{"word.word_cro": {"$regex": f'^{searchTerm}'}}, 
                                                 {"word.word_orig_lang": {"$regex": f'^{searchTerm}'}},
                                                 {"definition.definition_cro": {"$regex": f'^{searchTerm}'}},
                                                 {"definition.definition_orig_lang": {"$regex": f'^{searchTerm}'}},
                                                 {"type": {"$regex": f'^{searchTerm}'}},
                                                 {"type_word": {"$regex": f'^{searchTerm}'}},
                                                 { "gender": {"$regex": f'^{searchTerm}'}}]})
            json_data = dumps(list(queriedSearch))
            return json_data
        else:
            queriedSearch = posudj.find({selectedField : {"$regex": f'^{searchTerm}'}})
            json_data = dumps(list(queriedSearch))
            return json_data
class downloadCSV(Resource):
    def post(self):
        try:
            # Get the stringified JSON data from the request
            json_str = request.get_json()

            # Convert the JSON string to a Python list using json.loads
            json_list = json.loads(json_str)

            # Convert the list of JSON objects to a DataFrame
            csv_filename = "filter.csv"
            df = pd.json_normalize(json_list)
            print(df)

            # Save the DataFrame to a CSV file
            csv_data = df.to_csv( index=False)

            # Send the CSV file as a download
            return Response(csv_data, mimetype="text/csv")

        except Exception as e:
            print("Error:", e)
            return 'Internal server error', 500

    
api.add_resource(DBSearch, "/searchup")
api.add_resource(downloadCSV, "/downloadCSV")

if __name__ == "__main__":
    app.run(debug=True)