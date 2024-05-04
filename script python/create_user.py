import psycopg2

try:
    connection = psycopg2.connect(
        user="alexandre",
        password="esgi2024",
        host="exchange.cbquewsgc2wo.eu-west-1.rds.amazonaws.com",
        port="5432",
        database="postgre"
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
