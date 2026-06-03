import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "bibliotheque.db")


class DatabaseManager:
    def __init__(self):
        self.db_path = DB_PATH
        self.connection = None
        self.connect()
        self.create_tables()
        self.seed_sample_data()

    def connect(self):
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row

    def create_tables(self):
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS livres (
                id_livre INTEGER PRIMARY KEY AUTOINCREMENT,
                titre TEXT NOT NULL,
                auteur TEXT NOT NULL,
                categorie TEXT NOT NULL,
                annee_publication INTEGER,
                quantite_disponible INTEGER DEFAULT 1,
                statut TEXT DEFAULT 'disponible'
            )
        """)
        self.connection.commit()

    def seed_sample_data(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM livres")
        count = cursor.fetchone()[0]
        if count == 0:
            sample_books = [
                ("Le Petit Prince", "Antoine de Saint-Exupéry", "Fiction", 1943, 3, "disponible"),
                ("L'Étranger", "Albert Camus", "Roman", 1942, 2, "emprunté"),
                ("Germinal", "Émile Zola", "Roman historique", 1885, 4, "disponible"),
                ("Les Misérables", "Victor Hugo", "Roman", 1862, 1, "réservé"),
                ("Madame Bovary", "Gustave Flaubert", "Roman", 1857, 2, "disponible"),
                ("Introduction à Python", "Luciano Ramalho", "Informatique", 2015, 5, "disponible"),
                ("Clean Code", "Robert C. Martin", "Informatique", 2008, 3, "emprunté"),
                ("Sapiens", "Yuval Noah Harari", "Histoire", 2011, 2, "disponible"),
                ("1984", "George Orwell", "Science-Fiction", 1949, 3, "disponible"),
                ("Dune", "Frank Herbert", "Science-Fiction", 1965, 2, "réservé"),
            ]
            cursor.executemany(
                "INSERT INTO livres (titre, auteur, categorie, annee_publication, quantite_disponible, statut) VALUES (?,?,?,?,?,?)",
                sample_books
            )
            self.connection.commit()

    def execute_query(self, query, params=()):
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        self.connection.commit()
        return cursor

    def fetch_all(self, query, params=()):
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def fetch_one(self, query, params=()):
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None

    def close(self):
        if self.connection:
            self.connection.close()
