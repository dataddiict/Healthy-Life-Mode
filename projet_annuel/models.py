from django.db import models
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from django.contrib.auth.models import User as DjangoUser
from django import forms
from django.contrib.auth.models import User
from django.conf import settings
from dotenv import load_dotenv
load_dotenv()
import psycopg2
import os
import pickle
from django.shortcuts import get_object_or_404
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

model_sleep_path = settings.MODEL_SLEEP_PATH
model_sleep_path_encode = settings.MODEL_SLEEP_PATH_ENCODE
model_obesity_path = settings.MODEL_OBESITY_PATH
model_obesity_path_encode = settings.MODEL_OBESITY_PATH_ENCODE
model_obesity_path_preprocess = settings.MODEL_OBESITY_PATH_PREPROCESS
model_stress_path = settings.MODEL_STRESS_PATH
model_stress_path_params = settings.MODEL_STRESS_PATH_PARAMS
model_stress_path_features = settings.MODEL_STRESS_PATH_FEATURES

class FollowDataUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    age = models.IntegerField(null=True, blank=True)
    sexe = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')], null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    weight = models.IntegerField(null=True, blank=True)
    steps = models.IntegerField(null=True, blank=True)
    sleep_quality = models.IntegerField(null=True, blank=True)
    sleep_duration = models.IntegerField(null=True, blank=True)
    physical_activity = models.IntegerField(null=True, blank=True)
    stress_level = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    ch2o = models.FloatField(null=True, blank=True)
    fcvc = models.FloatField(null=True, blank=True)
    ncp = models.FloatField(null=True, blank=True)
    Days_Indoors = models.CharField(max_length=20, null=True, blank=True)
    Changes_Habits = models.CharField(max_length=10, null=True, blank=True)
    Work_Interest = models.CharField(max_length=10, null=True, blank=True)
    Social_Weakness = models.CharField(max_length=10, null=True, blank=True)
    Mental_Health_History = models.CharField(max_length=10, null=True, blank=True)

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    
def get_user_by_id(user_id):
    try:
        # get all information of the user
        user = UserProfile.objects.get(id=user_id)
        return user
    except User.DoesNotExist:
        print("Utilisateur non trouvé !")
        return None
def update_Last_Prediction_text(user_id, text,sleep,obesity,stress):
    try:
        user = UserProfile.objects.get(user_id=user_id)
        user.Last_Prediction_text = text
        user.Last_sleep_prediction = sleep
        user.Last_obesity_prediction = obesity
        user.Last_stress_prediction = stress
        user.save()
        print("Texte de dernière prédiction mis à jour avec succès !")
        return user
    except Exception as error:
        print("Erreur lors de la mise à jour du texte de dernière prédiction :", error)
        return None

class UserProfile(models.Model):
    user = models.OneToOneField(DjangoUser, on_delete=models.CASCADE)
    age = models.IntegerField(null=True, blank=True)
    sexe = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')], null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    weight = models.IntegerField(null=True, blank=True)
    steps = models.IntegerField(null=True, blank=True)
    sleep_quality = models.IntegerField(null=True, blank=True)
    sleep_duration = models.FloatField(null=True, blank=True)
    stress_level = models.IntegerField(null=True, blank=True)
    physical_activity = models.IntegerField(null=True, blank=True)
    ch2o = models.FloatField(null=True, blank=True)
    fcvc = models.FloatField(null=True, blank=True)
    ncp = models.FloatField(null=True, blank=True)
    Days_Indoors = models.CharField(max_length=20, null=True, blank=True)
    Changes_Habits = models.CharField(max_length=10, null=True, blank=True)
    Work_Interest = models.CharField(max_length=10, null=True, blank=True)
    Social_Weakness = models.CharField(max_length=10, null=True, blank=True)
    Mental_Health_History = models.CharField(max_length=10, null=True, blank=True)
    Last_Prediction_text = models.CharField(max_length=10000, null=True, blank=True)
    Last_sleep_prediction = models.CharField(max_length=1000, null=True, blank=True)
    Last_obesity_prediction = models.CharField(max_length=1000, null=True, blank=True)
    Last_stress_prediction = models.CharField(max_length=1000, null=True, blank=True)
    def __str__(self):
        return self.user.username
    
    @classmethod
    def get_user_profile(cls, user_id):
        try:
            user_profile = UserProfile.objects.get(user_id=user_id)
            return user_profile
        except Exception as error:
            print("Erreur lors de la récupération du profil de l'utilisateur :", error)
            return None

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


from django.db.models.signals import post_save
post_save.connect(create_user_profile, sender=DjangoUser)


class User_User(models.Model):
    pseudo = models.CharField(max_length=100)
    mail = models.EmailField(max_length=255)
    password = models.CharField(max_length=255)
    age = models.IntegerField(null=True, blank=True)
    sexe = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')], null=True, blank=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    weight = models.IntegerField(null=True, blank=True)
    steps = models.IntegerField(null=True, blank=True)
    sleep_quality = models.IntegerField(null=True, blank=True)
    sleep_duration = models.IntegerField(null=True, blank=True)
    stress_level = models.IntegerField(null=True, blank=True)
    physical_activity = models.IntegerField(null=True, blank=True)
    ch2o = models.FloatField(null=True, blank=True)
    fcvc = models.FloatField(null=True, blank=True)
    ncp = models.FloatField(null=True, blank=True)
    Days_Indoors = models.CharField(max_length=20, null=True, blank=True)
    Changes_Habits = models.CharField(max_length=10, null=True, blank=True)
    Work_Interest = models.CharField(max_length=10, null=True, blank=True)
    Social_Weakness = models.CharField(max_length=10, null=True, blank=True)
    Mental_Health_History = models.CharField(max_length=10, null=True, blank=True)
    @classmethod
    def create_user(cls, mail, password, first_name, last_name, username):
        try:
            user = DjangoUser.objects.create_user(username=username, email=mail, password=password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            print("Utilisateur créé avec succès !")
            return user
        except Exception as error:
            print("Erreur lors de la création de l'utilisateur :", error)
            return None
    
    @classmethod
    def user_login(cls, mail, password):
        try:
            user = DjangoUser.objects.get(email=mail)
            if user.check_password(password):
                print("Connexion réussie !")
                return user
            else:
                print("Mot de passe incorrect !")
                return None
        except DjangoUser.DoesNotExist:
            print("Utilisateur non trouvé !")
            return None
        except Exception as error:
            print("Erreur lors de la connexion de l'utilisateur :", error)
            return None

    
    @classmethod
    def update_django_user(cls, mail, password, first_name, last_name, username):
        try:
            user = DjangoUser.objects.get(email=mail)
            user.username = username
            user.email = mail
            user.set_password(password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            print("Utilisateur mis à jour avec succès !")
            return user
        except Exception as error:
            print("Erreur lors de la mise à jour de l'utilisateur :", error)
            return None
    @classmethod    
    def update_user(cls, mail, password, first_name, last_name, username, age, sexe, height, weight, steps, sleep_quality, sleep_duration, physical_activity, stress_level):
        try:
            user = DjangoUser.objects.get(email=mail)
            user.username = username
            user.email = mail
            user.set_password(password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            conn = psycopg2.connect(
                dbname=os.environ.get('DB_NAME'),
                user=os.environ.get('DB_USER'),
                password=os.environ.get('DB_PASSWORD'),
                host=os.environ.get('DB_HOST'),
                port=os.environ.get('DB_PORT')
            )
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE auth_user SET age = {age}, sexe = '{sexe}', height = {height}, weight = {weight}, steps = {steps}, sleep_quality = {sleep_quality}, sleep_duration = {sleep_duration}, physical_activity = {physical_activity}, stress_level = {stress_level} WHERE id = {user.id}"
            )
            conn.commit()
            cursor.close()
            conn.close()

            print("Utilisateur mis à jour avec succès !")
            return user
        except Exception as error:
            print("Erreur lors de la mise à jour de l'utilisateur :", error)
            return None
        

class Image(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/')

    def __str__(self):
        return self.title
    
class Service(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='services/')

    def __str__(self):
        return self.title
    
def getunbr_user():
    conn = psycopg2.connect(
        dbname=os.environ.get('DB_NAME'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        host=os.environ.get('DB_HOST'),
        port=os.environ.get('DB_PORT')
    )
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM auth_user")
    unbr_user = cursor.fetchone()
    cursor.close()
    conn.close()
    return unbr_user[0]


#_______________________________________________________________________________________________________________________


class ObesityPrediction(models.Model):
    user = models.ForeignKey(DjangoUser, on_delete=models.CASCADE)
    prediction = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

def load_model_obesity():
    with open(model_obesity_path, 'rb') as file:
        return pickle.load(file)
def load_label_encoder():
    with open(model_obesity_path_encode, 'rb') as file:
        return pickle.load(file)
def preprocess_user_data_ob(user_profile):
    # Step 1: Load User Data
    gender_map = {'M': 'Male', 'F': 'Female'}
    gender = gender_map.get(user_profile.sexe, user_profile.sexe)
    
    data = {
        'Gender': [gender],
        'CH2O': [user_profile.ch2o],
        'FCVC': [user_profile.fcvc],
        'NCP': [user_profile.ncp],
        'Age': [user_profile.age],
        'Height': [user_profile.height],
        'Weight': [user_profile.weight]
    }
    
    df = pd.DataFrame(data)
    print("Initial DataFrame:")
    print(df)

    # Step 2: Handle Missing Values
    categorical_features = ['Gender']
    numeric_features = ['CH2O', 'FCVC', 'NCP', 'Age', 'Height', 'Weight']

    # Define imputers
    categorical_imputer = SimpleImputer(strategy='constant', fill_value='Unknown')
    numeric_imputer = SimpleImputer(strategy='mean')

    # Apply imputations
    df[categorical_features] = categorical_imputer.fit_transform(df[categorical_features])
    df[numeric_features] = numeric_imputer.fit_transform(df[numeric_features])

    print("DataFrame after handling missing values:")
    print(df)

    # Load and apply preprocessor
    model = load_model_obesity()
    preprocessor = model.named_steps['preprocessor']
    df_transformed = preprocessor.transform(df)
    
    print("Transformed Data Shape:", df_transformed.shape)
    print("Transformed Data:")
    print(df_transformed)

    return df_transformed

def predict_obesity(user_id):
    model = load_model_obesity()
    label_encoder = load_label_encoder()
    user_profile = get_object_or_404(UserProfile, user_id=user_id)
    features = preprocess_user_data_ob(user_profile)
    
    # Ensure features is a 2D array
    if features.ndim == 1:
        features = features.reshape(1, -1)
    
    prediction_num = model.named_steps['classifier'].predict(features)[0]
    prediction_label = label_encoder.inverse_transform([prediction_num])[0]
    print("Obesity Prediction:", prediction_label)
    
    # print label and their numbers
    print("Label and their numbers:")
    for label, num in zip(label_encoder.classes_, range(len(label_encoder.classes_))):
        print(f"{label}: {num}")

    # Save prediction to database
    ObesityPrediction.objects.create(user=user_profile.user, prediction=prediction_label)
    print(prediction_num)
    
    return prediction_num


#_______________________________________________________________________________________________________________________


def load_model(model_name=model_sleep_path):
    return joblib.load(model_name)

def preprocess_user_data(user_profile):
    # Calculate BMI
    bmi = user_profile.weight / (user_profile.height / 100) ** 2
    if bmi < 18.5:
        bmi_category = 'Underweight'
    elif 18.5 <= bmi < 25:
        bmi_category = 'Normal'
    elif 25 <= bmi < 30:
        bmi_category = 'Overweight'
    else:
        bmi_category = 'Obese'

    # Map categorical values to numerical values
    gender_map = {'M': 0, 'F': 1}
    bmi_category_map = {'Underweight': 0, 'Normal': 1, 'Overweight': 2, 'Obese': 3}
    age_bins = [0, 18, 30, 50, 70, float('inf')]
    age_labels = [0, 1, 2, 3, 4]  # Numeric labels for age categories
    
    gender = gender_map.get(user_profile.sexe, -1)
    bmi_category = bmi_category_map.get(bmi_category, -1)
    age_category = pd.cut([user_profile.age], bins=age_bins, labels=age_labels).astype(int)[0]

    # Create a DataFrame with user data
    data = {
        'Gender': [gender],
        'Quality of Sleep': [user_profile.sleep_quality],
        'Physical Activity Level': [user_profile.physical_activity],
        'Stress Level': [user_profile.stress_level],
        'BMI Category': [bmi_category],
        'Daily Steps': [user_profile.steps],
        'Sleep Duration': [user_profile.sleep_duration],
        'Age': [user_profile.age]
    }
    df = pd.DataFrame(data)
    print(df)

    # Rearrange columns to match the order used in training
    final_columns = ['Gender', 'Quality of Sleep', 'Physical Activity Level', 'Stress Level',
                     'BMI Category', 'Daily Steps', 'Sleep Duration', 'Age']
    df = df[final_columns]
    return df.values[0]

def predict_sleep_disorder(user_id):
    model = load_model()
    user_profile = UserProfile.objects.get(user_id=user_id)
    # Save user data to FollowDataUser for history
    FollowDataUser.objects.create(
        user=user_profile.user,
        age=user_profile.age,
        sexe=user_profile.sexe,
        height=user_profile.height,
        weight=user_profile.weight,
        steps=user_profile.steps,
        sleep_quality=user_profile.sleep_quality,
        sleep_duration=user_profile.sleep_duration,
        physical_activity=user_profile.physical_activity,
        stress_level=user_profile.stress_level
    )
    features = preprocess_user_data(user_profile)
    prediction = model.predict([features])[0]
    return prediction
#_______________________________________________________________________________________________________________________

def load_model_stress():
    return joblib.load(model_stress_path)

def load_scaler_params():
    return joblib.load(model_stress_path_params)

def load_feature_names():
    return joblib.load(model_stress_path_features)

def transform_data(data):
    data['Days_Indoors'] = data['Days_Indoors'].map({'1-14 days': 0, '15-30 days': 1, '31-60 days': 2, 'More than 60 days': 3})
    data['Changes_Habits'] = data['Changes_Habits'].map({'Yes': 0, 'No': 1, 'Maybe': 2})
    data['Work_Interest'] = data['Work_Interest'].map({'Yes': 0, 'No': 1})
    data['Social_Weakness'] = data['Social_Weakness'].map({'Yes': 0, 'No': 1, 'Maybe': 2})
    data['Mental_Health_History'] = data['Mental_Health_History'].map({'Yes': 0, 'No': 1, 'Maybe': 2})
    data['Gender'] = data['Gender'].map({'Male': 0, 'Female': 1})

    return data

def manual_normalize(df, mean, std, numeric_features):
    df[numeric_features] = (df[numeric_features] - mean) / std
    return df

def preprocess_user_data_stress(user_profile):
    mean, std = load_scaler_params()
    feature_names = load_feature_names()
    gender_map = {'M': 'Male', 'F': 'Female'}
    gender = gender_map.get(user_profile.sexe, user_profile.sexe)
    
    data = {
        'Days_Indoors': [user_profile.Days_Indoors],
        'Changes_Habits': [user_profile.Changes_Habits],
        'Work_Interest': [user_profile.Work_Interest],
        'Social_Weakness': [user_profile.Social_Weakness],
        'Mental_Health_History': [user_profile.Mental_Health_History],
        'Gender': [gender]
    }

    df = pd.DataFrame(data)
    print("Initial DataFrame:")
    print(df)

    # Encoder manuellement les caractéristiques catégorielles
    df = transform_data(df)
    
    # Normaliser manuellement les caractéristiques numériques
    numeric_features = []  # Update this if there are numeric features
    df = manual_normalize(df, mean, std, numeric_features)

    # Ensure the DataFrame has the same columns in the same order as during training
    df = df[feature_names]
    
    print("Transformed Data Shape:", df.shape)
    print("Transformed Data:")
    print(df)

    return df

def predict_stress(user_id):
    model = load_model_stress()
    user_profile = get_object_or_404(UserProfile, user_id=user_id)
    features = preprocess_user_data_stress(user_profile)
    
    prediction_num = model.predict(features)[0]
    print("Stress Prediction:", prediction_num)
    
    return prediction_num