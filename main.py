import sys
import os

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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
        self.minsize(900, 600)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.controller = Book_controller()
        self.views = {}
        self.current_view = None

        self._build_layout()

    # ─── Layout ───────────────────────────────────────────────────────────────

    def _build_layout(self):
        # Root container
        root = ctk.CTkFrame(self, fg_color=("#f0f0f0", "#141414"), corner_radius=0)
        root.pack(fill="both", expand=True)

        # ── Sidebar ───────────────────────────────────────────────────────────
        sidebar = ctk.CTkFrame(root, fg_color=("#1a1a2e", "#0d0d1a"), width=220, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Logo / title
        logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", padx=16, pady=(24, 8))

        ctk.CTkLabel(logo_frame, text="📚",
                     font=ctk.CTkFont(size=32)).pack()
        ctk.CTkLabel(logo_frame, text="Bibliothèque",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color="#ffffff").pack()
        ctk.CTkLabel(logo_frame, text="Intelligente",
                     font=ctk.CTkFont(size=12),
                     text_color="#6B7280").pack()

        # Divider
        ctk.CTkFrame(sidebar, height=1, fg_color="#2a2a4a").pack(fill="x", padx=16, pady=16)

        # Navigation
        nav_label = ctk.CTkLabel(sidebar, text="NAVIGATION",
                                 font=ctk.CTkFont(size=10, weight="bold"),
                                 text_color="#4B5563")
        nav_label.pack(anchor="w", padx=20, pady=(0, 8))

        self.nav_buttons = {}
        nav_items = [
            ("dashboard", "🏠", "Tableau de bord"),
            ("books",     "📚", "Gestion des livres"),
            ("chatbot",   "🤖", "Chatbot IA"),
            ("settings",  "⚙️", "Paramètres"),
        ]
        for key, icon, label in nav_items:
            btn = self._nav_button(sidebar, icon, label, key)
            self.nav_buttons[key] = btn

        # Divider
        ctk.CTkFrame(sidebar, height=1, fg_color="#2a2a4a").pack(fill="x", padx=16, pady=16)

        # Theme toggle at bottom
        theme_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        theme_frame.pack(fill="x", padx=14, side="bottom", pady=20)

        ctk.CTkLabel(theme_frame, text="Thème",
                     font=ctk.CTkFont(size=11),
                     text_color="#6B7280").pack(anchor="w", padx=6, pady=(0, 6))

        self.theme_seg = ctk.CTkSegmentedButton(
            theme_frame,
            values=["🌙 Sombre", "☀️ Clair"],
            command=self._on_theme_toggle,
            font=ctk.CTkFont(size=11),
            height=30
        )
        self.theme_seg.set("🌙 Sombre")
        self.theme_seg.pack(fill="x", padx=4)

        # DB status pill
        ctk.CTkFrame(sidebar, fg_color="transparent").pack(expand=True)
        status_pill = ctk.CTkFrame(sidebar, fg_color=("#0d2a1a", "#0d2a1a"), corner_radius=20)
        status_pill.pack(padx=16, pady=(0, 10), fill="x")
        ctk.CTkLabel(status_pill, text="● SQLite  Connectée",
                     font=ctk.CTkFont(size=11), text_color="#10B981").pack(pady=6)

        # ── Content area ──────────────────────────────────────────────────────
        self.content_frame = ctk.CTkFrame(root, fg_color="transparent", corner_radius=0)
        self.content_frame.pack(side="right", fill="both", expand=True)

        # Initialise all views
        self.views["dashboard"] = DashboardView(self.content_frame, self.controller)
        self.views["books"]     = BookManagementView(self.content_frame, self.controller)
        self.views["chatbot"]   = ChatbotView(self.content_frame, self.controller)
        self.views["settings"]  = SettingsView(self.content_frame, self.controller, self.change_theme)

        self.switch_view("dashboard")

    def _nav_button(self, parent, icon, label, key):
        frame = ctk.CTkFrame(parent, fg_color="transparent", corner_radius=10)
        frame.pack(fill="x", padx=10, pady=2)

        btn = ctk.CTkButton(
            frame,
            text=f"  {icon}  {label}",
            command=lambda k=key: self.switch_view(k),
            fg_color="transparent",
            hover_color=("#2a2a4a", "#1e1e3a"),
            text_color="#D1D5DB",
            anchor="w",
            height=42,
            corner_radius=10,
            font=ctk.CTkFont(size=13),
            border_width=0,
        )
        btn.pack(fill="x")
        return btn

    # ─── View Switching ───────────────────────────────────────────────────────

    def switch_view(self, view_key):
        if self.current_view:
            self.views[self.current_view].pack_forget()

        self.views[view_key].pack(fill="both", expand=True)
        self.current_view = view_key

        for key, btn in self.nav_buttons.items():
            if key == view_key:
                btn.configure(fg_color=("#2563EB", "#1D4ED8"), text_color="#ffffff")
            else:
                btn.configure(fg_color="transparent", text_color="#D1D5DB")

        if view_key == "dashboard":
            self.views["dashboard"].refresh()

    # ─── Theme ────────────────────────────────────────────────────────────────

    def _on_theme_toggle(self, value):
        mode = "dark" if "Sombre" in value else "light"
        self.change_theme(mode)

    def change_theme(self, theme):
        ctk.set_appearance_mode(theme)

    # ─── Close ────────────────────────────────────────────────────────────────

    def on_closing(self):
        self.controller.close()
        self.destroy()


if __name__ == "__main__":
    app = LibraryApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
