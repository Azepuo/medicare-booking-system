import mysql.connector
from specialisations import up  # chemin vers ton fichier

# Connexion à la base
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",  # change selon ta config
    database="medicare_db"
)

# Exécuter la migration
up(connection)

# Fermer la connexion
connection.close()
