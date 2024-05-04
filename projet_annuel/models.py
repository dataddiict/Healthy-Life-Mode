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

    @classmethod
    def create_user(cls, pseudo, mail, password):
            try:
                # Créer un nouvel utilisateur dans la table auth_user
                user = DjangoUser.objects.create_user(username=mail, email=mail, password=password)
                
                # Mettre à jour les autres champs de l'utilisateur
                user.first_name = pseudo
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
   

