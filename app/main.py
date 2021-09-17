from flask import Flask, request, render_template
import pickle
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15")
app = Flask(__name__, template_folder='./static/templates')
columns = ['title', 'year', 'mileage', 'engine_capacity', 'hp', 'fuel_type', 'gearbox', 'carbody', 'city', 'transmission', 'color']
cols = ['wallsMaterial', 'floorNumber', 'floorsTotal', 'totalArea', 'kitchenArea', 'latitude', 'longitude']
model = pickle.load(open('app/static/model/finalized_model.sav', 'rb'))
model_houses = pickle.load(open('app/static/model/finalized_model_houses.sav', 'rb'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/prediction_auto', methods=['POST'])
def prediction_auto():
    print(request.form.values())

    init_features = [x for x in request.form.values()]
    print(init_features)

    final = list(map(float, init_features[:12]))
    df = pd.DataFrame([final], columns = columns)

    prediction = f"{np.round(np.e**model.predict(df))}".replace('[', '').replace(']', '') + ' рублей'

    return render_template('result.html', pred=f'{prediction}')

@app.route('/prediction_house', methods=['POST'])
def prediction_house():
    print(request.form.values())

    init_features = [x for x in request.form.values()]
    location = geolocator.geocode(init_features[-1])
    init_features = init_features[:-1]
    init_features.append(f"{location.latitude}")
    init_features.append(f"{location.longitude}")
    print(init_features)
    print(len(init_features))

    final = list(map(float, init_features[:7]))
    df = pd.DataFrame([final], columns = cols)
    
    print(df)
    print('---------------')
    prediction = f"{np.round(np.e**model_houses.predict(df))}".replace('[', '').replace(']', '') + ' рублей'

    return render_template('result.html', pred=f'{prediction}')
