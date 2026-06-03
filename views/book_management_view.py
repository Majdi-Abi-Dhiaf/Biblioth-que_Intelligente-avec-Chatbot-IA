import customtkinter as ctk
from tkinter import ttk, messagebox
from models.livre import Livre


CATEGORIES = [
    "Fiction", "Roman", "Roman historique", "Science-Fiction",
    "Informatique", "Histoire", "Philosophie", "Sciences", "Poésie",
    "Biographie", "Développement personnel", "Autre"
]
STATUTS = ["disponible", "emprunté", "réservé"]


class BookManagementView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.selected_id = None
        self._build_ui()
        self.load_books()

    # ─── UI Build ─────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Title
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(25, 0))
        ctk.CTkLabel(header, text="📚  Gestion des Livres",
                     font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")
        ctk.CTkLabel(header, text="Ajouter, modifier et supprimer des livres",
                     font=ctk.CTkFont(size=13), text_color="#888").pack(side="left", padx=(14, 0), pady=(6, 0))

        # Main two-column layout
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=30, pady=16)
        main.columnconfigure(0, weight=2)
        main.columnconfigure(1, weight=5)
        main.rowconfigure(0, weight=1)

        # ── Left panel: Form ──────────────────────────────────────────────────
        left = ctk.CTkFrame(main, corner_radius=14)
        left.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        ctk.CTkLabel(left, text="✏️  Formulaire", font=ctk.CTkFont(size=15, weight="bold")).pack(
            anchor="w", padx=16, pady=(16, 4))

        form_scroll = ctk.CTkScrollableFrame(left, fg_color="transparent")
        form_scroll.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        # Form fields
        self.entry_titre    = self._form_entry(form_scroll, "Titre *")
        self.entry_auteur   = self._form_entry(form_scroll, "Auteur *")
        self.combo_categorie = self._form_combo(form_scroll, "Catégorie *", CATEGORIES)
        self.entry_annee    = self._form_entry(form_scroll, "Année de publication")
        self.entry_quantite = self._form_entry(form_scroll, "Quantité disponible")
        self.combo_statut   = self._form_combo(form_scroll, "Statut *", STATUTS)

        # CRUD Buttons
        btns = ctk.CTkFrame(left, fg_color="transparent")
        btns.pack(fill="x", padx=10, pady=(4, 14))

        btn_defs = [
            ("➕  Ajouter",       self.add_book,    "#10B981", "#065F46"),
            ("✏️  Modifier",      self.update_book, "#3B82F6", "#1D4ED8"),
            ("🗑️  Supprimer",    self.delete_book, "#EF4444", "#991B1B"),
            ("🔄  Actualiser",    self.load_books,  "#6B7280", "#374151"),
            ("🧹  Vider",         self.clear_form,  "#8B5CF6", "#4C1D95"),
        ]
        for text, cmd, color, hcolor in btn_defs:
            ctk.CTkButton(
                btns, text=text, command=cmd,
                fg_color=color, hover_color=hcolor,
                height=36, corner_radius=8,
                font=ctk.CTkFont(size=12)
            ).pack(fill="x", pady=3)

        # ── Right panel: Search + Table ───────────────────────────────────────
        right = ctk.CTkFrame(main, corner_radius=14)
        right.grid(row=0, column=1, padx=(10, 0), sticky="nsew")

        # Search bar
        search_bar = ctk.CTkFrame(right, fg_color="transparent")
        search_bar.pack(fill="x", padx=16, pady=(16, 8))

        ctk.CTkLabel(search_bar, text="🔍  Rechercher :",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=(0, 10))

        self.search_titre_var = ctk.StringVar()
        self.search_auteur_var = ctk.StringVar()
        self.search_id_var = ctk.StringVar()

        for var, placeholder in [
            (self.search_titre_var, "Par titre…"),
            (self.search_auteur_var, "Par auteur…"),
            (self.search_id_var, "Par ID…"),
        ]:
            e = ctk.CTkEntry(search_bar, textvariable=var, placeholder_text=placeholder,
                             width=130, height=32, corner_radius=8)
            e.pack(side="left", padx=4)
            var.trace_add("write", self._on_search_change)

        ctk.CTkButton(search_bar, text="Réinitialiser", command=self._reset_search,
                      fg_color="#6B7280", hover_color="#374151",
                      width=100, height=32, corner_radius=8).pack(side="left", padx=6)

        # Book count label
        self.count_label = ctk.CTkLabel(right, text="", font=ctk.CTkFont(size=12), text_color="#888")
        self.count_label.pack(anchor="e", padx=16)

        # Treeview
        tree_frame = ctk.CTkFrame(right, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=12, pady=(0, 14))

        self._configure_treeview_style()

        columns = ("id", "titre", "auteur", "categorie", "annee", "quantite", "statut")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                                 style="Books.Treeview")

        col_defs = [
            ("id",        "ID",         50,  "center"),
            ("titre",     "Titre",      200, "w"),
            ("auteur",    "Auteur",     140, "w"),
            ("categorie", "Catégorie",  120, "w"),
            ("annee",     "Année",       65, "center"),
            ("quantite",  "Qté",         45, "center"),
            ("statut",    "Statut",       90, "center"),
        ]
        for col, heading, width, anchor in col_defs:
            self.tree.heading(col, text=heading, command=lambda c=col: self._sort_tree(c, False))
            self.tree.column(col, width=width, anchor=anchor, minwidth=width//2)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_row_select)
        self.tree.tag_configure("disponible", foreground="#10B981")
        self.tree.tag_configure("emprunté",   foreground="#F59E0B")
        self.tree.tag_configure("réservé",    foreground="#8B5CF6")
        self.tree.tag_configure("odd",  background="#252525")
        self.tree.tag_configure("even", background="#1e1e1e")

    def _configure_treeview_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Books.Treeview",
                        background="#252525", foreground="#eeeeee",
                        rowheight=32, fieldbackground="#252525",
                        borderwidth=0, font=("Helvetica", 11))
        style.configure("Books.Treeview.Heading",
                        background="#1a1a1a", foreground="#aaaaaa",
                        font=("Helvetica", 11, "bold"), relief="flat", padding=(4, 6))
        style.map("Books.Treeview",
                  background=[("selected", "#3B82F6")],
                  foreground=[("selected", "#ffffff")])

    def _form_entry(self, parent, label_text):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=5)
        ctk.CTkLabel(frame, text=label_text, font=ctk.CTkFont(size=12),
                     anchor="w").pack(fill="x")
        entry = ctk.CTkEntry(frame, height=36, corner_radius=8)
        entry.pack(fill="x")
        return entry

    def _form_combo(self, parent, label_text, values):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=5)
        ctk.CTkLabel(frame, text=label_text, font=ctk.CTkFont(size=12),
                     anchor="w").pack(fill="x")
        combo = ctk.CTkComboBox(frame, values=values, height=36, corner_radius=8)
        combo.set(values[0])
        combo.pack(fill="x")
        return combo

    # ─── CRUD Operations ──────────────────────────────────────────────────────

    def _get_form_data(self):
        return {
            "titre":              self.entry_titre.get().strip(),
            "auteur":             self.entry_auteur.get().strip(),
            "categorie":          self.combo_categorie.get(),
            "annee_publication":  self.entry_annee.get().strip(),
            "quantite_disponible": self.entry_quantite.get().strip(),
            "statut":             self.combo_statut.get(),
        }

    def _validate(self, data):
        if not data["titre"]:
            messagebox.showerror("Validation", "Le titre est obligatoire.")
            return False
        if not data["auteur"]:
            messagebox.showerror("Validation", "L'auteur est obligatoire.")
            return False
        if data["annee_publication"] and not data["annee_publication"].isdigit():
            messagebox.showerror("Validation", "L'année doit être un nombre entier.")
            return False
        if data["quantite_disponible"] and not data["quantite_disponible"].isdigit():
            messagebox.showerror("Validation", "La quantité doit être un nombre entier.")
            return False
        return True

    def add_book(self):
        data = self._get_form_data()
        if not self._validate(data):
            return
        livre = Livre(
            titre=data["titre"],
            auteur=data["auteur"],
            categorie=data["categorie"],
            annee_publication=int(data["annee_publication"]) if data["annee_publication"] else None,
            quantite_disponible=int(data["quantite_disponible"]) if data["quantite_disponible"] else 1,
            statut=data["statut"],
        )
        self.controller.add_book(livre)
        self.load_books()
        self.clear_form()
        messagebox.showinfo("Succès", f"✅ Le livre « {data['titre']} » a été ajouté.")

    def update_book(self):
        if not self.selected_id:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner un livre à modifier.")
            return
        data = self._get_form_data()
        if not self._validate(data):
            return
        livre = Livre(
            id_livre=self.selected_id,
            titre=data["titre"],
            auteur=data["auteur"],
            categorie=data["categorie"],
            annee_publication=int(data["annee_publication"]) if data["annee_publication"] else None,
            quantite_disponible=int(data["quantite_disponible"]) if data["quantite_disponible"] else 1,
            statut=data["statut"],
        )
        self.controller.update_book(livre)
        self.load_books()
        messagebox.showinfo("Succès", f"✏️ Le livre « {data['titre']} » a été modifié.")

    def delete_book(self):
        if not self.selected_id:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner un livre à supprimer.")
            return
        book = self.controller.get_book_by_id(self.selected_id)
        if not book:
            return
        if messagebox.askyesno("Confirmer", f"Supprimer « {book.titre} » ?"):
            self.controller.delete_book(self.selected_id)
            self.load_books()
            self.clear_form()
            messagebox.showinfo("Succès", "🗑️ Le livre a été supprimé.")

    def clear_form(self):
        self.entry_titre.delete(0, "end")
        self.entry_auteur.delete(0, "end")
        self.combo_categorie.set(CATEGORIES[0])
        self.entry_annee.delete(0, "end")
        self.entry_quantite.delete(0, "end")
        self.combo_statut.set(STATUTS[0])
        self.selected_id = None

    # ─── Table & Search ───────────────────────────────────────────────────────

    def load_books(self, books=None):
        if books is None:
            books = self.controller.get_all_books()
        for row in self.tree.get_children():
            self.tree.delete(row)
        for i, b in enumerate(books):
            tags = (b.statut.replace("é", "e").replace("è", "e"),
                    "odd" if i % 2 else "even")
            self.tree.insert("", "end", iid=str(b.id_livre), values=(
                b.id_livre, b.titre, b.auteur, b.categorie,
                b.annee_publication or "", b.quantite_disponible, b.statut
            ), tags=tags)
        n = len(books)
        self.count_label.configure(text=f"{n} livre{'s' if n > 1 else ''} affiché{'s' if n > 1 else ''}")

    def _on_row_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        values = self.tree.item(sel[0])["values"]
        self.selected_id = values[0]
        self.entry_titre.delete(0, "end")
        self.entry_titre.insert(0, values[1])
        self.entry_auteur.delete(0, "end")
        self.entry_auteur.insert(0, values[2])
        self.combo_categorie.set(values[3])
        self.entry_annee.delete(0, "end")
        self.entry_annee.insert(0, str(values[4]))
        self.entry_quantite.delete(0, "end")
        self.entry_quantite.insert(0, str(values[5]))
        self.combo_statut.set(values[6])

    def _on_search_change(self, *args):
        titre  = self.search_titre_var.get().strip()
        auteur = self.search_auteur_var.get().strip()
        sid    = self.search_id_var.get().strip()
        if sid:
            if sid.isdigit():
                books = self.controller.search_by_id(int(sid))
            else:
                books = []
        elif titre:
            books = self.controller.search_by_title(titre)
        elif auteur:
            books = self.controller.search_by_author(auteur)
        else:
            books = self.controller.get_all_books()
        self.load_books(books)

    def _reset_search(self):
        self.search_titre_var.set("")
        self.search_auteur_var.set("")
        self.search_id_var.set("")
        self.load_books()

    def _sort_tree(self, col, reverse):
        data = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        try:
            data.sort(key=lambda t: int(t[0]), reverse=reverse)
        except ValueError:
            data.sort(key=lambda t: t[0].lower(), reverse=reverse)
        for index, (_, k) in enumerate(data):
            self.tree.move(k, "", index)
        self.tree.heading(col, command=lambda: self._sort_tree(col, not reverse))
