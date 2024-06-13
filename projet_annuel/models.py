from django.db import models
import os 
import psycopg2
from django.contrib.auth.models import User as DjangoUser
from dotenv import load_dotenv
load_dotenv()


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

            # Vérification du mot de passe
            if user.check_password(password):
                print("Connexion réussie !")
            else:
                print("Mot de passe incorrect.")

        except DjangoUser.DoesNotExist:
            print("Utilisateur non trouvé.")
        except Exception as error:
            print("Erreur lors de la connexion ou de la vérification du mot de passe :", error)

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


