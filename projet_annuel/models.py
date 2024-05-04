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

    @classmethod
    def create_user(cls, mail, password, first_name, last_name, username):
        try:
            # Créer un nouvel utilisateur dans la table auth_user
            user = DjangoUser.objects.create_user(username=username, email=mail, password=password)
            
            # Mettre à jour les autres champs de l'utilisateur
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
    def update_user(cls, mail, password, first_name, last_name, username, age, sexe):
        try:
            # Mettre à jour l'utilisateur existant ou en créer un nouveau s'il n'existe pas déjà
            user, created = DjangoUser.objects.update_or_create(
                username=username,
                defaults={
                    'email': mail,
                    'password': password,
                    'first_name': first_name,
                    'last_name': last_name,
                    'age': age,
                    'sexe': sexe
                }
            )
            print("Utilisateur mis à jour avec succès !")
            return user

        except Exception as error:
            print("Erreur lors de la mise à jour de l'utilisateur :", error)
            return None


