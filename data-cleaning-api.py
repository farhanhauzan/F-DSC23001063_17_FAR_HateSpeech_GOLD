import re
import pandas as pd
import sqlite3

from cleaning import cleansing
from flask import Flask, jsonify, request, Response
from flasgger import Swagger, LazyString, LazyJSONEncoder, swag_from


class CustomFlaskAppWithEncoder(Flask):
    json_provider_class = LazyJSONEncoder

app = CustomFlaskAppWithEncoder(__name__)

swagger_template = dict(
    info = {
        'title' : LazyString(lambda: "API Documentation for Data Processing and Modeling"),
        'version' : LazyString(lambda: "1.0.0"),
        'description' : LazyString(lambda: " API untuk Data Text Processing dan Modeling Level Gold"),
    },
    host = LazyString(lambda: request.host)
)


swagger_config = {
    "headers" : [],
    "specs" : [
        {
            "endpoint": "docs",
            "route" : "/docs.json",
        }
    ],
    "static_url_path": "/flasgger_static",
    # "static_folder": "static",  # must be set by user
    "swagger_ui": True,
    "specs_route": "/docs/"
}
swagger = Swagger(app, template=swagger_template, config = swagger_config)

# text processing route
@swag_from("docs/text_processing.yml", methods= ['POST'])
@app.route('/text-processing', methods=['POST'])
def text_processing():
    
    input_text = request.form.get('text')
    output_text = cleansing(input_text)

    json_response = {
        'status_code': 200,
        'description': "Text telah diproses",
        'input': input_text,
        'output': output_text,   
                   
    }

    response_data = jsonify(json_response)
    return response_data

@swag_from("docs/csv_processing.yml", methods= ['POST'])
@app.route('/csv-processing', methods=['POST'])
def csv_processing():

    file = request.files['file']
    tweet_df = pd.read_csv(file, encoding="latin-1")
    tweet_df.drop_duplicates(inplace=True)
    tweet_df['Tweet_clean'] = tweet_df['Tweet'].apply(cleansing)
    tweet_df = tweet_df.reindex(columns=['Tweet', 'Tweet_clean', 'HS', 'Abusive','HS_Individual','HS_Group','HS_Religion','HS_Race',
                             'HS_Physical','HS_Gender','HS_Other','HS_Weak','HS_Moderate','HS_Strong'])

    conn = sqlite3.connect("tweet.db")
    tweet_df.to_sql('tweet_clean', conn, if_exists='replace')
    conn.commit()
    conn.close() 
    
     
    json_response = {
        'status_code': 200,
        'description': "File telah diproses dan diupload kedalam database",
              
                   
    }

    response_data = jsonify(json_response)
    return response_data

if __name__ == '__main__':
    app.run()