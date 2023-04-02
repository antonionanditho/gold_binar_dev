import pandas as pd
import re

from flask import Flask, appcontext_popped, jsonify
from flask import request
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from

app = Flask(__name__)

"""review:
Good, script load data yang dibutuhin udah tepat penempatannya
di sarankan buat load data disimpen di atas, sesudah import library
"""
# load data 
alay = pd.read_csv("new_kamusalay.csv", encoding="latin-1", names=("original","replacement"))
# abusive = pd.read_csv("abusive.csv", names=("stopword")) # ini salah, di data abusive nggak ada kolom stopword
abusive = pd.read_csv('abusive.csv', encoding='latin-1') #perbaikan load data abusive.

"""Review:
disarankan buat konfig template swagger nya diatas, setelah read data"""


# Flask Template
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
            "endpoint": 'docs',
            "route": '/docs.json',
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}
swagger = Swagger(app, template=swagger_template,             
                  config=swagger_config)
# End Flask Template


# cleaning preprocessing
# rules 1
def lowercase(text):
    return text.lower()

# rules 2
def remove_unnecessary_char(text):
    text = re.sub('\n',' ',text) # Remove every '\n'
    text = re.sub('rt',' ',text) # Remove every retweet symbol
    text = re.sub('user',' ',text) # Remove every username
    text = re.sub('((www\.[^\s]+)|(https?://[^\s]+)|(http?://[^\s]+))',' ',text) # Remove every URL
    text = re.sub('  +', ' ', text) # Remove extra spaces
    return text

# rules 3 
def remove_nonaplhanumeric(text):
    text = re.sub('[^0-9a-zA-Z]+', ' ', text) 
    return text

# rules 4
alay_dict_map = dict(zip(alay['original'], alay['replacement']))
def normalize_alay(text):
    return ' '.join([alay_dict_map[word] if word in alay_dict_map else word for word in text.split(' ')])

# rules 5
def remove_stopword(text):
    text = ' '.join(['' if word in abusive.values else word for word in text.split(' ')])
    text = re.sub('  +', ' ', text) # Remove extra spaces
    text = text.strip()
    return text

# rules 6 penggabungan seluruh fungsi
def preprocess(text):
    text = lowercase(text) # 1
    text = remove_nonaplhanumeric(text) # 2
    text = remove_unnecessary_char(text) # 3
    text = normalize_alay(text) # 4
    text = remove_stopword(text) # 5
    return text

"""Review: Good! response data nya udah nerapin fungsi preprocess(text)"""
# endpoint pertama
@swag_from("docs/text_processing.yml", methods=['POST'])
@app.route('/text-processing', methods=['POST'])
def text_processing():

    text = request.form.get('text')

    json_response = {
        'status_code': 200,
        'description': "Teks yang sudah diproses",
        'data': preprocess(text),
    }

    response_data = jsonify(json_response)
    return response_data

"""Review: Good! ini udah bener slicing nya pembacaan data dengan logika for nya"""
# endpoint kedua
@swag_from("docs/text_processing_file.yml", methods=['POST'])
@app.route('/text-processing-file', methods=['POST'])
def text_processing_file():

    # Upladed file
    file = request.files.getlist('file')[0]

    # Import file csv ke Pandas
    df = pd.read_csv(file)

    # Ambil teks yang akan diproses dalam format list
    # texts = df.text.to_list()

    # Lakukan cleansing pada teks
    cleaned_text = []
    for text in df["Tweet"]:
        cleaned_text.append(preprocess(text))

    json_response = {
        'status_code': 200,
        'description': "Teks yang sudah diproses",
        'data': cleaned_text,
    }

    response_data = jsonify(json_response)
    return response_data

if __name__ == '__main__':
   app.run()
