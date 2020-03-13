import web  # pip install web.py
import csv  # CSV parser
import json  # json parser
import pandas as pd
import numpy as np
import statsmodels.api as sm
import scipy.stats as st
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure, show
import seaborn as sn
from sklearn.metrics import confusion_matrix
import matplotlib.mlab as mlab

render = web.template.render('application/views/', base="master")

class Describe:

    app_version = "0.1.0"  # version de la webapp
    file = 'static/csv/temp.csv'  # define el archivo donde se almacenan los datos

    def __init__(self):  # Método inicial o constructor de la clase
        pass  # Simplemente continua con la ejecución

    def GET(self):
        try:
            dataframe = pd.read_csv(self.file)
            de = dataframe.describe().to_dict()

            code_lines = []
            code_lines.append("# Describe")
            code_lines.append("dataframe.describe()")

            python_code=open('static/csv/code.py','a+')
            for element in code_lines:
                python_code.write(element+"\n")
            python_code.close()
            
            return render.describe(de)
        except Exception as e:
            print(e.args)

  