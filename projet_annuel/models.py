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
    family_history_with_overweight = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')], null=True, blank=True)
    favc = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')], null=True, blank=True)
    caec = models.CharField(max_length=10, choices=[('no', 'No'), ('Sometimes', 'Sometimes'), ('Frequently', 'Frequently'), ('Always', 'Always')], null=True, blank=True)
    smoke = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')], null=True, blank=True)
    scc = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')], null=True, blank=True)
    calc = models.CharField(max_length=10, choices=[('no', 'No'), ('Sometimes', 'Sometimes'), ('Frequently', 'Frequently'), ('Always', 'Always')], null=True, blank=True)
    mtrans = models.CharField(max_length=21, choices=[('Walking', 'Walking'), ('Bike', 'Bike'), ('Public_Transportation', 'Public_Transportation'), ('Automobile', 'Automobile')], null=True, blank=True)
    faf = models.FloatField(null=True, blank=True)
    tue = models.FloatField(null=True, blank=True)
    ch2o = models.FloatField(null=True, blank=True)
    fcvc = models.FloatField(null=True, blank=True)
    ncp = models.FloatField(null=True, blank=True)
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    @classmethod
    def update_user_django(cls, mail, password, first_name, last_name, username):
        try:
            user = User.objects.get(email=mail)
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
    family_history_with_overweight = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')], null=True, blank=True)
    favc = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')], null=True, blank=True)
    caec = models.CharField(max_length=10, choices=[('no', 'No'), ('Sometimes', 'Sometimes'), ('Frequently', 'Frequently'), ('Always', 'Always')], null=True, blank=True)
    smoke = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')], null=True, blank=True)
    scc = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')], null=True, blank=True)
    calc = models.CharField(max_length=10, choices=[('no', 'No'), ('Sometimes', 'Sometimes'), ('Frequently', 'Frequently'), ('Always', 'Always')], null=True, blank=True)
    mtrans = models.CharField(max_length=21, choices=[('Walking', 'Walking'), ('Bike', 'Bike'), ('Public_Transportation', 'Public_Transportation'), ('Automobile', 'Automobile')], null=True, blank=True)
    faf = models.FloatField(null=True, blank=True)
    tue = models.FloatField(null=True, blank=True)
    ch2o = models.FloatField(null=True, blank=True)
    fcvc = models.FloatField(null=True, blank=True)
    ncp = models.FloatField(null=True, blank=True)    
    def __str__(self):
        return self.user.username

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

from django.db.models.signals import post_save
post_save.connect(create_user_profile, sender=DjangoUser)

def load_model(model_name=model_sleep_path):
    return joblib.load(model_name)

def load_label_encoders(encoder_name=model_sleep_path_encode):
    return joblib.load(encoder_name)


def load_label_encoders():
    # Placeholder function to simulate loading pre-fitted label encoders
    # Replace with your actual loading mechanism
    encoders = {
        'Gender': LabelEncoder().fit(['Male', 'Female']),
        'BMI Category': LabelEncoder().fit(['Underweight', 'Normal', 'Overweight', 'Obese']),
        'Sleep Duration Category': LabelEncoder().fit(['Très court', 'Court', 'Normal', 'Long']),
        'Age Category': LabelEncoder().fit(['Enfant', 'Jeune adulte', 'Adulte', 'Senior', 'Super Senior'])
    }
    return encoders

def preprocess_user_data(user_profile):
    # Calculer le BMI
    bmi = user_profile.weight / (user_profile.height / 100) ** 2
    if bmi < 18.5:
        bmi_category = 'Underweight'
    elif 18.5 <= bmi < 25:
        bmi_category = 'Normal'
    elif 25 <= bmi < 30:
        bmi_category = 'Overweight'
    else:
        bmi_category = 'Obese'

    # Créer un DataFrame avec les données utilisateur
    data = {
        'Gender': [user_profile.sexe],
        'Quality of Sleep': [user_profile.sleep_quality],
        'Physical Activity Level': [user_profile.physical_activity],
        'Stress Level': [user_profile.stress_level],
        'BMI Category': [bmi_category],
        'Daily Steps': [user_profile.steps],
        'Sleep Duration': [user_profile.sleep_duration],
        'Heart Rate': [70],  # Placeholder - ajouter le champ si nécessaire
        'Age': [user_profile.age],
    }
    df = pd.DataFrame(data)

    # Appliquer les transformations comme dans le notebook
    heart_rate_bins = [0, 60, 80, 100, float('inf')]
    heart_rate_labels = ['Faible', 'Modéré', 'Élevé', 'Très élevé']
    df['Heart Rate Category'] = pd.cut(df['Heart Rate'], bins=heart_rate_bins, labels=heart_rate_labels)

    sleep_duration_bins = [0, 5, 7, 9, float('inf')]
    sleep_duration_labels = ['Très court', 'Court', 'Normal', 'Long']
    df['Sleep Duration Category'] = pd.cut(df['Sleep Duration'], bins=sleep_duration_bins, labels=sleep_duration_labels)

    age_bins = [0, 18, 30, 50, 70, float('inf')]
    age_labels = ['Enfant', 'Jeune adulte', 'Adulte', 'Senior', 'Super Senior']
    df['Age Category'] = pd.cut(df['Age'], bins=age_bins, labels=age_labels)

    df.drop(columns=['Sleep Duration', 'Heart Rate', 'Age', 'Heart Rate Category'], inplace=True)

    # Charger les encodeurs
    label_encoders = load_label_encoders()

    # Assurez-vous que les valeurs sont cohérentes avec celles utilisées pendant l'entraînement
    for col in ['Gender', 'BMI Category', 'Sleep Duration Category', 'Age Category']:
        df[col] = df[col].apply(lambda x: label_encoders[col].transform([x])[0] if x in label_encoders[col].classes_ else -1)

    # Réorganiser les colonnes pour correspondre à l'ordre de l'entraînement
    final_columns = ['Gender', 'Quality of Sleep', 'Physical Activity Level', 'Stress Level',
                     'BMI Category', 'Daily Steps', 'Sleep Duration Category', 'Age Category']
    df = df[final_columns]

    return df.values[0]

def predict_sleep_disorder(user_id):
    model = load_model()
    feature_names = model.feature_names_in_
    print(feature_names)
    # Récupérer l'utilisateur et son profil
    user_profile = UserProfile.objects.get(user_id=user_id)
    
    # Prétraiter les données utilisateur
    features = preprocess_user_data(user_profile)
    
    # Faire la prédiction
    prediction = model.predict([features])[0]
    
    # Enregistrer les données dans FollowDataUser
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
    
    return prediction

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
    family_history_with_overweight = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')], null=True, blank=True)
    favc = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')], null=True, blank=True)
    caec = models.CharField(max_length=10, choices=[('no', 'No'), ('Sometimes', 'Sometimes'), ('Frequently', 'Frequently'), ('Always', 'Always')], null=True, blank=True)
    smoke = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')], null=True, blank=True)
    scc = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')], null=True, blank=True)
    calc = models.CharField(max_length=10, choices=[('no', 'No'), ('Sometimes', 'Sometimes'), ('Frequently', 'Frequently'), ('Always', 'Always')], null=True, blank=True)
    mtrans = models.CharField(max_length=21, choices=[('Walking', 'Walking'), ('Bike', 'Bike'), ('Public_Transportation', 'Public_Transportation'), ('Automobile', 'Automobile')], null=True, blank=True)
    faf = models.FloatField(null=True, blank=True)
    tue = models.FloatField(null=True, blank=True)
    ch2o = models.FloatField(null=True, blank=True)
    fcvc = models.FloatField(null=True, blank=True)
    ncp = models.FloatField(null=True, blank=True)
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
        'family_history_with_overweight': [user_profile.family_history_with_overweight],
        'FAVC': [user_profile.favc],
        'CAEC': [user_profile.caec],
        'SMOKE': [user_profile.smoke],
        'SCC': [user_profile.scc],
        'CALC': [user_profile.calc],
        'MTRANS': [user_profile.mtrans],
        'FAF': [user_profile.faf],
        'TUE': [user_profile.tue],
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
    categorical_features = ['Gender', 'family_history_with_overweight', 'FAVC', 'CAEC', 'SMOKE', 'SCC', 'CALC', 'MTRANS']
    numeric_features = ['FAF', 'TUE', 'CH2O', 'FCVC', 'NCP', 'Age', 'Height', 'Weight']

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
    
    # Save prediction to database
    ObesityPrediction.objects.create(user=user_profile.user, prediction=prediction_label)
    print(prediction_num)
    return prediction_num