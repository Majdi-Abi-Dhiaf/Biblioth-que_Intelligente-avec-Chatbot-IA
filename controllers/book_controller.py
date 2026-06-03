from database.db_manager import DatabaseManager
from models.livre import Livre


class Book_controller:
    def __init__(self):
        self.db = DatabaseManager()

    # ─── CRUD ────────────────────────────────────────────────────────────────

    def get_all_books(self):
        rows = self.db.fetch_all("SELECT * FROM livres ORDER BY id_livre")
        return [Livre.from_dict(r) for r in rows]

    def get_book_by_id(self, book_id):
        row = self.db.fetch_one("SELECT * FROM livres WHERE id_livre=?", (book_id,))
        return Livre.from_dict(row) if row else None

    def add_book(self, livre: Livre):
        self.db.execute_query(
            "INSERT INTO livres (titre, auteur, categorie, annee_publication, quantite_disponible, statut) VALUES (?,?,?,?,?,?)",
            livre.to_tuple()
        )

    def update_book(self, livre: Livre):
        self.db.execute_query(
            "UPDATE livres SET titre=?, auteur=?, categorie=?, annee_publication=?, quantite_disponible=?, statut=? WHERE id_livre=?",
            (*livre.to_tuple(), livre.id_livre)
        )

    def delete_book(self, book_id):
        self.db.execute_query("DELETE FROM livres WHERE id_livre=?", (book_id,))

    # ─── Search ───────────────────────────────────────────────────────────────

    def search_by_title(self, titre):
        rows = self.db.fetch_all(
            "SELECT * FROM livres WHERE titre LIKE ? ORDER BY titre",
            (f"%{titre}%",)
        )
        return [Livre.from_dict(r) for r in rows]

    def search_by_author(self, auteur):
        rows = self.db.fetch_all(
            "SELECT * FROM livres WHERE auteur LIKE ? ORDER BY auteur",
            (f"%{auteur}%",)
        )
        return [Livre.from_dict(r) for r in rows]

    def search_by_id(self, book_id):
        livre = self.get_book_by_id(book_id)
        return [livre] if livre else []

    # ─── Statistics ───────────────────────────────────────────────────────────

    def get_stats(self):
        total = self.db.fetch_one("SELECT COUNT(*) as c FROM livres")["c"]
        disponible = self.db.fetch_one("SELECT COUNT(*) as c FROM livres WHERE statut='disponible'")["c"]
        emprunte = self.db.fetch_one("SELECT COUNT(*) as c FROM livres WHERE statut='emprunté'")["c"]
        reserve = self.db.fetch_one("SELECT COUNT(*) as c FROM livres WHERE statut='réservé'")["c"]
        return {
            "total": total,
            "disponible": disponible,
            "emprunte": emprunte,
            "reserve": reserve,
        }

    def get_recent_books(self, limit=5):
        rows = self.db.fetch_all(
            "SELECT * FROM livres ORDER BY id_livre DESC LIMIT ?", (limit,)
        )
        return [Livre.from_dict(r) for r in rows]

    # ─── Chatbot helpers ──────────────────────────────────────────────────────

    def book_exists(self, titre):
        rows = self.db.fetch_all(
            "SELECT * FROM livres WHERE titre LIKE ?", (f"%{titre}%",)
        )
        return [Livre.from_dict(r) for r in rows]

    def get_by_category(self, categorie):
        rows = self.db.fetch_all(
            "SELECT * FROM livres WHERE categorie LIKE ?", (f"%{categorie}%",)
        )
        return [Livre.from_dict(r) for r in rows]

    def get_categories(self):
        rows = self.db.fetch_all("SELECT DISTINCT categorie FROM livres ORDER BY categorie")
        return [r["categorie"] for r in rows]

    def close(self):
        self.db.close()
