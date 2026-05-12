import customtkinter as ctk

class SettingsView(ctk.CTkFrame):
    def __init__(self, parent, controller, theme_callback=None):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.theme_callback = theme_callback
        self.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create settings widgets"""
        # Title
        title = ctk.CTkLabel(
            self,
            text="Paramètres",
            font=("Helvetica", 28, "bold"),
            text_color="#FFFFFF"
        )
        title.pack(pady=(0, 30))
        
        # Theme section
        theme_section = ctk.CTkFrame(self, fg_color="#2a2a2a", corner_radius=10)
        theme_section.pack(fill="x", pady=(0, 20))
        
        theme_title = ctk.CTkLabel(
            theme_section,
            text="Apparence",
            font=("Helvetica", 16, "bold"),
            text_color="#FFFFFF"
        )
        theme_title.pack(pady=(15, 10), padx=20, anchor="w")
        
        theme_frame = ctk.CTkFrame(theme_section, fg_color="transparent")
        theme_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        theme_label = ctk.CTkLabel(
            theme_frame,
            text="Mode Thème:",
            font=("Helvetica", 12),
            text_color="#CCCCCC"
        )
        theme_label.pack(side="left", padx=(0, 20))
        
        self.theme_var = ctk.StringVar(value="dark")
        theme_menu = ctk.CTkComboBox(
            theme_frame,
            values=["dark", "light"],
            variable=self.theme_var,
            command=self.on_theme_change,
            width=150,
            height=35
        )
        theme_menu.pack(side="left")
        
        # Database section
        db_section = ctk.CTkFrame(self, fg_color="#2a2a2a", corner_radius=10)
        db_section.pack(fill="x", pady=(0, 20))
        
        db_title = ctk.CTkLabel(
            db_section,
            text="Base de Données",
            font=("Helvetica", 16, "bold"),
            text_color="#FFFFFF"
        )
        db_title.pack(pady=(15, 10), padx=20, anchor="w")
        
        db_info = ctk.CTkLabel(
            db_section,
            text="Base de données: SQLite (bibliotheque.db)",
            font=("Helvetica", 11),
            text_color="#CCCCCC"
        )
        db_info.pack(pady=(0, 15), padx=20, anchor="w")
        
        db_button_frame = ctk.CTkFrame(db_section, fg_color="transparent")
        db_button_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        stats_btn = ctk.CTkButton(
            db_button_frame,
            text="Afficher les Statistiques",
            command=self.show_statistics,
            fg_color="#0084FF",
            hover_color="#0066CC"
        )
        stats_btn.pack(side="left", padx=(0, 10))
        
        # About section
        about_section = ctk.CTkFrame(self, fg_color="#2a2a2a", corner_radius=10)
        about_section.pack(fill="x", pady=(0, 20))
        
        about_title = ctk.CTkLabel(
            about_section,
            text="À Propos",
            font=("Helvetica", 16, "bold"),
            text_color="#FFFFFF"
        )
        about_title.pack(pady=(15, 10), padx=20, anchor="w")
        
        about_text = ctk.CTkLabel(
            about_section,
            text="Bibliothèque Intelligente avec Chatbot IA\nVersion 1.0\n\nUne application de gestion de bibliothèque moderne avec un assistant IA intégré.",
            font=("Helvetica", 11),
            text_color="#CCCCCC",
            justify="left"
        )
        about_text.pack(pady=(0, 15), padx=20, anchor="w")
        
        # Features section
        features_section = ctk.CTkFrame(self, fg_color="#2a2a2a", corner_radius=10)
        features_section.pack(fill="x")
        
        features_title = ctk.CTkLabel(
            features_section,
            text="Fonctionnalités",
            font=("Helvetica", 16, "bold"),
            text_color="#FFFFFF"
        )
        features_title.pack(pady=(15, 10), padx=20, anchor="w")
        
        features_text = ctk.CTkLabel(
            features_section,
            text="✓ Gestion complète des livres (Ajouter, Modifier, Supprimer)\n✓ Recherche avancée par titre, auteur ou catégorie\n✓ Tableau de bord avec statistiques en temps réel\n✓ Chatbot IA intelligent pour assistance\n✓ Interface moderne avec thème clair/sombre\n✓ Base de données SQLite robuste",
            font=("Helvetica", 11),
            text_color="#CCCCCC",
            justify="left"
        )
        features_text.pack(pady=(0, 15), padx=20, anchor="w")
    
    def on_theme_change(self, choice):
        """Handle theme change"""
        if self.theme_callback:
            self.theme_callback(choice)
    
    def show_statistics(self):
        """Show database statistics"""
        stats = self.controller.get_statistics()
        message = (
            f"Statistiques de la Bibliothèque:\n\n"
            f"Livres Totaux: {stats['total_books']}\n"
            f"Livres Disponibles: {stats['available_books']}\n"
            f"Auteurs Uniques: {stats['total_authors']}\n"
            f"Catégories: {stats['total_categories']}"
        )
        
        # Create info dialog
        dialog = ctk.CTkToplevel(self.master)
        dialog.title("Statistiques")
        dialog.geometry("400x300")
        
        dialog.attributes('-topmost', True)
        
        info_label = ctk.CTkLabel(
            dialog,
            text=message,
            font=("Helvetica", 12),
            text_color="#FFFFFF",
            justify="left"
        )
        info_label.pack(pady=30, padx=30)
        
        close_btn = ctk.CTkButton(
            dialog,
            text="Fermer",
            command=dialog.destroy,
            width=100
        )
        close_btn.pack(pady=20)
