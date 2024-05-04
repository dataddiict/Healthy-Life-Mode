import psycopg2
from dotenv import load_dotenv
import os
load_dotenv()

def user_login():
    connection = None  # Initialisation de la variable connection à None
    try:
        print("DB_NAME", os.environ.get("DB_NAME"))
        # Connexion à la base de données en utilisant les variables d'environnement
        connection = psycopg2.connect(
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD"),
            host=os.environ.get("DB_HOST"),
            port=os.environ.get("DB_PORT"),
            database=os.environ.get("DB_NAME")
        )

        cursor = connection.cursor()

        # Demander à l'utilisateur de saisir son adresse e-mail et son mot de passe
        email = input("Veuillez saisir votre adresse e-mail : ")
        password = input("Veuillez saisir votre mot de passe : ")

        # Requête pour vérifier l'adresse e-mail et le mot de passe
        postgres_select_query = """SELECT * FROM user_data WHERE MAIL = %s AND PASSWORD = %s"""
        cursor.execute(postgres_select_query, (email, password))
        user_record = cursor.fetchone()

        if user_record:
            print("Connexion réussie !")
            # Ici vous pouvez ajouter du code pour gérer la connexion réussie, par exemple rediriger l'utilisateur vers une autre page
        else:
            print("Adresse e-mail ou mot de passe incorrect.")

    except (Exception, psycopg2.Error) as error:
        print("Erreur lors de la connexion à PostgreSQL ou lors de la récupération des données :", error)

    finally:
        # Fermeture de la connexion
        if connection:
            cursor.close()
            connection.close()
            print("Connexion à PostgreSQL fermée")

# Exemple d'utilisation
user_login()
