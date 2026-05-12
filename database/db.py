import sqlite3
from config import DATABASE_NAME
def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    return connection

def create_tables():
    connection =get_connection()
    # Create a cursor object to execute SQL commands
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id_livre INTEGER PRIMARY KEY AUTOINCREMENT,
            titre TEXT NOT NULL,
            auteur TEXT NOT NULL,
            categorie TEXT NOT NULL,
            annee_publication INTEGER NOT NULL,
            quantite_disponible INTEGER NOT NULL,
            statut TEXT NOT NULL
        )
    """)
    connection.commit()
    connection.close()
