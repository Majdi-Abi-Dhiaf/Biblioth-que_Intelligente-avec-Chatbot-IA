import customtkinter as ctk
import sqlite3
import os


class SettingsView(ctk.CTkFrame):
    def __init__(self, parent, controller, change_theme_callback):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.change_theme_callback = change_theme_callback
        self._build_ui()

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(25, 0))
        ctk.CTkLabel(header, text="⚙️  Paramètres",
                     font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")
        ctk.CTkLabel(header, text="Configuration et informations de l'application",
                     font=ctk.CTkFont(size=13), text_color="#888").pack(side="left", padx=14, pady=(6, 0))

        # Scrollable content
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=30, pady=20)

        # ── Theme Section ─────────────────────────────────────────────────────
        self._section(scroll, "🎨  Apparence")
        theme_card = ctk.CTkFrame(scroll, corner_radius=12)
        theme_card.pack(fill="x", pady=(0, 16))

        row = ctk.CTkFrame(theme_card, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=18)
        ctk.CTkLabel(row, text="Mode d'affichage", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")
        ctk.CTkLabel(row, text="Choisissez entre le mode sombre et clair",
                     font=ctk.CTkFont(size=12), text_color="#888").pack(side="left", padx=10)

        import customtkinter as _ctk
        current_mode = _ctk.get_appearance_mode().lower()
        self.theme_var = ctk.StringVar(value=current_mode)

        toggle_frame = ctk.CTkFrame(row, fg_color="transparent")
        toggle_frame.pack(side="right")

        for mode, icon in [("dark", "🌙  Sombre"), ("light", "☀️  Clair")]:
            ctk.CTkRadioButton(
                toggle_frame, text=icon, variable=self.theme_var, value=mode,
                command=lambda m=mode: self._apply_theme(m),
                font=ctk.CTkFont(size=13)
            ).pack(side="left", padx=10)

        # Color theme
        color_row = ctk.CTkFrame(theme_card, fg_color="transparent")
        color_row.pack(fill="x", padx=20, pady=(0, 16))
        ctk.CTkLabel(color_row, text="Thème de couleur", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")

        self.color_var = ctk.StringVar(value="blue")
        for color in ["blue", "green", "dark-blue"]:
            ctk.CTkRadioButton(
                color_row, text=color.capitalize(), variable=self.color_var, value=color,
                command=lambda c=color: ctk.set_default_color_theme(c),
                font=ctk.CTkFont(size=13)
            ).pack(side="left", padx=(20, 0))

        # ── Database Section ──────────────────────────────────────────────────
        self._section(scroll, "🗄️  Base de données")
        db_card = ctk.CTkFrame(scroll, corner_radius=12)
        db_card.pack(fill="x", pady=(0, 16))

        try:
            stats = self.controller.get_stats()
            db_status = "✅  Connectée"
            db_color  = "#10B981"
        except Exception:
            stats = {"total": 0}
            db_status = "❌  Déconnectée"
            db_color  = "#EF4444"

        db_path = os.path.abspath("bibliotheque.db")
        db_size = f"{os.path.getsize(db_path) / 1024:.1f} KB" if os.path.exists(db_path) else "N/A"

        info_items = [
            ("Statut",       db_status,           db_color),
            ("Moteur",       "SQLite 3",           None),
            ("Fichier",      db_path,              None),
            ("Taille",       db_size,              None),
            ("Total livres", str(stats["total"]),  None),
        ]
        for label, value, color in info_items:
            r = ctk.CTkFrame(db_card, fg_color="transparent")
            r.pack(fill="x", padx=20, pady=5)
            ctk.CTkLabel(r, text=f"{label} :", font=ctk.CTkFont(size=13),
                         text_color="#888", width=120, anchor="w").pack(side="left")
            ctk.CTkLabel(r, text=value, font=ctk.CTkFont(size=13),
                         text_color=color or ("white" if ctk.get_appearance_mode() == "dark" else "black")).pack(side="left")

        ctk.CTkButton(
            db_card, text="🔄  Rafraîchir les statistiques",
            command=self._refresh_db_info,
            fg_color="#3B82F6", hover_color="#1D4ED8",
            height=36, corner_radius=8, width=220
        ).pack(padx=20, pady=(6, 16))

        # ── API Section ───────────────────────────────────────────────────────
        self._section(scroll, "🤖  API Intelligence Artificielle")
        api_card = ctk.CTkFrame(scroll, corner_radius=12)
        api_card.pack(fill="x", pady=(0, 16))

        api_items = [
            ("Fournisseur", "Anthropic Claude"),
            ("Modèle",      "claude-sonnet-4-20250514"),
            ("Endpoint",    "https://api.anthropic.com/v1/messages"),
            ("Mode",        "Chatbot bibliothécaire intelligent"),
            ("Fallback",    "Réponses locales si API indisponible"),
        ]
        for label, value in api_items:
            r = ctk.CTkFrame(api_card, fg_color="transparent")
            r.pack(fill="x", padx=20, pady=5)
            ctk.CTkLabel(r, text=f"{label} :", font=ctk.CTkFont(size=13),
                         text_color="#888", width=120, anchor="w").pack(side="left")
            ctk.CTkLabel(r, text=value, font=ctk.CTkFont(size=13)).pack(side="left")

        # ── About Section ─────────────────────────────────────────────────────
        self._section(scroll, "ℹ️  À propos")
        about_card = ctk.CTkFrame(scroll, corner_radius=12)
        about_card.pack(fill="x", pady=(0, 16))

        about_frame = ctk.CTkFrame(about_card, fg_color="transparent")
        about_frame.pack(fill="x", padx=20, pady=16)

        ctk.CTkLabel(about_frame, text="📚", font=ctk.CTkFont(size=48)).pack(pady=(0, 8))
        ctk.CTkLabel(about_frame, text="Bibliothèque Intelligente avec Chatbot IA",
                     font=ctk.CTkFont(size=18, weight="bold")).pack()
        ctk.CTkLabel(about_frame, text="Version 1.0.0",
                     font=ctk.CTkFont(size=13), text_color="#888").pack(pady=(2, 0))
        ctk.CTkLabel(about_frame,
                     text="Application de gestion de bibliothèque avec chatbot IA intégré.\n"
                          "Architecture MVC • Python • CustomTkinter • SQLite",
                     font=ctk.CTkFont(size=12), text_color="#888",
                     justify="center").pack(pady=(10, 0))

        ctk.CTkLabel(about_frame, text="Développé par Majdi Abi Dhiaf",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color="#3B82F6").pack(pady=(10, 4))

        tech_frame = ctk.CTkFrame(about_frame, fg_color="transparent")
        tech_frame.pack(pady=8)
        for tech, color in [
            ("Python 3", "#3B82F6"),
            ("CustomTkinter", "#10B981"),
            ("SQLite", "#F59E0B"),
            ("Anthropic API", "#8B5CF6"),
        ]:
            badge = ctk.CTkFrame(tech_frame, fg_color=color, corner_radius=20)
            badge.pack(side="left", padx=4)
            ctk.CTkLabel(badge, text=tech, font=ctk.CTkFont(size=11, weight="bold"),
                         text_color="white").pack(padx=12, pady=4)

    def _section(self, parent, title):
        ctk.CTkLabel(parent, text=title, font=ctk.CTkFont(size=16, weight="bold")).pack(
            anchor="w", pady=(8, 6))

    def _apply_theme(self, mode):
        ctk.set_appearance_mode(mode)
        self.change_theme_callback(mode)

    def _refresh_db_info(self):
        # Rebuild settings view to refresh stats
        for w in self.winfo_children():
            w.destroy()
        self._build_ui()
