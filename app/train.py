from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier

import glob
import pickle
# import csv
import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns
import numpy as np

#import statsmodels.api as sm
#from statsmodels.stats.outliers_influence import variance_inflation_factor

PATH = './static/csv/'

def get_csv_files(path_dir):
    return glob.iglob(f"{path_dir}*.csv", recursive=False)

last = ''
csvName = get_csv_files(PATH)
for filE in csvName:
    last = filE
#%matplotlib inline

#2021-09-15_13:45:21.251410_cars.csv
# csvfile = open('2021-09-15_13:45:21.251410_cars.csv', encoding='utf8')
# reader = csv.reader(csvfile, delimiter=';')
columns = ['title', 'rub_price', 'year', 'mileage', 'engine_capacity', 'hp', 'fuel_type', 'gearbox', 'carbody', 'city', 'transmission', 'color']
# data = pd.DataFrame(data=csvfile, columns=columns)
data = pd.read_csv(last, usecols=columns, sep=';')
# data.head() # some top data
df = pd.DataFrame(data.dropna(), columns=columns)

prices = np.log(df['rub_price'])
features = df.drop('rub_price', axis=1)

xtr, xte, ytr, yte = train_test_split(features, prices, test_size=0.2, random_state=10)


MODEL_NAME = './static/model/finalized_model.sav'
regr = pickle.load(open(MODEL_NAME, 'rb'))

regr.fit(xtr, ytr)
print("training data r-squared: ", regr.score(xtr, ytr))
print("test data r-squared: ", regr.score(xte, yte))

print('intercept ', regr.intercept_)
pd.DataFrame(data=regr.coef_, index=xtr.columns, columns=['coef'])

pickle.dump(regr, open(MODEL_NAME, 'wb'))
