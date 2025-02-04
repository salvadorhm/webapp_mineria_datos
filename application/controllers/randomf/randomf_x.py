import web  # pip install web.py
import ml4d
import csv  # CSV parser
import json  # json parser
import pandas as pd
import numpy as np
import statsmodels.api as sm
import scipy.stats as st
import matplotlib.pyplot as plt
import seaborn as sn
from sklearn.metrics import classification_report, confusion_matrix,accuracy_score
import matplotlib.mlab as mlab

from sklearn.ensemble import RandomForestClassifier
from sklearn import preprocessing as pp

from matplotlib.pyplot import figure, show
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_curve, auc

#Reducción de dimensionalidad
from sklearn.decomposition import PCA
from sklearn.decomposition import KernelPCA
from sklearn.decomposition import IncrementalPCA

from application.controllers.save_code import SaveCode
sc = SaveCode()

render = web.template.render('application/views/randomf', base="../master")

class RandomfX:

    file = 'static/csv/train.csv'  # define el archivo donde se almacenan los datos

    def __init__(self):  # Método inicial o constructor de la clase
        pass  # Simplemente continua con la ejecución

    def GET(self):
        try:
            dataframe = pd.read_csv(self.file)
            cols = list(dataframe)
            y = ml4d.sessions['y']

            columns = []
            types = []
            nulls = []
            correlation = []
            cols.remove(y)
            for row in cols:
                if dataframe[row].dtypes != 'object' and dataframe[y].dtype != 'object':
                    correlation.append(dataframe[y].corr(dataframe[row]))
                    types.append(dataframe[row].dtype)
                    nulls.append(dataframe[row].isnull().sum())
                    columns.append((row))
                else:
                    correlation.append(0)
                    types.append(dataframe[row].dtype)
                    nulls.append(dataframe[row].isnull().sum())
                    columns.append((row))
            return render.randomf_x(columns,types,nulls,correlation)
        except Exception as e:
            print(e.args)
            return render.error(e.args[0])

    def POST(self):
        try:
            try:
                filename = ml4d.file['filename']
            except Exception as e:
                filename = "train.csv"
            y = ml4d.sessions['y']
            form = web.input(column = [''])
            x_cols = form.column
            ml4d.sessions['x']=list(x_cols)
            dataframe = pd.read_csv(self.file)

            df_x = dataframe[x_cols]
            df_y = dataframe[y]

            x_train, x_test, y_train, y_test = train_test_split(df_x,df_y,test_size=0.3,random_state=42)

            varianzas = x_train.describe().loc['std',:]
            medias = x_train.describe().loc['mean',:]
            
            model = RandomForestClassifier(n_estimators=80)
            # model = RandomForestClassifier(max_depth = 5, random_state = 101, criterion = 'gini', n_estimators = 50, min_samples_split = 5, min_samples_leaf = 2, max_features = 'log2')
            model.fit(x_train,y_train)
            predictions = model.predict(x_test)

            report = classification_report(y_test, predictions)
             
            labels = y_train.unique()
            confusion = confusion_matrix(y_test, predictions,labels)

            importances = model.feature_importances_
            indices = np.argsort(importances)

            features = x_train.columns

            r = pd.DataFrame({"features":features[indices], "importance":importances[indices]})
            results = r.sort_values(by='importance',ascending=False)

            compare = pd.DataFrame({"Actual":y_test, "Predicted":predictions})

            plt.figure()
            width=20
            height=8
            figure(figsize=(width,height))
            plt.title('Feature Importances')
            plt.barh(range(len(indices)), importances[indices], color='b', align='center')
            plt.yticks(range(len(indices)), features[indices])
            plt.xlabel('Relative Importance')
            image_name = "static/images/randomf.png"
            plt.savefig(image_name)

            figure()
            width=20
            height=8
            figure(figsize=(width,height))
            sn.distplot(varianzas, bins = 200, hist = True, kde = True, color = 'g')
            image_name = "static/images/varianzas.png"
            plt.savefig(image_name)

            figure()
            width=20
            height=8
            figure(figsize=(width,height))
            sn.distplot(medias, bins = 200, hist = True, kde = True)
            image_name = "static/images/medias.png"
            plt.savefig(image_name)

            #confusion_matrix
            figure()
            width=20
            height=8
            figure(figsize=(width,height))

            confusion_columns=[]
            confusion_index=[]
            # TODO revisar el orden de campos de la matriz de confucion con los nombre que le estoy dando
            for variable in labels:
                confusion_columns.append("Predicted:"+str(variable))
                confusion_index.append("Actual:"+str(variable))
            
            conf_matrix = pd.DataFrame(data=confusion,columns=confusion_columns,index=confusion_index)
            
            # sn.heatmap(conf_matrix, annot=True,fmt='d',cmap="YlGnBu")
            sn.heatmap(conf_matrix, annot=True,  fmt='d',cmap="YlGnBu")
            # confusion.plot()
            image_name = "static/images/confusion_matrix.png"
            plt.savefig(image_name)

            code = []
            code.append("import numpy as np")
            code.append("\n")
            code.append("from sklearn.metrics import classification_report, confusion_matrix")
            code.append("\n")
            code.append("from sklearn.model_selection import train_test_split")
            code.append("\n")
            code.append("from sklearn.ensemble import RandomForestClassifier")
            code.append("\n")
            code.append("dataframe = pd.read_csv("+filename+")")
            code.append("\n")
            code.append("df_x = dataframe["+str(x_cols)+"]")
            code.append("\n")
            code.append("df_y = dataframe['"+y+"']")
            code.append("\n")
            code.append("x_train, x_test, y_train, y_test = train_test_split(df_x,df_y,test_size=0.3,random_state=42)")
            code.append("\n")
            code.append("model = RandomForestClassifier(n_estimators=80)")
            code.append("\n")
            code.append("model.fit(x_train,y_train)")
            code.append("\n")
            code.append("predictions = model.predict(x_test)")
            code.append("\n")
            code.append("classification_report(y_test, predictions)")
            code.append("\n")
            code.append("confusion_matrix(y_test, predictions)")
            code.append("\n")
            code.append("importances = model.feature_importances_")
            code.append("\n")
            code.append("indices = np.argsort(importances)")
            code.append("\n")
            code.append("features = x_train.columns")

            total_cols = len(x_cols)
            total_cols_20 = int(abs(total_cols * 0.20))

            ml4d.randomf= {}
            ml4d.randomf['filename']= filename
            ml4d.randomf['y'] = y 
            ml4d.randomf['x'] = list(x_cols)
            ml4d.randomf['x_train.describe()['+str(x_cols[0])+"]"] = x_train.describe().to_dict()[x_cols[0]]
            ml4d.randomf['Report'] = report
            ml4d.randomf['Confusion matrix'] = list(confusion)
            ml4d.randomf['Score'] = model.score(x_test,y_test)
            ml4d.randomf['Accuracy score'] = accuracy_score(y_test, predictions)

            ml4d.randomf['Real test values'] = list(compare.Actual.head(10))
            ml4d.randomf['Predicted values'] = list(compare.Predicted.head(10))
            ml4d.randomf['Python'] = ''.join(code)
            ml4d.randomf['Features'] = list(results.features)[0:total_cols_20]
            ml4d.randomf['Importance'] = list(results.importance)[0:total_cols_20]


            '''
            ----------------------------------------------------------------------------------------
            Normalizado
            ----------------------------------------------------------------------------------------
            '''
            # scaler_x = pp.StandardScaler(copy = True)
            # df_nor_x = scaler_x.fit_transform(df_x)

            df_nor_x = (df_x - df_x.mean())/df_x.std()
            # df_nor_x = pp.normalize(df_x)

            x_train, x_test, y_train, y_test = train_test_split(df_nor_x,df_y,test_size=0.3,random_state=42)
            
            varianzas = x_train.describe().loc['std',:]
            medias = x_train.describe().loc['mean',:]

            model = RandomForestClassifier(n_estimators=80)
            # model = RandomForestClassifier(max_depth = 5, random_state = 101, criterion = 'gini', n_estimators = 50, min_samples_split = 5, min_samples_leaf = 2, max_features = 'log2')
            
            model.fit(x_train,y_train)
            
            predictions = model.predict(x_test)

            report = classification_report(y_test, predictions)
            labels = y_train.unique()
            confusion = confusion_matrix(y_test, predictions, labels)

            importances = model.feature_importances_
            indices = np.argsort(importances)

            features = x_train.columns


            r = pd.DataFrame({"features":features[indices], "importance":importances[indices]})
            results = r.sort_values(by='importance',ascending=False)

            compare = pd.DataFrame({"Actual":y_test, "Predicted":predictions})

            plt.figure()
            width=20
            height=8
            figure(figsize=(width,height))
            plt.title('Feature Importances')
            plt.barh(range(len(indices)), importances[indices], color='b', align='center')
            plt.yticks(range(len(indices)), features[indices])
            plt.xlabel('Relative Importance')
            image_name = "static/images/randomf_nor.png"
            plt.savefig(image_name)

            figure()
            width=20
            height=8
            figure(figsize=(width,height))
            sn.distplot(varianzas, bins = 200, hist = True, kde = True, color = 'g')
            image_name = "static/images/varianzas_nor.png"
            plt.savefig(image_name)

            figure()
            width=20
            height=8
            figure(figsize=(width,height))
            sn.distplot(medias, bins = 200, hist = True, kde = True)
            image_name = "static/images/medias_nor.png"
            plt.savefig(image_name)

            #confusion_matrix
            figure()
            width=20
            height=8
            figure(figsize=(width,height))

            confusion_columns=[]
            confusion_index=[]
            for variable in labels:
                confusion_columns.append("Predicted:"+str(variable))
                confusion_index.append("Actual:"+str(variable))
            
            conf_matrix = pd.DataFrame(data=confusion,columns=confusion_columns,index=confusion_index)
            sn.heatmap(conf_matrix, annot=True,fmt='d',cmap="YlGnBu")
            image_name = "static/images/confusion_matrix_nor.png"
            plt.savefig(image_name)

            code = []
            code.append("import numpy as np")
            code.append("\n")
            code.append("from sklearn.metrics import classification_report, confusion_matrix")
            code.append("\n")
            code.append("from sklearn.model_selection import train_test_split")
            code.append("\n")
            code.append("from sklearn.ensemble import RandomForestClassifier")
            code.append("\n")
            code.append("dataframe = pd.read_csv("+filename+")")
            code.append("\n")
            code.append("df_x = dataframe["+str(x_cols)+"]")
            code.append("\n")
            code.append("df_y = dataframe['"+y+"']")
            code.append("\n")
            code.append("df_nor_x = (df_x - df_x.mean())/df_x.std()")
            code.append("\n")
            code.append("x_train, x_test, y_train, y_test = train_test_split(df_x,df_y,test_size=0.3,random_state=42)")
            code.append("\n")
            code.append("model = RandomForestClassifier(n_estimators=80)")
            code.append("\n")
            code.append("model.fit(x_train,y_train)")
            code.append("\n")
            code.append("predictions = model.predict(x_test)")
            code.append("\n")
            code.append("classification_report(y_test, predictions)")
            code.append("\n")
            code.append("confusion_matrix(y_test, predictions)")
            code.append("\n")
            code.append("importances = model.feature_importances_")
            code.append("\n")
            code.append("indices = np.argsort(importances)")
            code.append("\n")
            code.append("features = x_train.columns")

            total_cols = len(x_cols)
            total_cols_20 = int(abs(total_cols * 0.20))

            ml4d.randomf_nor = {}
            ml4d.randomf_nor['filename']= filename
            ml4d.randomf_nor['y'] = y 
            ml4d.randomf_nor['x'] = list(x_cols)
            # ml4d.randomf_nor['x_train.describe()['+str(x_cols[0])+"]"] = pd.DataFrame(x_train).describe().to_dict()[x_cols[0]]
            ml4d.randomf_nor['Report'] = report
            ml4d.randomf_nor['Confusion matrix'] = list(confusion)
            ml4d.randomf_nor['Score'] = model.score(x_test,y_test)
            ml4d.randomf_nor['Accuracy score'] = accuracy_score(y_test, predictions)

            ml4d.randomf_nor['Real test values'] = list(compare.Actual.head(10))
            ml4d.randomf_nor['Predicted values'] = list(compare.Predicted.head(10))
            ml4d.randomf_nor['Python'] = ''.join(code)
            ml4d.randomf_nor['Features max 20%'] = list(results.features)[0:total_cols_20]
            ml4d.randomf_nor['Importance max 20%'] = list(results.importance)[0:total_cols_20]

            '''
            ----------------------------------------------------------------------------------------
            Normalizado PCA
            ----------------------------------------------------------------------------------------
            '''
            # scaler_x = pp.StandardScaler(copy = True)
            # df_nor_x = scaler_x.fit_transform(df_x)

            df_nor_x = (df_x - df_x.mean())/df_x.std()
            # df_nor_x = pp.normalize(df_x)

            x_train, x_test, y_train, y_test = train_test_split(df_nor_x,df_y,test_size=0.3,random_state=42)

            n = len(x_cols)
            pca_train = PCA(n_components = n)

            train_data = pca_train.fit_transform(x_train)
            test_data = pca_train.transform(x_test)

            train_dataframe = pd.DataFrame(data = train_data)
            test_dataframe = pd.DataFrame(data = test_data)

            reconstruct = pd.DataFrame(pca_train.components_, columns = x_cols)
            # print(reconstruct.head())

            # print(sum(pca_train.explained_variance_ratio_[:2]))

            # clf = RandomForestClassifier(max_depth = 5, random_state = 101, criterion = 'gini', 
            #                  n_estimators = 50, min_samples_split = 5, min_samples_leaf = 2, max_features = 'log2' )
            # clf.fit(train_data, y_train)
            # acc = clf.score(test_data, y_test)
            # print(acc)
            
            varianzas = train_dataframe.describe().loc['std',:]
            medias = train_dataframe.describe().loc['mean',:]

            model = RandomForestClassifier(n_estimators=80)
            # model = RandomForestClassifier(max_depth = 5, random_state = 101, criterion = 'gini', n_estimators = 50, min_samples_split = 5, min_samples_leaf = 2, max_features = 'log2')
            
            model.fit(train_data,y_train)
            
            predictions = model.predict(test_data)

            report = classification_report(y_test, predictions)
            confusion = confusion_matrix(y_test, predictions, labels)

            importances = model.feature_importances_
            indices = np.argsort(importances)

            features = x_train.columns


            r = pd.DataFrame({"features":features[indices], "importance":importances[indices]})
            results = r.sort_values(by='importance',ascending=False)

            compare = pd.DataFrame({"Actual":y_test, "Predicted":predictions})

            plt.figure()
            width=20
            height=8
            figure(figsize=(width,height))
            plt.title('Feature Importances')
            plt.barh(range(len(indices)), importances[indices], color='b', align='center')
            plt.yticks(range(len(indices)), features[indices])
            plt.xlabel('Relative Importance')
            image_name = "static/images/randomf_pca.png"
            plt.savefig(image_name)

            figure()
            width=20
            height=8
            figure(figsize=(width,height))
            sn.distplot(varianzas, bins = 200, hist = True, kde = True, color = 'g')
            image_name = "static/images/varianzas_pca.png"
            plt.savefig(image_name)

            figure()
            width=20
            height=8
            figure(figsize=(width,height))
            sn.distplot(medias, bins = 200, hist = True, kde = True)
            image_name = "static/images/medias_pca.png"
            plt.savefig(image_name)

            #confusion_matrix
            figure()
            width=20
            height=8
            figure(figsize=(width,height))
            confusion_columns=[]
            confusion_index=[]
            for variable in labels:
                confusion_columns.append("Predicted:"+str(variable))
                confusion_index.append("Actual:"+str(variable))
            
            conf_matrix = pd.DataFrame(data=confusion,columns=confusion_columns,index=confusion_index)
            sn.heatmap(conf_matrix, annot=True,fmt='d',cmap="YlGnBu")
            image_name = "static/images/confusion_matrix_pca.png"
            plt.savefig(image_name)

            code = []
            code.append("import numpy as np")
            code.append("\n")
            code.append("from sklearn.metrics import classification_report, confusion_matrix")
            code.append("\n")
            code.append("from sklearn.model_selection import train_test_split")
            code.append("\n")
            code.append("from sklearn.ensemble import RandomForestClassifier")
            code.append("\n")
            code.append("from sklearn.decomposition import PCA")
            code.append("\n")
            code.append("from sklearn.decomposition import KernelPCA")
            code.append("\n")
            code.append("from sklearn.decomposition import IncrementalPCA")
            code.append("\n")
            code.append("dataframe = pd.read_csv("+filename+")")
            code.append("\n")
            code.append("x_cols = list(dataframe)")
            code.append("\n")
            code.append("df_x = dataframe["+str(x_cols)+"]")
            code.append("\n")
            code.append("df_y = dataframe['"+y+"']")
            code.append("\n")
            code.append("df_nor_x = (df_x - df_x.mean())/df_x.std()")
            code.append("\n")
            code.append("x_train, x_test, y_train, y_test = train_test_split(df_x,df_y,test_size=0.3,random_state=42)")
            code.append("\n")
            code.append("n = len(x_cols)")
            code.append("\n")
            code.append("pca_train = PCA(n_components = n)")
            code.append("\n")
            code.append("train_data = pca_train.fit_transform(x_train)")
            code.append("\n")
            code.append("test_data = pca_train.transform(x_test)")
            code.append("\n")
            code.append("train_dataframe = pd.DataFrame(data = train_data)")
            code.append("\n")
            code.append("test_dataframe = pd.DataFrame(data = test_data)")
            code.append("\n")
            code.append("reconstruct = pd.DataFrame(pca_train.components_, columns = x_cols)")
            code.append("\n")
            code.append("print(reconstruct.head())")
            code.append("\n")
            code.append("model = RandomForestClassifier(n_estimators=80)")
            code.append("\n")
            code.append("model.fit(x_train,y_train)")
            code.append("\n")
            code.append("predictions = model.predict(x_test)")
            code.append("\n")
            code.append("classification_report(y_test, predictions)")
            code.append("\n")
            code.append("confusion_matrix(y_test, predictions)")
            code.append("\n")
            code.append("importances = model.feature_importances_")
            code.append("\n")
            code.append("indices = np.argsort(importances)")
            code.append("\n")
            code.append("features = x_train.columns")

            total_cols = len(x_cols)
            total_cols_20 = int(abs(total_cols * 0.20))

            ml4d.randomf_pca = {}
            ml4d.randomf_pca['filename']= filename
            ml4d.randomf_pca['y'] = y 
            ml4d.randomf_nor['x'] = list(x_cols)
            # ml4d.randomf_nor['x_train.describe()['+str(x_cols[0])+"]"] = pd.DataFrame(x_train).describe().to_dict()[x_cols[0]]
            ml4d.randomf_pca['Report'] = report
            ml4d.randomf_pca['Confusion matrix'] = list(confusion)
            ml4d.randomf_pca['Score'] = model.score(x_test,y_test)
            ml4d.randomf_pca['Accuracy score'] = accuracy_score(y_test, predictions)

            ml4d.randomf_pca['Real test values'] = list(compare.Actual.head(10))
            ml4d.randomf_pca['Predicted values'] = list(compare.Predicted.head(10))
            ml4d.randomf_pca['Python'] = ''.join(code)
            ml4d.randomf_pca['Features max 20%'] = list(results.features)[0:total_cols_20]
            ml4d.randomf_pca['Importance max 20%'] = list(results.importance)[0:total_cols_20]

            raise web.seeother('/randomf_r')
        except Exception as e:
            print(e.args)
            return render.error(e.args[0])
