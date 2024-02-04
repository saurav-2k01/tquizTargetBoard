import json
import csv
import pandas as pd
import os

def csv2json(filename, encoding="utf-8"):
    with open(filename,encoding=encoding) as file:
        raw_data = csv.DictReader(file)
        json_data = []
        for i in raw_data:
            json_data.append(json.dumps(i, indent=4))
        return json_data

def csv2list(filename, encoding="utf-8"):
    data = []
    try:
        with open(filename, encoding=encoding) as file:
            for i in csv.reader(file):
                data.append(i[1:])
        return data
    except Exception as E:
        print(E)

def xl2list(filename):
    data = []
    try:
        df = pd.read_excel(filename, engine="openpyxl")
        data_= df.values.tolist()
        for i in data_:
            data.append(i[1:])
        return data
    except Exception as E:
        print(E)
