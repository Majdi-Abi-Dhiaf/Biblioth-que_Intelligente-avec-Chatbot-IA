import customtkinter as ctk
import threading
import json
import urllib.request
import datetime


class ChatbotView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.conversation_history = []
        self._build_ui()
        self._welcome_message()

    # ─── UI Build ─────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(25, 0))
        ctk.CTkLabel(header, text="🤖  Chatbot IA — Bibliothèque",
                     font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")

        clear_btn = ctk.CTkButton(
            header, text="🧹  Nouvelle conversation",
            command=self.clear_conversation,
            fg_color="#6B7280", hover_color="#374151",
            height=34, corner_radius=8, width=190,
            font=ctk.CTkFont(size=12)
        )
        clear_btn.pack(side="right")

        ctk.CTkLabel(self, text="Posez des questions sur vos livres, disponibilités, recommandations…",
                     font=ctk.CTkFont(size=13), text_color="#888").pack(anchor="w", padx=30, pady=(4, 16))

        # Main chat area
        chat_container = ctk.CTkFrame(self, corner_radius=14)
        chat_container.pack(fill="both", expand=True, padx=30, pady=(0, 0))

        # Quick suggestions
        suggestions_frame = ctk.CTkFrame(chat_container, fg_color="transparent")
        suggestions_frame.pack(fill="x", padx=16, pady=(14, 0))
        ctk.CTkLabel(suggestions_frame, text="Suggestions :", font=ctk.CTkFont(size=12),
                     text_color="#888").pack(side="left", padx=(0, 8))

        suggestions = [
            "Livres disponibles",
            "Recommande-moi un roman",
            "Livres de science-fiction",
            "Combien de livres ?",
        ]
        for s in suggestions:
            btn = ctk.CTkButton(
                suggestions_frame, text=s,
                command=lambda t=s: self._send_suggestion(t),
                fg_color=("#e0e7ff", "#1e2a3a"),
                text_color=("#3B82F6", "#93C5FD"),
                hover_color=("#c7d2fe", "#263547"),
                height=28, corner_radius=20,
                font=ctk.CTkFont(size=11), width=0
            )
            btn.pack(side="left", padx=4)

        # Scrollable chat messages
        self.chat_scroll = ctk.CTkScrollableFrame(chat_container, fg_color="transparent")
        self.chat_scroll.pack(fill="both", expand=True, padx=8, pady=12)

        # Input area
        input_frame = ctk.CTkFrame(chat_container, fg_color=("#f0f0f0", "#1e1e1e"), corner_radius=12)
        input_frame.pack(fill="x", padx=12, pady=(0, 14))

        self.input_var = ctk.StringVar()
        self.input_entry = ctk.CTkEntry(
            input_frame,
            textvariable=self.input_var,
            placeholder_text="Écrivez votre message… (Ex: Est-ce que le livre 'Dune' est disponible ?)",
            height=44, corner_radius=10,
            font=ctk.CTkFont(size=13),
            border_width=0, fg_color="transparent"
        )
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(10, 4), pady=6)
        self.input_entry.bind("<Return>", lambda e: self.send_message())

        self.send_btn = ctk.CTkButton(
            input_frame, text="Envoyer ➤",
            command=self.send_message,
            fg_color="#3B82F6", hover_color="#1D4ED8",
            height=36, width=110, corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.send_btn.pack(side="right", padx=(0, 8), pady=6)

    def _welcome_message(self):
        welcome = (
            "Bonjour ! Je suis votre assistant bibliothécaire IA 📚\n\n"
            "Je peux vous aider à :\n"
            "• Vérifier si un livre existe dans la bibliothèque\n"
            "• Consulter la disponibilité d'un livre\n"
            "• Recommander des livres par genre ou auteur\n"
            "• Rechercher par auteur, catégorie ou titre\n"
            "• Obtenir des statistiques sur la collection\n\n"
            "Comment puis-je vous aider ?"
        )
        self._add_bot_message(welcome)

    # ─── Message Rendering ────────────────────────────────────────────────────

    def _add_user_message(self, text):
        row = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        row.pack(fill="x", pady=4)

        bubble = ctk.CTkFrame(row, fg_color="#3B82F6", corner_radius=14)
        bubble.pack(side="right", padx=(80, 8))

        ctk.CTkLabel(
            bubble, text=text,
            font=ctk.CTkFont(size=13),
            text_color="#ffffff",
            wraplength=420, justify="left"
        ).pack(padx=14, pady=10)

        ts = ctk.CTkLabel(row, text=self._ts(), font=ctk.CTkFont(size=10), text_color="#666")
        ts.pack(side="right", padx=(0, 8), anchor="s", pady=(0, 4))
        self._scroll_to_bottom()

    def _add_bot_message(self, text):
        row = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        row.pack(fill="x", pady=4)

        avatar = ctk.CTkLabel(row, text="🤖", font=ctk.CTkFont(size=20))
        avatar.pack(side="left", padx=(8, 4), anchor="n", pady=6)

        bubble = ctk.CTkFrame(row, fg_color=("#e8f0fe", "#1e2a3a"), corner_radius=14)
        bubble.pack(side="left", padx=(0, 80))

        ctk.CTkLabel(
            bubble, text=text,
            font=ctk.CTkFont(size=13),
            wraplength=460, justify="left"
        ).pack(padx=14, pady=10)

        ts = ctk.CTkLabel(row, text=self._ts(), font=ctk.CTkFont(size=10), text_color="#666")
        ts.pack(side="left", padx=4, anchor="s", pady=(0, 4))
        self._scroll_to_bottom()

    def _add_typing_indicator(self):
        row = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        row.pack(fill="x", pady=4)
        row._is_typing = True

        ctk.CTkLabel(row, text="🤖", font=ctk.CTkFont(size=20)).pack(side="left", padx=(8, 4), anchor="n", pady=6)
        bubble = ctk.CTkFrame(row, fg_color=("#e8f0fe", "#1e2a3a"), corner_radius=14)
        bubble.pack(side="left")
        ctk.CTkLabel(bubble, text="✦ En train de répondre…",
                     font=ctk.CTkFont(size=12), text_color="#888").pack(padx=14, pady=10)
        self._scroll_to_bottom()
        return row

    def _remove_typing_indicator(self, indicator):
        try:
            indicator.pack_forget()
            indicator.destroy()
        except Exception:
            pass

    def _scroll_to_bottom(self):
        self.chat_scroll.after(50, lambda: self.chat_scroll._parent_canvas.yview_moveto(1.0))

    def _ts(self):
        return datetime.datetime.now().strftime("%H:%M")

    # ─── Logic ────────────────────────────────────────────────────────────────

    def send_message(self):
        text = self.input_var.get().strip()
        if not text:
            return
        self.input_var.set("")
        self._add_user_message(text)
        self.conversation_history.append({"role": "user", "content": text})
        self.send_btn.configure(state="disabled", text="…")
        typing = self._add_typing_indicator()
        threading.Thread(target=self._get_ai_response, args=(text, typing), daemon=True).start()

    def _send_suggestion(self, text):
        self.input_var.set(text)
        self.send_message()

    def _get_ai_response(self, user_message, typing_indicator):
        try:
            # Gather library context
            stats = self.controller.get_stats()
            books = self.controller.get_all_books()
            book_list = "\n".join([
                f"- ID {b.id_livre}: «{b.titre}» par {b.auteur} ({b.categorie}, {b.annee_publication or 'N/A'}) — {b.statut}, qté: {b.quantite_disponible}"
                for b in books
            ])

            system_prompt = f"""Tu es un assistant bibliothécaire intelligent et serviable pour la "Bibliothèque Intelligente".
Tu as accès à la base de données complète de la bibliothèque.

STATISTIQUES ACTUELLES:
- Total livres: {stats['total']}
- Disponibles: {stats['disponible']}
- Empruntés: {stats['emprunte']}
- Réservés: {stats['reserve']}

CATALOGUE COMPLET:
{book_list}

INSTRUCTIONS:
- Réponds en français de manière claire, concise et professionnelle
- Si on te demande un livre spécifique, vérifie s'il existe dans le catalogue ci-dessus
- Si on demande des recommandations, base-toi sur le catalogue disponible
- Indique toujours le statut (disponible/emprunté/réservé) et la quantité
- Sois chaleureux et utile
- Ne réponds pas aux questions hors du contexte bibliothèque, redirige poliment
"""

            payload = json.dumps({
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1000,
                "system": system_prompt,
                "messages": self.conversation_history[-10:],  # last 10 turns
            }).encode("utf-8")

            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode("utf-8"))
                reply = result["content"][0]["text"]

        except Exception as e:
            # Fallback: local rule-based response
            reply = self._local_response(user_message)

        self.conversation_history.append({"role": "assistant", "content": reply})
        self.after(0, lambda: self._on_response(reply, typing_indicator))

    def _on_response(self, reply, typing_indicator):
        self._remove_typing_indicator(typing_indicator)
        self._add_bot_message(reply)
        self.send_btn.configure(state="normal", text="Envoyer ➤")

    def _local_response(self, msg):
        """Fallback rule-based chatbot when API is unavailable."""
        msg_lower = msg.lower()
        stats = self.controller.get_stats()

        if any(w in msg_lower for w in ["combien", "statistique", "total", "stats"]):
            return (
                f"📊 Voici les statistiques de la bibliothèque :\n\n"
                f"• Total livres : {stats['total']}\n"
                f"• Disponibles : {stats['disponible']}\n"
                f"• Empruntés : {stats['emprunte']}\n"
                f"• Réservés : {stats['reserve']}"
            )

        if any(w in msg_lower for w in ["disponible", "disponibles"]):
            books = [b for b in self.controller.get_all_books() if b.statut == "disponible"]
            if books:
                lines = "\n".join([f"• «{b.titre}» — {b.auteur}" for b in books[:8]])
                return f"✅ Livres disponibles ({len(books)}) :\n\n{lines}"
            return "Aucun livre disponible pour le moment."

        if "recommend" in msg_lower or "recommand" in msg_lower:
            books = self.controller.get_all_books()
            available = [b for b in books if b.statut == "disponible"][:5]
            if available:
                lines = "\n".join([f"• «{b.titre}» par {b.auteur} ({b.categorie})" for b in available])
                return f"📚 Je vous recommande ces livres disponibles :\n\n{lines}"
            return "Je n'ai pas de recommandations disponibles pour le moment."

        # Search by title
        for word in msg_lower.split():
            if len(word) > 4:
                results = self.controller.search_by_title(word)
                if results:
                    b = results[0]
                    return (
                        f"📖 J'ai trouvé : «{b.titre}» par {b.auteur}\n"
                        f"• Catégorie : {b.categorie}\n"
                        f"• Année : {b.annee_publication or 'Inconnue'}\n"
                        f"• Statut : {b.statut}\n"
                        f"• Quantité disponible : {b.quantite_disponible}"
                    )

        return (
            "Je ne suis pas sûr de comprendre votre question. Essayez de me demander :\n"
            "• La disponibilité d'un livre spécifique\n"
            "• Des recommandations par genre\n"
            "• Les statistiques de la bibliothèque\n"
            "• La recherche par auteur ou titre"
        )

    def clear_conversation(self):
        for widget in self.chat_scroll.winfo_children():
            widget.destroy()
        self.conversation_history.clear()
        self._welcome_message()
