from django.db import models
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from django.contrib.auth.models import User as DjangoUser
from dotenv import load_dotenv
load_dotenv()
import psycopg2
import os

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
    def __str__(self):
        return self.user.username

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

from django.db.models.signals import post_save
post_save.connect(create_user_profile, sender=DjangoUser)

def load_model(model_name='src\projet_annuel\script python\sleep_disorder_model.joblib'):
    return joblib.load(model_name)

def load_label_encoders(encoder_name='src\projet_annuel\script python\label_encoders.joblib'):
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
    prediction = model.predict([features])
    return prediction[0]

class User(models.Model):
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
        user = None
        try:
            user = DjangoUser.objects.get(email=mail)
            if user.check_password(password):
                print("Connexion réussie !")
                return user
            else:
                print("Mot de passe incorrect !")
        except DjangoUser.DoesNotExist:
            print("Utilisateur non trouvé !")
        except Exception as error:
            print("Erreur lors de la connexion de l'utilisateur :", error)
        return user
    
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
