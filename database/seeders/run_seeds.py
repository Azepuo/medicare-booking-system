import mysql.connector
from insert_data import seed_all

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="medicare_db"  # <- Vérifie ce nom
)

cursor = connection.cursor()
seed_all(cursor)
connection.commit()  # ⚠️ Obligatoire pour appliquer les insertions
cursor.close()
connection.close()
