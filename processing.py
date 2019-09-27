import pandas.io.sql as sqlio
import psycopg2

import string
from stemming.porter2 import stem

from config import STOP_WORDS

def make_sql_request(query):
    connection = psycopg2.connect(user = "dfbgkpvujfyejl",
                                  password = "480b25edb1509aa455da09625ff9050d9a80633907f3f862bf7a29062b2ca9e7",
                                  host = "ec2-23-21-94-99.compute-1.amazonaws.com",
                                  port = "5432",
                                  database = "dfqj6tg3rrit6")
    df = sqlio.read_sql_query(query, connection)
    connection.close()
    return df

def filter_area(areas, loc):
    for i in areas:
        if i in loc:
            return True
    return False

def loc_list(loc):
    loc_list = []
    for i in range(len(loc)):
        loc_list.append(', '.join(loc[:i+1]))
    return loc_list

def clean_text(text):
    text = text.lower()
    text = ''.join([ch for ch in text if ch not in string.punctuation])
    text = text.split()
    text = [word for word in text if word not in STOP_WORDS]
    text = [stem(word) for word in text]
    return ' '.join(text)
