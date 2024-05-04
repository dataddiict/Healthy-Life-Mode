import psycopg2
from dotenv import load_dotenv
import os
load_dotenv()
try:
    connection = psycopg2.connect(
        # Connexion à la base de données en utilisant les variables d'environnement

        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        host=os.environ.get("DB_HOST"),
        port=os.environ.get("DB_PORT"),
        database=os.environ.get("DB_NAME")
    )
    
    cursor = connection.cursor()
    postgres_insert_query = """ INSERT INTO user_data (PSEUDO, MAIL, PASSWORD) VALUES (%s,%s,%s)"""
    record_to_insert = ('VICTOR', 'jouinvictor1@gmail.com', '1234')
    cursor.execute(postgres_insert_query, record_to_insert)

    connection.commit()
    count = cursor.rowcount
    print (count, "Record inserted successfully into nom_table")

except (Exception, psycopg2.Error) as error:
    print("Erreur lors de la connexion à PostgreSQL ou lors de l'insertion :", error)

finally:
    # Fermeture de la connexion
    if connection:
        cursor.close()
        connection.close()
        print("Connexion à PostgreSQL fermée")
