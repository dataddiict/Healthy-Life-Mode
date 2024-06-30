import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

# Function to save models
def save_model(model, model_name):
    joblib.dump(model, f'{model_name}.joblib')
    print(f'Model {model_name} saved successfully.')

def load_model(model_name):
    return joblib.load(f'{model_name}.joblib')

# Data processing function
def process_data(file_path):
    data = pd.read_csv(file_path)

    # Split Blood Pressure into Systolic and Diastolic
    data[['Systolic_BP', 'Diastolic_BP']] = data['Blood Pressure'].str.split('/', expand=True)
    data['BMI Category'] = data['BMI Category'].replace('Normal Weight', 'Normal')
    data.drop(columns=['Person ID', 'Blood Pressure', 'Systolic_BP', 'Diastolic_BP', 'Occupation', 'Heart Rate'], inplace=True)
    
    # Map categorical values to numerical values
    gender_map = {'Male': 0, 'Female': 1}
    bmi_category_map = {'Underweight': 0, 'Normal': 1, 'Overweight': 2, 'Obese': 3}
    sleep_disorder_map = {'None': 0, 'Sleep Apnea': 1, 'Insomnia': 2}

    data['Gender'] = data['Gender'].map(gender_map)
    data['BMI Category'] = data['BMI Category'].map(bmi_category_map)
    data['Sleep Disorder'] = data['Sleep Disorder'].map(sleep_disorder_map)
    
    # Bin age into categories
    age_bins = [0, 18, 30, 50, 70, float('inf')]
    age_labels = [0, 1, 2, 3, 4]  # Numeric labels for age categories
    data['Age Category'] = pd.cut(data['Age'], bins=age_bins, labels=age_labels).astype(int)
    
    data.drop(columns=['Age'], inplace=True)
    
    # Drop rows with missing target values
    data.dropna(subset=['Sleep Disorder'], inplace=True)

    return data

# Function to train the model
def train_model(data):
    X = data.drop(columns=['Sleep Disorder'])
    y = data['Sleep Disorder']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    clf = RandomForestClassifier()
    clf.fit(X_train, y_train)
    
    y_pred = clf.predict(X_test)
    print("0: Pas de trouble du sommeil\n1: Apnée du sommeil\n2: Insomnie")
    print(classification_report(y_test, y_pred))
    
    # Save the model
    save_model(clf, 'sleep_disorder_model')

    print("feature", X.columns)
# Main function to process data and train model
def main():
    file_path = 'Sleep_health_and_lifestyle_dataset.csv'
    data = process_data(file_path)
    train_model(data)

if __name__ == "__main__":
    main()
