"""
from views.app import LibraryApp
if __name__ == "__main__":
    app = LibraryApp()
    app.mainloop()
"""
import customtkinter as ctk
from controllers.book_controller import Book_controller
from views.dashboard_view import DashboardView
from views.book_management_view import BookManagementView
from views.chatbot_view import ChatbotView
from views.settings_view import SettingsView

class LibraryApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Bibliothèque Intelligente avec Chatbot IA")
        self.geometry("1200x700")
        self.iconbitmap("", default="")
        
        # Initialize controller
        self.controller = Book_controller()
        
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        
        
        # Store references to views
        self.views = {}
        self.current_view = None
        
        # Create main layout
        self.create_layout()
    def create_layout(self):
        """Create the main application layout"""
        # Main container
        main_container = ctk.CTkFrame(self, fg_color="#1a1a1a")
        main_container.pack(fill="both", expand=True)
        
        # Sidebar
        sidebar = ctk.CTkFrame(main_container, fg_color="#1a1a1a", width=200)
        sidebar.pack(side="left", fill="y", padx=0, pady=0)
        sidebar.pack_propagate(False)
        
        # App title in sidebar
        app_title = ctk.CTkLabel(
            sidebar,
            text="📚 Bibliothèque",
            font=("Helvetica", 18, "bold"),
            text_color="#FFFFFF"
        )
        app_title.pack(pady=(20, 30), padx=10)
        
        # Navigation buttons
        nav_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        nav_frame.pack(fill="x", padx=10, pady=10)
        
        self.nav_buttons = {}
        nav_items = [
            ("Tableau de Bord", "dashboard"),
            ("Gestion des Livres", "books"),
            ("Chatbot IA", "chatbot"),
            ("Paramètres", "settings")
        ]
        
        for label, key in nav_items:
            btn = ctk.CTkButton(
                nav_frame,
                text=label,
                command=lambda k=key: self.switch_view(k),
                fg_color="#0084FF",
                hover_color="#0066CC",
                height=40,
                corner_radius=8,
                font=("Helvetica", 11)
            )
            btn.pack(fill="x", pady=8)
            self.nav_buttons[key] = btn
        
        # Theme toggle
        theme_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        theme_frame.pack(fill="x", padx=10, pady=(40, 20))
        
        theme_label = ctk.CTkLabel(
            theme_frame,
            text="Thème:",
            font=("Helvetica", 10),
            text_color="#CCCCCC"
        )
        theme_label.pack(side="left", padx=(0, 10))
        
        self.theme_var = ctk.StringVar(value="dark")
        theme_menu = ctk.CTkComboBox(
            theme_frame,
            values=["dark", "light"],
            variable=self.theme_var,
            command=self.change_theme,
            width=80,
            height=30
        )
        theme_menu.pack(side="left")
        
        # Content area
        self.content_frame = ctk.CTkFrame(main_container, fg_color="#1a1a1a")
        self.content_frame.pack(side="right", fill="both", expand=True)
        
        # Initialize views
        self.views['dashboard'] = DashboardView(self.content_frame, self.controller)
        self.views['books'] = BookManagementView(self.content_frame, self.controller)
        self.views['chatbot'] = ChatbotView(self.content_frame, self.controller)
        self.views['settings'] = SettingsView(self.content_frame, self.controller, self.change_theme)
        
        # Show dashboard by default
        self.switch_view('dashboard')
    
    def switch_view(self, view_key):
        """Switch between different views"""
        # Hide current view
        if self.current_view:
            self.views[self.current_view].pack_forget()
        
        # Show new view
        self.views[view_key].pack(fill="both", expand=True)
        self.current_view = view_key
        
        # Update button colors
        for key, btn in self.nav_buttons.items():
            if key == view_key:
                btn.configure(fg_color="#0084FF", text_color="#FFFFFF")
            else:
                btn.configure(fg_color="#2a2a2a", text_color="#CCCCCC")
        
        # Refresh dashboard when switching to it
        if view_key == 'dashboard':
            self.views['dashboard'].refresh()
    
    def change_theme(self, theme):
        """Change application theme"""
        if theme == "dark":
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")
    
    def on_closing(self):
        """Handle application closing"""
        self.controller.close()
        self.destroy()

if __name__ == "__main__":
    app = LibraryApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
