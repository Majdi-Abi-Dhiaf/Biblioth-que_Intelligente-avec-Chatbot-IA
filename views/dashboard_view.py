import customtkinter as ctk
from PIL import Image, ImageDraw
import io

class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create dashboard widgets"""
        # Title
        title = ctk.CTkLabel(
            self,
            text="Tableau de Bord",
            font=("Helvetica", 28, "bold"),
            text_color="#FFFFFF"
        )
        title.pack(pady=(0, 30))
        
        # Statistics grid
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.pack(fill="both", expand=True)
        
        stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="column")
        stats_frame.grid_rowconfigure(0, weight=1)
        
        # Get statistics from database
        stats = self.controller.get_statistics()
        
        # Stat cards
        self.create_stat_card(
            stats_frame, 0, "Livres Totaux",
            str(stats['total_books']), "#0084FF"
        )
        self.create_stat_card(
            stats_frame, 1, "Livres Disponibles",
            str(stats['available_books']), "#00D084"
        )
        self.create_stat_card(
            stats_frame, 2, "Auteurs",
            str(stats['total_authors']), "#FF6B6B"
        )
        self.create_stat_card(
            stats_frame, 3, "Catégories",
            str(stats['total_categories']), "#FFB800"
        )
        
        # Welcome message
        welcome_frame = ctk.CTkFrame(self, fg_color="#2a2a2a", corner_radius=10)
        welcome_frame.pack(fill="x", pady=(30, 0))
        
        welcome_title = ctk.CTkLabel(
            welcome_frame,
            text="Bienvenue dans votre Bibliothèque Intelligente",
            font=("Helvetica", 18, "bold"),
            text_color="#FFFFFF"
        )
        welcome_title.pack(pady=(15, 10), padx=20)
        
        welcome_text = ctk.CTkLabel(
            welcome_frame,
            text="Utilisez le menu latéral pour accéder à la gestion des livres, au chatbot IA, et aux paramètres.",
            font=("Helvetica", 12),
            text_color="#CCCCCC",
            wraplength=400
        )
        welcome_text.pack(pady=(0, 15), padx=20)
    
    def create_stat_card(self, parent, column, label, value, color):
        """Create a statistics card"""
        card = ctk.CTkFrame(
            parent,
            fg_color="#2a2a2a",
            corner_radius=10,
            border_width=2,
            border_color=color
        )
        card.grid(row=0, column=column, padx=10, pady=10, sticky="nsew")
        
        label_widget = ctk.CTkLabel(
            card,
            text=label,
            font=("Helvetica", 12),
            text_color="#CCCCCC"
        )
        label_widget.pack(pady=(15, 5))
        
        value_widget = ctk.CTkLabel(
            card,
            text=value,
            font=("Helvetica", 36, "bold"),
            text_color=color
        )
        value_widget.pack(pady=(5, 15))
    
    def refresh(self):
        """Refresh dashboard statistics"""
        # Clear current widgets
        for widget in self.winfo_children():
            widget.destroy()
        
        # Recreate widgets with updated data
        self.create_widgets()
