from flask import Flask, jsonify, Response, request, send_file
from flask_restful import Resource, Api
from pymongo import MongoClient
from flask_cors import CORS
import re
import pandas as pd
import json
from bson.json_util import dumps, loads
import webbrowser
import json
from os import environ as env
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for


client = MongoClient("mongodb://localhost:27017")
db = client.otvrac_posudjenice
posudj = db.posudjenice

login_check = 1


app = Flask(__name__)
api = Api(app)
CORS(app, resources={r"/*": {"origins": "*"}})

app.secret_key = "NmwjAnkdYNKyLNuAzfygGZ4Fn-1h9O_5iM4AZbvxRSGxSLy7jOdO8TrlyudEyOJ5"

oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id="Je3NSACtmJ5NG6gLbPm8bw5IMzhZb3Jd",
    client_secret="NmwjAnkdYNKyLNuAzfygGZ4Fn-1h9O_5iM4AZbvxRSGxSLy7jOdO8TrlyudEyOJ5",
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://dev-qm81qiwcvb8iormj.us.auth0.com/.well-known/openid-configuration'
)


@app.route("/login",  methods=["GET"])
def login():
    if("user" in session):
         return redirect(url_for("Home"))
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    print(session["user"])
    return render_template("index.html", session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))

@app.route("/logout")
def logout():
    session.clear()
    #print(session["user"])
    return redirect(url_for("Home"))


@app.route('/')
def Home():
    global login_check
    return render_template("index.html", session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))

@app.errorhandler(501)
def handle_not_implemented(error):
    return "Not implemented.", 501

class WordHTTP(Resource):
    def get(self, word):
        global posudj

        if not word:
            return 404

        queriedSearch = posudj.find_one({'word.word_cro' : word})
        json_data = dumps(queriedSearch)

        if queriedSearch:
            response = Response(status=200, response= json_data, mimetype="application/json")
            response.headers['message'] = 'success'
            return response
        else:
            response = Response(status=404, response = 'null')
            response.headers['message'] = 'No such word exists in the database'
            return response

    def put(self, word):
        global posudj
        data = request.json
        filterCriteria = {"word.word_cro" : word}
        updateOperation = {
            "$set" : {
                "example" : data["example"]
            }
        }

        result = posudj.update_one(filterCriteria, updateOperation)

        if result.modified_count > 0:
            response = Response(status = 200)
            response.headers["message"] = "Updated successfully"
            return response
        else:
            response = Response(status = 404, response = None)
            response.headers["message"] = "Update failed"
            return response
    def delete(self, word):
        global posudj

        if not word:
            return 404
        result = posudj.delete_one({"word.word_cro" : word})
        if result.deleted_count > 0:
            response= Response(status = 200)
            response.headers["message"] = "Deletion successful"
            return response
        else:
            response= Response(status = 404)
            response.headers["message"] = "Deletion failed"
            return response
def giveContext(json_data):
        context_data =  '{"@context":{ "@vocab": "http://schema.org/", "gender": "https://schema.org/gender", "orig_lang": "https://schema.org/Language"}},'

        index_open_bracket = json_data.find("[")
        index_open_brace = json_data.find("{", index_open_bracket)

        # Add your text between "[" and "{"
        data_with_context = (
            json_data[:index_open_bracket + 1]
            + context_data
            + json_data[index_open_brace:]
        )
        return data_with_context

def download_json():
        global posudj
        dataDump = posudj.find({})

        if dataDump is None:
            return Response(status = 404)
        json_data = dumps(dataDump)
        data_with_context = giveContext(json_data)
        response = Response(
            data_with_context,
            content_type="application/json",
            headers={"Content-disposition": "attachment; filename=data.json"}
        )

        return response


def download_csv():
    global posudj
    data = list(posudj.find())
    df = pd.DataFrame(data)
    csv_data = df.to_csv(index=False)

    response = Response(
        csv_data,
        content_type="text/csv",
        headers={"Content-disposition": "attachment; filename=data.csv"}
    )

    return response

@app.route("/retrieveall")
def retrieveall():
    return download_json()


class DatabaseRetrieve(Resource):
    def get(self):
        global posudj
        dataDump = posudj.find({})

        if dataDump is None:
            return Response(status = 404)

        json_data = dumps(dataDump)
        json_data = giveContext(json_data)
        response =Response(status = 200, response = json_data, mimetype="application/json")
        response.headers['message'] = 'Database retrieved'
        return response

class NounRetrieval(Resource):
    def get(self):
        global posudj

        query= {"gender" : {"$ne" : ""}}

        queriedSearch = posudj.find(query)

        if queriedSearch is None:
            return Response(status=404)

        json_data = dumps(queriedSearch)
        json_data = giveContext(json_data)
        response =Response(status = 200, response = json_data, mimetype="application/json")
        response.headers['message'] = 'All nouns retrieved'
        return response

class ExampleHTTP(Resource):
    def get(self):
        global posudj

        projection = {"example":1, "_id": 0}
        queriedData = posudj.find({}, projection)
        if queriedData is None:
            response = Response(status = 404, response = None)
            response.headers['message'] = 'Failed to send back examples'
            return response

        exampleData = list(queriedData)
        json_data = dumps(exampleData)
        json_data = giveContext(json_data)
        response = Response(status = 200, response = json_data, mimetype="application/json")
        response.headers['message'] = 'All examples sent'
        return response

class EntryHTTP(Resource):
    def get(self):
        global posudj

        pipeline = [{"$sample" : {"size" : 1}}]

        randomEntry = list(posudj.aggregate(pipeline))

        json_data = dumps(randomEntry)
        json_data = giveContext(json_data)
        if randomEntry is None:
            return Response(status=404, response= None)

        response = Response(status = 200, response=json_data, mimetype="application/json")
        response.headers['message'] = 'Random entry sent'
        return response
    def post(self):
        global posudj
        data = request.json
        required_fields = [
            data["word.word_cro"],
            data["word.word_orig_lang"],
            data["definition.definition_cro"],
            data["definition.definition_orig_lang"],
            data["type"],
            data["example"],
            data["orig_lang"],
            data["type_word"]
        ]
        optElement = data["gender"]
        if any(field == "" for field in required_fields):
            response = Response(status = 404)
            response.headers['message'] = "All fields except gender are mandatory"
            return response

        insertableData = {
            "word":{"word_cro":required_fields[0], "word_orig_lang":required_fields[1]},
             "definition":{"definition_cro": required_fields[2], "definition_orig_lang":required_fields[3]},
             "type":required_fields[4],
             "example":required_fields[5],
             "orig_lang":required_fields[6],
             "type_word":required_fields[7],
             "gender": optElement
        }
        posudj.insert_one(insertableData)
        insertedData = posudj.find_one(insertableData)
        jsondata = dumps(insertedData)

        response = Response(status = 201, response = jsondata)
        response.headers['message'] = 'Added entry successfully'
        return response


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

            # Save the DataFrame to a CSV files
            csv_data = df.to_csv( index=False)

            # Send the CSV file as a download
            return Response(csv_data, mimetype="text/csv")

        except Exception as e:
            print("Error:", e)
            return 'Internal server error', 500



api.add_resource(DBSearch, "/searchup")
api.add_resource(downloadCSV, "/downloadCSV")
api.add_resource(WordHTTP, '/croword/<string:word>')
api.add_resource(EntryHTTP, '/entry')
api.add_resource(DatabaseRetrieve, '/dumpall')
api.add_resource(NounRetrieval, "/nouns")
api.add_resource(ExampleHTTP, "/examples")
if __name__ == "__main__":
    app.run(debug=True)
