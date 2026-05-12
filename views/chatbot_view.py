import customtkinter as ctk
from tkinter import scrolledtext
import threading
from datetime import datetime

class ChatbotView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.chat_history = []
        self.create_widgets()
        self.add_welcome_message()
    
    def create_widgets(self):
        """Create chatbot widgets"""
        # Title
        title = ctk.CTkLabel(
            self,
            text="Chatbot Bibliothèque IA",
            font=("Helvetica", 28, "bold"),
            text_color="#FFFFFF"
        )
        title.pack(pady=(0, 20))
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            self,
            wrap='word',
            font=("Helvetica", 11),
            bg='#2a2a2a',
            fg='#FFFFFF',
            height=20,
            padx=10,
            pady=10,
            insertbackground='#0084FF',
            relief='flat',
            borderwidth=0
        )
        self.chat_display.pack(fill="both", expand=True, pady=(0, 15))
        self.chat_display.config(state='disabled')
        
        # Configure tags for styling
        self.chat_display.tag_config('user', foreground='#0084FF', font=("Helvetica", 11, "bold"))
        self.chat_display.tag_config('bot', foreground='#00D084', font=("Helvetica", 11, "bold"))
        self.chat_display.tag_config('timestamp', foreground='#888888', font=("Helvetica", 9))
        self.chat_display.tag_config('user_message', foreground='#FFFFFF', lmargin2=20)
        self.chat_display.tag_config('bot_message', foreground='#CCCCCC', lmargin2=20)
        
        # Input frame
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(fill="x")
        
        self.input_text = ctk.CTkEntry(
            input_frame,
            placeholder_text="Posez une question à propos de la bibliothèque...",
            height=40,
            border_width=1,
            border_color="#0084FF"
        )
        self.input_text.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self.input_text.bind('<Return>', lambda e: self.send_message())
        
        send_btn = ctk.CTkButton(
            input_frame,
            text="Envoyer",
            command=self.send_message,
            width=100,
            height=40,
            fg_color="#0084FF",
            hover_color="#0066CC"
        )
        send_btn.pack(side="right")
    
    def add_welcome_message(self):
        """Add welcome message to chat"""
        self.chat_display.config(state='normal')
        
        self.chat_display.insert('end', '[Assistant Bibliothèque IA]\n', 'bot')
        self.chat_display.insert('end', f'  {self._get_time()}\n', 'timestamp')
        self.chat_display.insert('end', 'Bonjour! Je suis votre assistant IA pour la bibliothèque. ', 'bot_message')
        self.chat_display.insert('end', 'Je peux vous aider à:\n', 'bot_message')
        self.chat_display.insert('end', '• Trouver des livres par titre, auteur ou catégorie\n', 'bot_message')
        self.chat_display.insert('end', '• Obtenir des statistiques sur la bibliothèque\n', 'bot_message')
        self.chat_display.insert('end', '• Recommander des livres\n', 'bot_message')
        self.chat_display.insert('end', '• Vous aider avec la gestion des emprunts\n\n', 'bot_message')
        
        self.chat_display.config(state='disabled')
    
    def send_message(self):
        """Send a message to the chatbot"""
        user_input = self.input_text.get().strip()
        if not user_input:
            return
        
        # Display user message
        self.chat_display.config(state='normal')
        self.chat_display.insert('end', '[Vous]\n', 'user')
        self.chat_display.insert('end', f'  {self._get_time()}\n', 'timestamp')
        self.chat_display.insert('end', f'{user_input}\n\n', 'user_message')
        self.chat_display.config(state='disabled')
        self.chat_display.see('end')
        
        # Clear input
        self.input_text.delete(0, 'end')
        
        # Get bot response in a separate thread to avoid blocking UI
        threading.Thread(target=self._get_bot_response, args=(user_input,), daemon=True).start()
    
    def _get_bot_response(self, user_input):
        """Get response from the chatbot"""
        # Simulate AI responses based on user input
        response = self._generate_response(user_input)
        
        # Display bot response
        self.chat_display.config(state='normal')
        self.chat_display.insert('end', '[Assistant Bibliothèque IA]\n', 'bot')
        self.chat_display.insert('end', f'  {self._get_time()}\n', 'timestamp')
        self.chat_display.insert('end', f'{response}\n\n', 'bot_message')
        self.chat_display.config(state='disabled')
        self.chat_display.see('end')
    
    def _generate_response(self, user_input):
        """Generate a response based on user input"""
        user_input_lower = user_input.lower()
        
        # Get library statistics
        stats = self.controller.get_statistics()
        
        # Check for specific patterns and respond accordingly
        if 'combien' in user_input_lower and ('livre' in user_input_lower or 'total' in user_input_lower):
            return f"La bibliothèque contient actuellement {stats['total_books']} livres."
        
        elif 'disponible' in user_input_lower:
            return f"Il y a {stats['available_books']} livres disponibles pour l'emprunt."
        
        elif 'auteur' in user_input_lower:
            return f"La bibliothèque a {stats['total_authors']} auteurs différents enregistrés."
        
        elif 'catégorie' in user_input_lower or 'categorie' in user_input_lower:
            return f"Il existe {stats['total_categories']} catégories de livres dans la bibliothèque."
        
        elif 'recherche' in user_input_lower or 'chercher' in user_input_lower:
            return "Pour rechercher un livre, allez dans l'onglet 'Gestion des Livres' et utilisez la barre de recherche. Vous pouvez rechercher par titre, auteur ou catégorie."
        
        elif 'ajouter' in user_input_lower or 'nouveau' in user_input_lower:
            return "Pour ajouter un nouveau livre, allez dans 'Gestion des Livres', remplissez le formulaire avec les détails du livre et cliquez sur 'Ajouter Livre'."
        
        elif 'supprimer' in user_input_lower or 'effacer' in user_input_lower:
            return "Pour supprimer un livre, allez dans 'Gestion des Livres', sélectionnez le livre en double-cliquant et cliquez sur 'Supprimer'."
        
        elif 'modifier' in user_input_lower or 'éditer' in user_input_lower:
            return "Pour modifier un livre, double-cliquez sur le livre dans la liste, modifiez les informations et cliquez sur 'Modifier'."
        
        elif 'statistique' in user_input_lower or 'statistiques' in user_input_lower:
            return f"Voici les statistiques actuelles:\n• Total: {stats['total_books']} livres\n• Disponibles: {stats['available_books']}\n• Auteurs: {stats['total_authors']}\n• Catégories: {stats['total_categories']}"
        
        elif 'bonjour' in user_input_lower or 'hi' in user_input_lower or 'salut' in user_input_lower:
            return "Bonjour! Comment puis-je vous aider avec votre bibliothèque?"
        
        elif 'aide' in user_input_lower or 'help' in user_input_lower:
            return "Je peux vous aider avec:\n• La gestion des livres\n• La recherche de livres\n• Les statistiques de la bibliothèque\n• Posez simplement votre question!"
        
        else:
            return "Je comprends que vous posez une question sur la bibliothèque. Pourriez-vous être plus spécifique? Vous pouvez demander des informations sur les livres, les auteurs, les catégories ou comment utiliser l'application."
    
    def _get_time(self):
        """Get current time in HH:MM format"""
        return datetime.now().strftime("%H:%M")
