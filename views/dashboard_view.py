import customtkinter as ctk
from tkinter import ttk
import datetime


class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self._build_ui()

    def _build_ui(self):
        # ── Header ────────────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(25, 0))

        now = datetime.datetime.now()
        greeting = "Bonsoir" if now.hour >= 18 else ("Bonjour" if now.hour >= 12 else "Bonjour")

        ctk.CTkLabel(
            header,
            text=f"{greeting}, Bibliothécaire 👋",
            font=ctk.CTkFont(size=26, weight="bold"),
        ).pack(side="left")

        date_str = now.strftime("%A %d %B %Y")
        ctk.CTkLabel(
            header,
            text=date_str,
            font=ctk.CTkFont(size=13),
            text_color="#888",
        ).pack(side="right", padx=5)

        ctk.CTkLabel(
            self,
            text="Tableau de bord — vue d'ensemble de votre bibliothèque",
            font=ctk.CTkFont(size=13),
            text_color="#888",
        ).pack(anchor="w", padx=30, pady=(4, 20))

        # ── Stat cards ────────────────────────────────────────────────────────
        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.pack(fill="x", padx=30, pady=(0, 20))

        self.card_widgets = {}
        card_defs = [
            ("total",      "📚", "Total livres",     "#3B82F6", "#1D4ED8"),
            ("disponible", "✅", "Disponibles",       "#10B981", "#065F46"),
            ("emprunte",   "📤", "Empruntés",         "#F59E0B", "#92400E"),
            ("reserve",    "🔖", "Réservés",          "#8B5CF6", "#4C1D95"),
        ]
        for i, (key, icon, label, color, dark) in enumerate(card_defs):
            self.cards_frame.columnconfigure(i, weight=1)
            card = self._make_stat_card(self.cards_frame, icon, label, "0", color, dark)
            card.grid(row=0, column=i, padx=8, sticky="ew")
            self.card_widgets[key] = card

        # ── Content row ───────────────────────────────────────────────────────
        content_row = ctk.CTkFrame(self, fg_color="transparent")
        content_row.pack(fill="both", expand=True, padx=30, pady=(0, 25))
        content_row.columnconfigure(0, weight=3)
        content_row.columnconfigure(1, weight=2)
        content_row.rowconfigure(0, weight=1)

        # Recent books table
        left_panel = ctk.CTkFrame(content_row, corner_radius=14)
        left_panel.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="nsew")

        ctk.CTkLabel(
            left_panel,
            text="📖  Livres récemment ajoutés",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(anchor="w", padx=18, pady=(16, 8))

        # Treeview for recent books
        tree_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=12, pady=(0, 14))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Dashboard.Treeview",
            background="#2b2b2b",
            foreground="#eeeeee",
            rowheight=30,
            fieldbackground="#2b2b2b",
            borderwidth=0,
            font=("Helvetica", 11),
        )
        style.configure("Dashboard.Treeview.Heading",
                        background="#1f1f1f", foreground="#aaaaaa",
                        font=("Helvetica", 11, "bold"), relief="flat")
        style.map("Dashboard.Treeview", background=[("selected", "#3B82F6")])

        columns = ("titre", "auteur", "categorie", "statut")
        self.recent_tree = ttk.Treeview(
            tree_frame, columns=columns, show="headings",
            style="Dashboard.Treeview", height=9
        )
        for col, heading, width in [
            ("titre", "Titre", 200),
            ("auteur", "Auteur", 140),
            ("categorie", "Catégorie", 120),
            ("statut", "Statut", 90),
        ]:
            self.recent_tree.heading(col, text=heading)
            self.recent_tree.column(col, width=width, anchor="w")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.recent_tree.yview)
        self.recent_tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.recent_tree.pack(fill="both", expand=True)

        # Right panel – quick info
        right_panel = ctk.CTkFrame(content_row, corner_radius=14)
        right_panel.grid(row=0, column=1, padx=(10, 0), pady=0, sticky="nsew")

        ctk.CTkLabel(
            right_panel,
            text="⚡  Accès rapide",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(anchor="w", padx=18, pady=(16, 12))

        quick_items = [
            ("📚", "Gestion des livres",   "Ajouter, modifier, supprimer"),
            ("🤖", "Chatbot IA",            "Posez vos questions"),
            ("🔍", "Recherche avancée",     "Titre, auteur, ID"),
            ("⚙️", "Paramètres",            "Thème & configuration"),
        ]
        for icon, title, desc in quick_items:
            item_frame = ctk.CTkFrame(right_panel, corner_radius=10, fg_color=("#e8f0fe", "#1e2a3a"))
            item_frame.pack(fill="x", padx=14, pady=5)
            ctk.CTkLabel(item_frame, text=icon, font=ctk.CTkFont(size=22)).pack(side="left", padx=(12, 8), pady=10)
            text_f = ctk.CTkFrame(item_frame, fg_color="transparent")
            text_f.pack(side="left", pady=8)
            ctk.CTkLabel(text_f, text=title, font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w")
            ctk.CTkLabel(text_f, text=desc, font=ctk.CTkFont(size=11), text_color="#888").pack(anchor="w")

        # Category distribution
        ctk.CTkLabel(
            right_panel,
            text="📊  Statut des livres",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", padx=18, pady=(16, 6))

        self.status_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        self.status_frame.pack(fill="x", padx=14, pady=(0, 14))

        self.refresh()

    def _make_stat_card(self, parent, icon, label, value, color, dark_color):
        card = ctk.CTkFrame(parent, corner_radius=14, height=110)
        card.pack_propagate(False)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=16, pady=(14, 0))

        ctk.CTkLabel(top, text=icon, font=ctk.CTkFont(size=26)).pack(side="left")
        val_lbl = ctk.CTkLabel(top, text=value, font=ctk.CTkFont(size=28, weight="bold"), text_color=color)
        val_lbl.pack(side="right")
        card._value_label = val_lbl

        ctk.CTkLabel(card, text=label, font=ctk.CTkFont(size=12), text_color="#aaa").pack(anchor="w", padx=16, pady=(2, 10))

        # Accent bar
        accent = ctk.CTkFrame(card, fg_color=color, height=4, corner_radius=0)
        accent.pack(fill="x", side="bottom")

        return card

    def _update_stat_cards(self, stats):
        colors = {
            "total": "#3B82F6",
            "disponible": "#10B981",
            "emprunte": "#F59E0B",
            "reserve": "#8B5CF6",
        }
        for key, widget in self.card_widgets.items():
            widget._value_label.configure(
                text=str(stats.get(key, 0)),
                text_color=colors[key]
            )

    def _update_status_bars(self, stats):
        for w in self.status_frame.winfo_children():
            w.destroy()

        total = max(stats["total"], 1)
        for label, key, color in [
            ("Disponibles", "disponible", "#10B981"),
            ("Empruntés",   "emprunte",   "#F59E0B"),
            ("Réservés",    "reserve",    "#8B5CF6"),
        ]:
            count = stats[key]
            pct = int(count / total * 100)
            row = ctk.CTkFrame(self.status_frame, fg_color="transparent")
            row.pack(fill="x", pady=4)
            ctk.CTkLabel(row, text=f"{label}:", font=ctk.CTkFont(size=11), width=90, anchor="w").pack(side="left")
            bar_bg = ctk.CTkFrame(row, height=10, corner_radius=5, fg_color=("#ddd", "#333"))
            bar_bg.pack(side="left", fill="x", expand=True, padx=(4, 8))
            if pct > 0:
                fill = ctk.CTkFrame(bar_bg, height=10, corner_radius=5, fg_color=color)
                fill.place(relx=0, rely=0, relwidth=pct/100, relheight=1)
            ctk.CTkLabel(row, text=f"{count}", font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=color, width=28).pack(side="right")

    def refresh(self):
        try:
            stats = self.controller.get_stats()
            self._update_stat_cards(stats)
            self._update_status_bars(stats)

            for row in self.recent_tree.get_children():
                self.recent_tree.delete(row)

            books = self.controller.get_recent_books(10)
            status_colors = {"disponible": "#10B981", "emprunté": "#F59E0B", "réservé": "#8B5CF6"}
            for b in books:
                self.recent_tree.insert("", "end", values=(b.titre, b.auteur, b.categorie, b.statut))
        except Exception as e:
            print(f"Dashboard refresh error: {e}")
