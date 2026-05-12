from multiprocessing import connection

from database.db import get_connection
from models.book import Book
class Book_controller:
    def add_book(self,book:Book):
        connection= get_connection()
        cursor = connection.cursor()
        cursor.execute("""
        
        INSERT INTO books(
                titre,
                auteur,
                categorie,
                annee_publication,
                quantite_disponible,
                statut )
        VALUES(?,?,?,?,?,?)
        """,( book.titre,
            book.auteur,
            book.categorie,
            book.annee_publication,
            book.quantite_disponible,
            book.statut)
        )
        connection.commit()
        connection.close()


    def get_all_books(self):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM books")
        books = cursor.fetchall()
        connection.close()
        return books
    
    def get_by_id (self, id_livre):
        connection = get_connection()
        cursor =connection.cursor()
        cursor.execute("SELECT * FROM books WHERE id_livre=?",(id_livre,))
        book= cursor.fetchone()
        cursor.close()
        return book 
    def search_book(self, keyword):
        connection =get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM books WHERE title LIKE ? OR auteur LIKE ? OR categorie LIKE ? ",(  f"%{keyword}%",f"%{keyword}%",f"%{keyword}%"))
        books = cursor.fetchall()
        connection.close()
        return books
    def update_book(self,book:Book):
        connection= get_connection()
        cursor=connection.cursor()
        cursor.execute("UPDATE books SET titre = ?,auteur = ?,categorie = ?,annee_publication = ?,quantite_disponible = ?,statut = ? WHERE id_livre = ? ",(
            book.titre,
            book.auteur,
            book.categorie,
            book.annee_publication,
            book.quantite_disponible,
            book.statut,
            book.id_livre
        ))
        connection.commit()
        connection.close()

    def delete_book(self, id_livre):
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM books WHERE id_livre = ?",
            (id_livre,)
        )

        connection.commit()
        connection.close()
        
    def get_statistics(self):
        connection = get_connection()
        cursor = connection.cursor()

        # Total books
        cursor.execute("SELECT COUNT(*) FROM books")
        total_books = cursor.fetchone()[0]

        # Available books
        cursor.execute("""
            SELECT COUNT(*)
            FROM books
            WHERE statut = 'disponible'
        """)
        available_books = cursor.fetchone()[0]

        # Total authors
        cursor.execute("""
            SELECT COUNT(DISTINCT auteur)
            FROM books
        """)
        total_authors = cursor.fetchone()[0]

        # Total categories
        cursor.execute("""
            SELECT COUNT(DISTINCT categorie)
            FROM books
        """)
        total_categories = cursor.fetchone()[0]

        connection.close()

        return {
            "total_books": total_books,
            "available_books": available_books,
            "total_authors": total_authors,
            "total_categories": total_categories
        }