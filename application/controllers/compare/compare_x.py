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
from sklearn import tree as tree_pl

from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC

from matplotlib.pyplot import figure, show
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_curve, auc

from application.controllers.save_code import SaveCode
sc = SaveCode()


render = web.template.render('application/views/compare', base="../master")

class CompareX():

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
            return render.compare_x(columns,types,nulls,correlation)
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
            ml4d.sessions['y']= y
            dataframe = pd.read_csv(self.file)

            df_x = dataframe[x_cols]
            df_y = dataframe[y]

            x_train, x_test, y_train, y_test = train_test_split(df_x,df_y,test_size=0.3,random_state=42)
            labels = y_train.unique()
            '''
            ---------------------------------------------------------------------------
            KNeighbors classifier
            ---------------------------------------------------------------------------
            '''
            knn = KNeighborsClassifier(n_neighbors=5, weights='uniform', algorithm='auto', leaf_size=30, p=2, metric='minkowski', metric_params=None, n_jobs=None)

            knn.fit(x_train,y_train)
            predictions = knn.predict(x_test)

            report = classification_report(y_test, predictions)
            confusion = confusion_matrix(y_test, predictions)

            figure()
            width=10
            height=4
            figure(figsize=(width,height))

            confusion_columns=[]
            confusion_index=[]
            for variable in labels:
                confusion_columns.append("Predicted:"+str(variable))
                confusion_index.append("Actual:"+str(variable))
            conf_matrix = pd.DataFrame(data=confusion,columns=confusion_columns,index=confusion_index)
            sn.heatmap(conf_matrix, annot=True,  fmt='d',cmap="YlGnBu")
            image_name = "static/images/knn.png"
            plt.savefig(image_name)

 
            code = []
            code.append("import numpy as np")
            code.append("\n")
            code.append("from sklearn.metrics import classification_report, confusion_matrix")
            code.append("\n")
            code.append("from sklearn.model_selection import train_test_split")
            code.append("\n")
            code.append("from sklearn.neighbors import KNeighborsClassifier")
            code.append("\n")
            code.append("dataframe = pd.read_csv('"+filename+"')")
            code.append("\n")
            code.append("df_x = dataframe["+str(x_cols)+"]")
            code.append("\n")
            code.append("df_y = dataframe['"+y+"']")
            code.append("\n")
            code.append("x_train, x_test, y_train, y_test = train_test_split(df_x,df_y,test_size=0.3,random_state=42)")
            code.append("\n")
            code.append("model = KNeighborsClassifier(n_neighbors=5, weights='uniform', algorithm='auto', leaf_size=30, p=2, metric='minkowski', metric_params=None, n_jobs=None)")
            code.append("\n")
            code.append("model.fit(x_train,y_train)")
            code.append("\n")
            code.append("predictions = model.predict(x_test)")
            code.append("\n")
            code.append("classification_report(y_test, predictions)")
            code.append("\n")
            code.append("confusion_matrix(y_test, predictions)")

      
            ml4d.knn['filename']= filename
            ml4d.knn['x']=list(x_cols)
            ml4d.knn['y']= y
            ml4d.knn['Report'] = report
            ml4d.knn['Confusion matrix'] = list(confusion)
            ml4d.knn['Score'] = knn.score(x_test,y_test)
            ml4d.knn['Accuracy score'] = accuracy_score(y_test, predictions)

            data_result = pd.DataFrame({"Actual":y_test, "Predicted":predictions})
            ml4d.knn['Real test values'] = list(data_result.Actual.head(10))
            ml4d.knn['Predicted values'] = list(data_result.Predicted.head(10))
            ml4d.knn['Python'] = "".join(code)
            ml4d.knn['Confusion matrix plot']= True

            '''
            ---------------------------------------------------------------------------
            Decision Tree classifier
            ---------------------------------------------------------------------------
            '''
            tree = DecisionTreeClassifier(criterion='gini', splitter='best', max_depth=None, min_samples_split=2, min_samples_leaf=1, min_weight_fraction_leaf=0.0, max_features=None, random_state=None, max_leaf_nodes=None, min_impurity_decrease=0.0, min_impurity_split=None, class_weight=None, presort='deprecated', ccp_alpha=0.0)
            tree.fit(x_train,y_train)
            predictions = tree.predict(x_test)

            report = classification_report(y_test, predictions)
            confusion = confusion_matrix(y_test, predictions)
            data_compare = pd.DataFrame({"Actual":y_test, "Predicted":predictions})

            figure()
            width=10
            height=4
            figure(figsize=(width,height))

            confusion_columns=[]
            confusion_index=[]
            for variable in labels:
                confusion_columns.append("Predicted:"+str(variable))
                confusion_index.append("Actual:"+str(variable))
            conf_matrix = pd.DataFrame(data=confusion,columns=confusion_columns,index=confusion_index)
            sn.heatmap(conf_matrix, annot=True,  fmt='d',cmap="YlGnBu")
            image_name = "static/images/tree.png"
            plt.savefig(image_name)

            code = []
            code.append("import numpy as np")
            code.append("\n")
            code.append("from sklearn.metrics import classification_report, confusion_matrix")
            code.append("\n")
            code.append("from sklearn.model_selection import train_test_split")
            code.append("\n")
            code.append("from sklearn.tree import DecisionTreeClassifier")
            code.append("\n")
            code.append("dataframe = pd.read_csv('"+filename+"')")
            code.append("\n")
            code.append("df_x = dataframe["+str(x_cols)+"]")
            code.append("\n")
            code.append("df_y = dataframe['"+y+"']")
            code.append("\n")
            code.append("x_train, x_test, y_train, y_test = train_test_split(df_x,df_y,test_size=0.3,random_state=42)")
            code.append("\n")
            code.append("model = DecisionTreeClassifier(criterion='gini', splitter='best', max_depth=None, min_samples_split=2, min_samples_leaf=1, min_weight_fraction_leaf=0.0, max_features=None, random_state=None, max_leaf_nodes=None, min_impurity_decrease=0.0, min_impurity_split=None, class_weight=None, presort='deprecated', ccp_alpha=0.0)")
            code.append("\n")
            code.append("model.fit(x_train,y_train)")
            code.append("\n")
            code.append("predictions = model.predict(x_test)")
            code.append("\n")
            code.append("classification_report(y_test, predictions)")
            code.append("\n")
            code.append("confusion_matrix(y_test, predictions)")

            ml4d.tree['filename']= filename
            ml4d.tree['x']=list(x_cols)
            ml4d.tree['y']= y
            ml4d.tree['Report'] = report
            ml4d.tree['Confusion matrix'] = list(confusion)
            ml4d.tree['Score'] = tree.score(x_test,y_test)
            ml4d.tree['Accuracy score'] = accuracy_score(y_test, predictions)
            ml4d.tree['Real test values'] = list(data_compare.Actual.head(10))
            ml4d.tree['Predicted values'] = list(data_compare.Predicted.head(10))
            ml4d.tree['Python'] = "".join(code)
            ml4d.tree['Confusion matrix plot']= True

            '''
            ---------------------------------------------------------------------------
            RandomForest Classifier
            ---------------------------------------------------------------------------
            '''
            randomf = RandomForestClassifier(n_estimators=50, criterion='gini', max_depth=None, min_samples_split=2, min_samples_leaf=1, min_weight_fraction_leaf=0.0, max_features='auto', max_leaf_nodes=None, min_impurity_decrease=0.0, min_impurity_split=None, bootstrap=True, oob_score=False, n_jobs=None, random_state=None, verbose=1, warm_start=False, class_weight=None, ccp_alpha=0.0, max_samples=None)
            randomf.fit(x_train,y_train)
            predictions = randomf.predict(x_test)

            report = classification_report(y_test, predictions)
            confusion = confusion_matrix(y_test, predictions)
            data_compare = pd.DataFrame({"Actual":y_test, "Predicted":predictions})

            importances = randomf.feature_importances_
            indices = np.argsort(importances)

            features = x_train.columns

            figure()
            width=10
            height=4
            figure(figsize=(width,height))

            confusion_columns=[]
            confusion_index=[]
            for variable in labels:
                confusion_columns.append("Predicted:"+str(variable))
                confusion_index.append("Actual:"+str(variable))
            conf_matrix = pd.DataFrame(data=confusion,columns=confusion_columns,index=confusion_index)
            sn.heatmap(conf_matrix, annot=True,  fmt='d',cmap="YlGnBu")
            image_name = "static/images/randomf.png"
            plt.savefig(image_name)

            code = []
            code.append("import numpy as np\n")
            code.append("\n")
            code.append("from sklearn.metrics import classification_report, confusion_matrix")
            code.append("\n")
            code.append("from sklearn.model_selection import train_test_split")
            code.append("\n")
            code.append("from sklearn.ensemble import RandomForestClassifier")
            code.append("\n")
            code.append("dataframe = pd.read_csv('"+filename+"')")
            code.append("\n")
            code.append("df_x = dataframe["+str(x_cols)+"]")
            code.append("\n")
            code.append("df_y = dataframe['"+y+"']")
            code.append("\n")
            code.append("x_train, x_test, y_train, y_test = train_test_split(df_x,df_y,test_size=0.3,random_state=42)")
            code.append("\n")
            code.append("model = RandomForestClassifier(n_estimators=50, criterion='gini', max_depth=None, min_samples_split=2, min_samples_leaf=1, min_weight_fraction_leaf=0.0, max_features='auto', max_leaf_nodes=None, min_impurity_decrease=0.0, min_impurity_split=None, bootstrap=True, oob_score=False, n_jobs=None, random_state=None, verbose=1, warm_start=False, class_weight=None, ccp_alpha=0.0, max_samples=None)")
            code.append("\n")
            code.append("model.fit(x_train,y_train)")
            code.append("\n")
            code.append("predictions = model.predict(x_test)")
            code.append("\n")
            code.append("classification_report(y_test, predictions)")
            code.append("\n")
            code.append("confusion_matrix(y_test, predictions)")

            ml4d.randomf['filename']= filename
            ml4d.randomf['x']=list(x_cols)
            ml4d.randomf['y']= y
            ml4d.randomf['N_estimators'] = 80
            ml4d.randomf['Report'] = report
            ml4d.randomf['Confusion matrix'] = list(confusion)
            ml4d.randomf['Score'] = randomf.score(x_test,y_test)
            ml4d.randomf['Accuracy score'] = accuracy_score(y_test, predictions)
            ml4d.randomf['Real test values'] = list(data_compare.Actual.head(10))
            ml4d.randomf['Predicted values'] = list(data_compare.Predicted.head(10))
            ml4d.randomf['Python'] = "".join(code)
            ml4d.randomf['Confusion matrix plot']= True


            '''
            ---------------------------------------------------------------------------
            Suport Vector MAchine Classifier
            ---------------------------------------------------------------------------
            '''
            svc = SVC(C=1.0, kernel='rbf', degree=3, gamma='scale', coef0=0.0, shrinking=True, probability=False, tol=0.001, cache_size=200, class_weight=None, verbose=True, max_iter=-1, decision_function_shape='ovr', break_ties=False, random_state=None)
            svc.fit(x_train,y_train)
            predictions = svc.predict(x_test)

            report = classification_report(y_test, predictions)
            confusion = confusion_matrix(y_test, predictions)
            data_compare = pd.DataFrame({"Actual":y_test, "Predicted":predictions})

            figure()
            width=10
            height=4
            figure(figsize=(width,height))

            confusion_columns=[]
            confusion_index=[]
            for variable in labels:
                confusion_columns.append("Predicted:"+str(variable))
                confusion_index.append("Actual:"+str(variable))
            conf_matrix = pd.DataFrame(data=confusion,columns=confusion_columns,index=confusion_index)
            sn.heatmap(conf_matrix, annot=True,  fmt='d',cmap="YlGnBu")
            image_name = "static/images/svc.png"
            plt.savefig(image_name)

            code = []
            code.append("import numpy as np")
            code.append("\n")
            code.append("from sklearn.metrics import classification_report, confusion_matrix")
            code.append("\n")
            code.append("from sklearn.model_selection import train_test_split")
            code.append("\n")
            code.append("from sklearn.svm import SVC")
            code.append("\n")
            code.append("dataframe = pd.read_csv('"+filename+"')")
            code.append("\n")
            code.append("df_x = dataframe["+str(x_cols)+"]")
            code.append("\n")
            code.append("df_y = dataframe['"+y+"']")
            code.append("\n")
            code.append("x_train, x_test, y_train, y_test = train_test_split(df_x,df_y,test_size=0.3,random_state=42)")
            code.append("\n")
            code.append("model = SVC(C=1.0, kernel='rbf', degree=3, gamma='scale', coef0=0.0, shrinking=True, probability=False, tol=0.001, cache_size=200, class_weight=None, verbose=True, max_iter=-1, decision_function_shape='ovr', break_ties=False, random_state=None)")
            code.append("\n")
            code.append("model.fit(x_train,y_train)")
            code.append("\n")
            code.append("predictions = model.predict(x_test)")
            code.append("\n")
            code.append("classification_report(y_test, predictions)")
            code.append("\n")
            code.append("confusion_matrix(y_test, predictions)")

            ml4d.svc['filename']= filename
            ml4d.svc['x']=list(x_cols)
            ml4d.svc['y']= y
            ml4d.svc['Gamma'] = "auto"
            ml4d.svc['Report'] = report
            ml4d.svc['Confusion matrix'] = list(confusion)
            ml4d.svc['Score'] = svc.score(x_test,y_test)
            ml4d.svc['Accuracy score'] = accuracy_score(y_test, predictions)
            ml4d.svc['Real test values'] = list(data_compare.Actual.head(10))
            ml4d.svc['Predicted values'] = list(data_compare.Predicted.head(10))
            ml4d.svc['Python'] = "".join(code)
            ml4d.svc['Confusion matrix plot']= True

            raise web.seeother('/compare_r')
        except Exception as e:
            print(e.args)
            return render.error(e.args[0])
