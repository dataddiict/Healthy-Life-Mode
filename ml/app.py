from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pickle
import numpy as np
import pandas as pd

app = Flask(__name__)
CORS(app)

# ----------------- Charger les modèles -----------------
model_sleep = joblib.load('models/sleep_disorder_model.joblib')
model_obesity = pickle.load(open('models/obesity_model.pkl', 'rb'))
model_stress = joblib.load('models/stress_model.pkl')


# ----------------- Preprocessing pour chaque modèle -----------------
def preprocess_sleep(data):
    try:
        features = [
            data.get('sleep_quality', 0),
            data.get('physical_activity', 0),
            data.get('stress_level', 0),
            data.get('steps', 0),
            data.get('sleep_duration', 0),
            data.get('age', 0)
        ]
        return np.array(features).reshape(1, -1)
    except Exception as e:
        print("Erreur preprocessing sleep:", e)
        return None

def preprocess_obesity(data):
    try:
        features = [
            data.get('weight', 0),
            data.get('height', 0),
            data.get('age', 0),
            data.get('ch2o', 0),
            data.get('fcvc', 0),
            data.get('ncp', 0)
        ]
        df = pd.DataFrame([features], columns=['weight', 'height', 'age', 'ch2o', 'fcvc', 'ncp'])
        preprocessor = model_obesity.named_steps['preprocessor']
        transformed = preprocessor.transform(df)
        return transformed
    except Exception as e:
        print("Erreur preprocessing obesity:", e)
        return None

def preprocess_stress(data):
    try:
        mapping = {
            'Days_Indoors': {'1-14 days': 0, '15-30 days': 1, '31-60 days': 2, 'More than 60 days': 3},
            'Changes_Habits': {'Yes': 0, 'No': 1, 'Maybe': 2},
            'Work_Interest': {'Yes': 0, 'No': 1},
            'Social_Weakness': {'Yes': 0, 'No': 1, 'Maybe': 2},
            'Mental_Health_History': {'Yes': 0, 'No': 1, 'Maybe': 2},
            'sexe': {'M': 0, 'F': 1}
        }
        features = [
            mapping['Days_Indoors'].get(data.get('Days_Indoors', '1-14 days'), 0),
            mapping['Changes_Habits'].get(data.get('Changes_Habits', 'No'), 1),
            mapping['Work_Interest'].get(data.get('Work_Interest', 'No'), 1),
            mapping['Social_Weakness'].get(data.get('Social_Weakness', 'No'), 1),
            mapping['Mental_Health_History'].get(data.get('Mental_Health_History', 'No'), 1),
            mapping['sexe'].get(data.get('sexe', 'M'), 0)
        ]
        return np.array(features).reshape(1, -1)
    except Exception as e:
        print("Erreur preprocessing stress:", e)
        return None


# ----------------- Endpoints -----------------
@app.route('/predict_sleep', methods=['POST'])
def predict_sleep():
    data = request.json
    features = preprocess_sleep(data)
    if features is None:
        return jsonify({'error': 'Invalid data'}), 400
    prediction = model_sleep.predict(features)[0]
    return jsonify({'prediction': int(prediction)})

@app.route('/predict_obesity', methods=['POST'])
def predict_obesity():
    data = request.json
    features = preprocess_obesity(data)
    if features is None:
        return jsonify({'error': 'Invalid data'}), 400
    prediction_num = model_obesity.named_steps['classifier'].predict(features)[0]
    return jsonify({'prediction': int(prediction_num)})

@app.route('/predict_stress', methods=['POST'])
def predict_stress():
    data = request.json
    features = preprocess_stress(data)
    if features is None:
        return jsonify({'error': 'Invalid data'}), 400
    prediction = model_stress.predict(features)[0]
    return jsonify({'prediction': int(prediction)})

# ----------------- Lancement du serveur -----------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)