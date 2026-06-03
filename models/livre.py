class Livre:
    def __init__(self, id_livre=None, titre="", auteur="", categorie="",
                 annee_publication=None, quantite_disponible=1, statut="disponible"):
        self.id_livre = id_livre
        self.titre = titre
        self.auteur = auteur
        self.categorie = categorie
        self.annee_publication = annee_publication
        self.quantite_disponible = quantite_disponible
        self.statut = statut

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id_livre=data.get("id_livre"),
            titre=data.get("titre", ""),
            auteur=data.get("auteur", ""),
            categorie=data.get("categorie", ""),
            annee_publication=data.get("annee_publication"),
            quantite_disponible=data.get("quantite_disponible", 1),
            statut=data.get("statut", "disponible"),
        )

    def to_tuple(self):
        return (self.titre, self.auteur, self.categorie,
                self.annee_publication, self.quantite_disponible, self.statut)

    def __repr__(self):
        return f"<Livre id={self.id_livre} titre='{self.titre}'>"
