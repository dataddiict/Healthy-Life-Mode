from django.db import models
import os 
import psycopg2
from django.contrib.auth.models import User as DjangoUser
from dotenv import load_dotenv
load_dotenv()
from django.db import models
from django.contrib.auth.models import AbstractUser
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from dotenv import load_dotenv
load_dotenv()
import psycopg2
import os

class UserProfile(models.Model):
    user = models.OneToOneField(DjangoUser, on_delete=models.CASCADE)
    age = models.IntegerField(null=True, blank=True)
    sexe = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')], null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)  # Nouveau champ
    weight = models.IntegerField(null=True, blank=True)  # Nouveau champ
    steps = models.IntegerField(null=True, blank=True)   # Nouveau champ
    sleep_quality = models.IntegerField(null=True, blank=True)  # Nouveau champ
    sleep_duration = models.IntegerField(null=True, blank=True)  # Nouveau champ

    def __str__(self):
        return self.user.username

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

from django.db.models.signals import post_save
post_save.connect(create_user_profile, sender=DjangoUser)


class User(models.Model):
    pseudo = models.CharField(max_length=100)
    mail = models.EmailField(max_length=255)
    password = models.CharField(max_length=255)
    age = models.IntegerField(null=True, blank=True)
    sexe = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')], null=True, blank=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)  # Nouveau champ
    weight = models.IntegerField(null=True, blank=True)  # Nouveau champ
    steps = models.IntegerField(null=True, blank=True)   # Nouveau champ
    sleep_quality = models.IntegerField(null=True, blank=True)  # Nouveau champ
    sleep_duration = models.IntegerField(null=True, blank=True)  # Nouveau champ

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
            # Recherche de l'utilisateur dans la table auth_user de Django
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
    def update_user(cls, mail, password, first_name, last_name, username, age, sexe, height, weight, steps, sleep_quality, sleep_duration):
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
                f"UPDATE auth_user SET age = {age}, sexe = '{sexe}', height = {height}, weight = {weight}, steps = {steps}, sleep_quality = {sleep_quality}, sleep_duration = {sleep_duration} WHERE id = {user.id}"
            )
            conn.commit()
            cursor.close()
            conn.close()

            print("Utilisateur mis à jour avec succès !")
            return user
        except Exception as error:
            print("Erreur lors de la mise à jour de l'utilisateur :", error)
            return None
        
    @classmethod
    def get_user_data(self):
        conn = psycopg2.connect(
            dbname=os.environ.get('DB_NAME'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASSWORD'),
            host=os.environ.get('DB_HOST'),
            port=os.environ.get('DB_PORT')
        )
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM auth_user WHERE id = {self.id}")
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()
        print(user_data)
        return user_data

def load_model(model_name):
    loaded_model = joblib.load(f'{model_name}.joblib')
    return loaded_model

def preprocess_user_data(user):
    # Créer un DataFrame avec les données utilisateur
    data = {
        'Gender': [user.sexe],  # Assurez-vous que le genre est encodé comme 'M' ou 'F'
        'BMI Category': [user.bmi_category],  # Ajoutez ce champ si nécessaire
        'Sleep Duration': [user.sleep_duration],
        'Age': [user.age],
        'Heart Rate': [user.heart_rate],
        'Daily Steps': [user.steps],
        'Sleep Quality': [user.sleep_quality]
    }
    df = pd.DataFrame(data)

    # Appliquer le même prétraitement que vous avez fait pour les données d'entraînement
    heart_rate_bins = [0, 60, 80, 100, float('inf')]
    heart_rate_labels = ['Faible', 'Modéré', 'Élevé', 'Très élevé']
    df['Heart Rate Category'] = pd.cut(df['Heart Rate'], bins=heart_rate_bins, labels=heart_rate_labels)

    sleep_duration_bins = [0, 5, 7, 9, float('inf')]
    sleep_duration_labels = ['Très court', 'Court', 'Normal', 'Long']
    df['Sleep Duration Category'] = pd.cut(df['Sleep Duration'], bins=sleep_duration_bins, labels=sleep_duration_labels)

    age_bins = [0, 18, 30, 50, 70, float('inf')]
    age_labels = ['Enfant', 'Jeune adulte', 'Adulte', 'Senior', 'Super Senior']
    df['Age Category'] = pd.cut(df['Age'], bins=age_bins, labels=age_labels)

    df['BMI Category'] = df['BMI Category'].replace('Normal Weight', 'Normal')

    df.drop(columns=['Sleep Duration', 'Heart Rate', 'Age'], inplace=True)

    # Encodage des catégories
    label_encoders = {}
    for col in ['Gender', 'BMI Category', 'Sleep Duration Category', 'Age Category', 'Heart Rate Category']:
        label_encoders[col] = LabelEncoder()
        df[col] = label_encoders[col].fit_transform(df[col])

    return df.values[0]

def predict_sleep_disorder(user_id):
    model = load_model('sleep_disorder_model')
    
    # Récupérer l'utilisateur
    user = User.objects.get(id=user_id)
    
    # Prétraiter les données utilisateur
    features = preprocess_user_data(user)
    
    # Faire la prédiction
    prediction = model.predict([features])
    return prediction[0]