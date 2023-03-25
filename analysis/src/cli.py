import json
import pandas as pd

def askForGeojosn():
    while True:
        mapJson = input("Input map json name: ")
        mapJson = '%s.json' % mapJson
        try:
            with open(mapJson, encoding="utf-8") as json_file:  
                map = json.load(json_file)
        except FileNotFoundError as e:
            print(e)
        else:
            break
    return map

def getPoint(mode='data point'):
    while True:
        filename = input("Input %s csv file name: " % mode)
        try:
            df = pd.read_csv('%s.csv' % filename).dropna()
        except FileNotFoundError as e:
            print(e)
        else:
            break
    return df

# NOTE: Duplicated function (i.e. refer to the function above)
def getCluster():
    while True:
        filename = input("Input cluster csv file name: ")
        try:
            df = pd.read_csv('%s.csv' % filename)
        except FileNotFoundError as e:
            print(e)
        else:
            break
    return df

def exportCsv(data, mode='data point'):
    filename = input("Output %s csv file name: " % mode)
    data.to_csv('%s.csv' % filename, index=False, encoding='utf_8_sig')

def exportJson(data):
    filename = input("Output map geo json file name: ")
    with open('%s.json' % filename, 'w') as outfile:
        json.dump(data, outfile)