import pandas as pd
import re
import sqlite3
from flask import Flask, jsonify

app = Flask(__name__)

from flask import request
from flasgger  import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from

# update hapus codingan