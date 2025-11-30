import mysql.connector
from insert_data import seed_all # pyright: ignore[reportMissingImports]

connection = mysql.connector.connect(
    host="localhost",
    port=3307,  
    user="root",
    password="",
    database="medicare_booking"  # <- Vérifie ce nom
)

cursor = connection.cursor()
seed_all(cursor)
connection.commit()  #  Obligatoire pour appliquer les insertions
cursor.close()
connection.close()