import web  # pip install web.py
import ml4d
import csv  # CSV parser
import json  # json parser
import pandas as pd
import numpy as np

render = web.template.render('application/views/clean', base="../master")

class Detail:

    app_version = "0.1.0"  # version de la webapp
    file = 'static/csv/train.csv'  # define el archivo donde se almacenan los datos

    def __init__(self):  # Método inicial o constructor de la clase
        pass  # Simplemente continua con la ejecución

    def GET(self):
        try:
            dataframe = pd.read_csv(self.file)
            head = [dataframe.head()]
            cols = list(dataframe)
            nulls = list(dataframe.isnull().sum())
            dtypes = list(dataframe.dtypes)
            n = 0
            for i in nulls:
                if i != 0:
                    n += i
            unique = []
            mode = []
            mean = []
            median = []
            for col in cols:
                unique.append(len(dataframe[col].unique()))

            for i in range(len(dtypes)):
                if dtypes[i] == 'object':
                    # print("Col:{} mode: {}".format(cols[i],dataframe[cols[i]].mode()[0]))
                    mode.append(dataframe[cols[i]].mode()[0])
                    mean.append("None")
                    median.append("None")
                else:
                    # print("Col:{} mean: {}".format(cols[i],dataframe[cols[i]].mean()))
                    mode.append(dataframe[cols[i]].mode()[0])
                    mean.append(dataframe[cols[i]].mean())
                    median.append(dataframe[cols[i]].median())
                
            return render.detail(cols,nulls,dtypes,unique,mode,mean,median,n)
        except Exception as e:
            print(e.args)
            return render.error(e.args[0])

  