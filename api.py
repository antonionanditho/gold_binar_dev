import pandas as pd
import re
import sqlite3
from flask import Flask, jsonify

app = Flask(__name__)

from flask import request
from flasgger  import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from

# load data tweet
data = pd.read_csv("C:/Users/MSI - Dito/Desktop/DSC/Chapter 3/Challenge Chapter 3/Asset Challenge/data.csv", encoding="latin-1")
# load data kamus alay
alay = pd.read_csv("C:/Users/MSI - Dito/Desktop/DSC/Chapter 3/Challenge Chapter 3/Asset Challenge/new_kamusalay.csv", encoding="latin-1", header=None)
alay = alay.rename(columns={0:'Original',
                            1:'baku'})
# load data abusive
abusive = pd.read_csv("C:/Users/MSI - Dito/Desktop/DSC/Chapter 3/Challenge Chapter 3/Asset Challenge/abusive.csv") 

# cleaning preprocessing
def cleaning_data(text):
    text = text.str.lower()
    text = re.sub("RT\s","", text)
    text = re.sub("USER\s","", text)
    text = re.sub("http[s]?\://\S+","", text)
    text = re.sub ("^\[x]","", text)
    text = re.sub('[^0-9a-zA-Z]+',"", text)
    return text


app.json_encoder = LazyJSONEncoder
swagger_template = dict(
info = {
    'title': LazyString(lambda: 'API Documentation for Data Processing and Modeling'),
    'version': LazyString(lambda: '1.0.0'),
    'description': LazyString(lambda: 'Dokumentasi API untuk Data Processing dan Modeling'),
    },
    host = LazyString(lambda: request.host)
)
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": '/docs',
            "route": '/docs.json',
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}
swagger = Swagger(app, template=swagger_template,             
                  config=swagger_config)


@swag_from("Chapter 3/Challenge Chapter 3/Asset Challenge/doc/text_processing_file.yml", methods=['POST'])
@app.route('/text_cleaning', methods=['POST'])
def text_processing_file():

    # Upladed file
    file = request.files.getlist('file')[0]

    # Import file csv ke Pandas
    df = pd.read_csv(file)

    # Ambil teks yang akan diproses dalam format list
    texts = df.text.to_list()

    # Lakukan cleansing pada teks
    cleaned_text = []
    for text in texts:
        cleaned_text.append(cleaning_data)

    json_response = {
        'status_code': 200,
        'description': "Teks yang sudah diproses",
        'data': cleaned_text,
    }

    response_data = jsonify(json_response)
    return response_data

if __name__ == '__main__':
   app.run()