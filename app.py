"""
app.py — Entry point for Bibliothèque Intelligente avec Chatbot IA
Run this file to start the application:
    python app.py
"""
from main import LibraryApp

if __name__ == "__main__":
    app = LibraryApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
