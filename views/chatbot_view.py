import customtkinter as ctk
import threading
import json
import urllib.request
import urllib.error
import datetime
import re
import os


# ══════════════════════════════════════════════════════════════════════════════
#  🔑  GROQ API KEY  (free at console.groq.com)
# ══════════════════════════════════════════════════════════════════════════════

GROQ_MODEL   = "llama-3.3-70b-versatile"
GROQ_URL     = "https://api.groq.com/openai/v1/chat/completions"
# ══════════════════════════════════════════════════════════════════════════════


class ChatbotView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.conversation_history = []
        self._api_error_msg = None          # stores last API error for display
        self._build_ui()
        self._welcome_message()

    # ══════════════════════════════════════════════════════════════════════════
    #  UI
    # ══════════════════════════════════════════════════════════════════════════

    def _build_ui(self):
        # ── Header ────────────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(25, 0))

        ctk.CTkLabel(
            header, text="🤖  Chatbot IA — Bibliothèque",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(side="left")

        # API status badge — green if key set
        _key_ok = bool(GROQ_API_KEY)
        badge_color = "#10B981" if _key_ok else "#EF4444"
        badge_text  = "● Groq IA Connecté" if _key_ok else "● Clé API manquante"
        ctk.CTkLabel(
            header, text=badge_text,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=badge_color
        ).pack(side="left", padx=18, pady=(6, 0))

        ctk.CTkButton(
            header, text="🧹  Nouvelle conversation",
            command=self.clear_conversation,
            fg_color="#6B7280", hover_color="#374151",
            height=34, corner_radius=8, width=200,
            font=ctk.CTkFont(size=12)
        ).pack(side="right")

        ctk.CTkLabel(
            self,
            text="Posez vos questions en langage naturel — disponibilité, recherche, recommandations…",
            font=ctk.CTkFont(size=13), text_color="#888"
        ).pack(anchor="w", padx=30, pady=(4, 14))

        # ── Chat container ────────────────────────────────────────────────────
        chat_container = ctk.CTkFrame(self, corner_radius=14)
        chat_container.pack(fill="both", expand=True, padx=30, pady=(0, 16))

        # Suggestion chips
        sug_row = ctk.CTkFrame(chat_container, fg_color="transparent")
        sug_row.pack(fill="x", padx=16, pady=(14, 2))
        ctk.CTkLabel(
            sug_row, text="Suggestions :",
            font=ctk.CTkFont(size=12), text_color="#888"
        ).pack(side="left", padx=(0, 8))

        chips = [
            "Livres disponibles",
            "Recommande-moi un roman",
            "Livres de Victor Hugo",
            "Statistiques bibliothèque",
            "Livre avec l'ID 1",
        ]
        for s in chips:
            ctk.CTkButton(
                sug_row, text=s,
                command=lambda t=s: self._send_suggestion(t),
                fg_color=("#dbeafe", "#1e3a5f"),
                text_color=("#1D4ED8", "#93C5FD"),
                hover_color=("#bfdbfe", "#1e2a4a"),
                height=28, corner_radius=20,
                font=ctk.CTkFont(size=11), width=0
            ).pack(side="left", padx=3)

        # Scrollable messages
        self.chat_scroll = ctk.CTkScrollableFrame(chat_container, fg_color="transparent")
        self.chat_scroll.pack(fill="both", expand=True, padx=8, pady=8)

        # Input bar
        input_bar = ctk.CTkFrame(
            chat_container, fg_color=("#ececec", "#1c1c1c"), corner_radius=12
        )
        input_bar.pack(fill="x", padx=12, pady=(0, 14))

        self.input_var = ctk.StringVar()
        self.input_entry = ctk.CTkEntry(
            input_bar, textvariable=self.input_var,
            placeholder_text="Ex: Est-ce que Les Misérables est disponible ?",
            height=44, corner_radius=10,
            font=ctk.CTkFont(size=13),
            border_width=0, fg_color="transparent"
        )
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(12, 4), pady=6)
        self.input_entry.bind("<Return>", lambda e: self.send_message())

        self.send_btn = ctk.CTkButton(
            input_bar, text="Envoyer ➤",
            command=self.send_message,
            fg_color="#2563EB", hover_color="#1D4ED8",
            height=36, width=120, corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.send_btn.pack(side="right", padx=(0, 10), pady=6)

    def _welcome_message(self):
        self._add_bot_message(
            "Bonjour ! Je suis votre assistant bibliothécaire IA propulsé par Groq 🤖\n\n"
            "Je peux vous aider à :\n"
            "🔍  Vérifier l'existence d'un livre (par titre ou ID)\n"
            "✅  Consulter la disponibilité d'un livre\n"
            "📖  Recommander des livres par genre ou auteur\n"
            "👤  Lister toutes les œuvres d'un auteur\n"
            "📊  Obtenir les statistiques de la collection\n\n"
            "Posez votre question librement en français !"
        )

    # ══════════════════════════════════════════════════════════════════════════
    #  Message bubbles
    # ══════════════════════════════════════════════════════════════════════════

    def _add_user_message(self, text):
        row = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        row.pack(fill="x", pady=5)

        right = ctk.CTkFrame(row, fg_color="transparent")
        right.pack(side="right", anchor="e")

        bubble = ctk.CTkFrame(right, fg_color="#2563EB", corner_radius=16)
        bubble.pack(anchor="e", padx=(80, 10))
        ctk.CTkLabel(
            bubble, text=text,
            font=ctk.CTkFont(size=13),
            text_color="#fff",
            wraplength=440, justify="left"
        ).pack(padx=14, pady=10)

        ctk.CTkLabel(
            right, text="Vous  " + self._ts(),
            font=ctk.CTkFont(size=10), text_color="#555"
        ).pack(anchor="e", padx=12)
        self._scroll_bottom()

    def _add_bot_message(self, text):
        row = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        row.pack(fill="x", pady=5)

        left = ctk.CTkFrame(row, fg_color="transparent")
        left.pack(side="left", anchor="w")

        name_row = ctk.CTkFrame(left, fg_color="transparent")
        name_row.pack(anchor="w")
        ctk.CTkLabel(name_row, text="🤖", font=ctk.CTkFont(size=18)).pack(side="left", padx=(8, 4))
        ctk.CTkLabel(
            name_row,
            text="Groq IA" if GROQ_API_KEY else "Assistant Local",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#10B981" if GROQ_API_KEY else "#F59E0B"
        ).pack(side="left")

        bubble = ctk.CTkFrame(left, fg_color=("#dbeafe", "#162032"), corner_radius=16)
        bubble.pack(anchor="w", padx=(10, 80), pady=(2, 0))
        ctk.CTkLabel(
            bubble, text=text,
            font=ctk.CTkFont(size=13),
            wraplength=500, justify="left"
        ).pack(padx=16, pady=12)

        ctk.CTkLabel(
            left, text=self._ts(),
            font=ctk.CTkFont(size=10), text_color="#555"
        ).pack(anchor="w", padx=12)
        self._scroll_bottom()

    def _add_error_message(self, text):
        """Red bubble for API errors — so user can see what went wrong."""
        row = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        row.pack(fill="x", pady=5)
        left = ctk.CTkFrame(row, fg_color="transparent")
        left.pack(side="left", anchor="w")
        bubble = ctk.CTkFrame(left, fg_color=("#fee2e2", "#2d1010"), corner_radius=16)
        bubble.pack(anchor="w", padx=(10, 80), pady=(2, 0))
        ctk.CTkLabel(
            bubble, text=text,
            font=ctk.CTkFont(size=12),
            text_color="#EF4444",
            wraplength=500, justify="left"
        ).pack(padx=16, pady=10)
        self._scroll_bottom()

    def _add_typing(self):
        row = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        row.pack(fill="x", pady=4)
        ctk.CTkLabel(row, text="🤖", font=ctk.CTkFont(size=20)).pack(side="left", padx=(8, 4))
        bubble = ctk.CTkFrame(row, fg_color=("#dbeafe", "#162032"), corner_radius=14)
        bubble.pack(side="left")
        ctk.CTkLabel(
            bubble,
            text="⏳  Claude est en train de répondre…",
            font=ctk.CTkFont(size=12), text_color="#6B7280"
        ).pack(padx=14, pady=10)
        self._scroll_bottom()
        return row

    def _remove_typing(self, w):
        try:
            w.pack_forget()
            w.destroy()
        except Exception:
            pass

    def _scroll_bottom(self):
        self.chat_scroll.after(60, lambda: self.chat_scroll._parent_canvas.yview_moveto(1.0))

    def _ts(self):
        return datetime.datetime.now().strftime("%H:%M")

    # ══════════════════════════════════════════════════════════════════════════
    #  Send / receive
    # ══════════════════════════════════════════════════════════════════════════

    def send_message(self):
        text = self.input_var.get().strip()
        if not text:
            return
        self.input_var.set("")
        self._add_user_message(text)
        self.conversation_history.append({"role": "user", "content": text})
        self.send_btn.configure(state="disabled", text="…")
        typing = self._add_typing()
        threading.Thread(
            target=self._get_response, args=(text, typing), daemon=True
        ).start()

    def _send_suggestion(self, text):
        self.input_var.set(text)
        self.send_message()

    def _get_response(self, user_msg, typing):
        reply        = None
        api_used     = False
        error_detail = None

        if GROQ_API_KEY:
            reply, error_detail = self._call_groq_api(user_msg)
            if reply:
                api_used = True

        if not reply:
            reply = self._smart_local_response(user_msg)

        self.conversation_history.append({"role": "assistant", "content": reply})
        self.after(0, lambda: self._deliver(reply, typing, error_detail, api_used))

    def _deliver(self, reply, typing, error_detail, api_used):
        self._remove_typing(typing)
        # If API failed, show the error in red first so user knows
        if error_detail and not api_used:
            self._add_error_message(f"⚠️  API Groq indisponible — utilisation du moteur local.\nDétail : {error_detail}")
        self._add_bot_message(reply)
        self.send_btn.configure(state="normal", text="Envoyer ➤")

    # ══════════════════════════════════════════════════════════════════════════
    #  Groq API call — returns (text, error) tuple
    # ══════════════════════════════════════════════════════════════════════════

    def _call_groq_api(self, user_msg):
        """
        Returns (reply_text, None)  on success
        Returns (None, error_string) on failure
        """
        try:
            stats  = self.controller.get_stats()
            books  = self.controller.get_all_books()

            catalog = "\n".join([
                f"ID {b.id_livre} | «{b.titre}» | Auteur: {b.auteur} | "
                f"Catégorie: {b.categorie} | Année: {b.annee_publication or 'N/A'} | "
                f"Statut: {b.statut} | Quantité: {b.quantite_disponible}"
                for b in books
            ])

            system_prompt = f"""Tu es un assistant bibliothécaire IA expert et chaleureux pour la "Bibliothèque Intelligente".
Tu parles UNIQUEMENT en français. Tes réponses sont naturelles, précises et bien structurées.

=== STATISTIQUES EN TEMPS RÉEL ===
- Total livres   : {stats['total']}
- Disponibles    : {stats['disponible']}
- Empruntés      : {stats['emprunte']}
- Réservés       : {stats['reserve']}

=== CATALOGUE COMPLET ===
{catalog}

=== RÈGLES IMPORTANTES ===
1. Réponds TOUJOURS en français naturel et conversationnel
2. Pour chaque livre mentionné, indique : titre, auteur, statut, quantité disponible
3. Si un livre est emprunté ou réservé, dis-le clairement et propose une alternative
4. Pour les recommandations, explique POURQUOI tu recommandes ce livre
5. Si on cherche par ID, trouve le livre exact dans le catalogue
6. Utilise des emojis pour rendre la réponse agréable (📚 ✅ 📤 🔖 📖 etc.)
7. Sois précis avec les chiffres (quantités, années, IDs)
8. Si la question ne concerne pas la bibliothèque, redirige poliment
"""

            messages = [{"role": "system", "content": system_prompt}]
            messages += self.conversation_history[-10:]

            payload = json.dumps({
                "model": GROQ_MODEL,
                "messages": messages,
                "max_tokens": 1024,
                "temperature": 0.7,
            }).encode("utf-8")

            req = urllib.request.Request(
                GROQ_URL,
                data=payload,
                headers={
                    "Content-Type":  "application/json",
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "application/json",
                },
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text = data["choices"][0]["message"]["content"]
                print(f"[Groq API] ✅ Success — {len(text)} chars")
                return text, None

        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8")
            msg  = f"HTTP {e.code}: {body[:200]}"
            print(f"[Groq API] ❌ {msg}")
            return None, msg

        except urllib.error.URLError as e:
            msg = f"Connexion échouée: {e.reason}"
            print(f"[Groq API] ❌ {msg}")
            return None, msg

        except KeyError as e:
            msg = f"Réponse API inattendue — clé manquante: {e}"
            print(f"[Groq API] ❌ {msg}")
            return None, msg

        except Exception as e:
            msg = f"{type(e).__name__}: {e}"
            print(f"[Groq API] ❌ {msg}")
            return None, msg

    # ══════════════════════════════════════════════════════════════════════════
    #  Smart local NLP engine  (fallback — no API needed)
    # ══════════════════════════════════════════════════════════════════════════

    def _smart_local_response(self, msg: str) -> str:
        ml = msg.lower().strip()
        books_all = self.controller.get_all_books()

        # 1. Search by ID
        id_match = re.search(r"\b(?:id|numéro|numero|n°)\s*[:#]?\s*(\d+)\b", ml)
        if id_match:
            bid = int(id_match.group(1))
            b = self.controller.get_book_by_id(bid)
            if b:
                icon = "✅" if b.statut == "disponible" else ("📤" if b.statut == "emprunté" else "🔖")
                return (
                    f"📖  Livre trouvé (ID {b.id_livre}) :\n\n"
                    f"  📕  Titre     : {b.titre}\n"
                    f"  ✍️   Auteur    : {b.auteur}\n"
                    f"  🗂️   Catégorie : {b.categorie}\n"
                    f"  📅  Année     : {b.annee_publication or 'Inconnue'}\n"
                    f"  {icon}  Statut   : {b.statut.capitalize()}\n"
                    f"  📦  Quantité  : {b.quantite_disponible} exemplaire(s)"
                )
            return f"❌  Aucun livre avec l'ID {bid} trouvé."

        # 2. Statistics
        if any(w in ml for w in ["statistique", "combien", "total", "bilan", "état", "etat", "résumé"]):
            s = self.controller.get_stats()
            cats = {}
            for b in books_all:
                cats[b.categorie] = cats.get(b.categorie, 0) + 1
            top_cats = sorted(cats.items(), key=lambda x: -x[1])[:4]
            cat_lines = "\n".join([f"    • {c} : {n} livre(s)" for c, n in top_cats])
            return (
                f"📊  Statistiques de la bibliothèque :\n\n"
                f"  📚  Total livres  : {s['total']}\n"
                f"  ✅  Disponibles   : {s['disponible']}\n"
                f"  📤  Empruntés     : {s['emprunte']}\n"
                f"  🔖  Réservés      : {s['reserve']}\n\n"
                f"  Top catégories :\n{cat_lines}"
            )

        # 3. All available books
        if re.search(r"\b(tous|liste|lister|affich|montre|quels?)\b.*\bdisponible", ml) or \
           ml in ["livres disponibles", "disponibles"]:
            avail = [b for b in books_all if b.statut == "disponible"]
            if not avail:
                return "😔  Aucun livre disponible pour le moment."
            lines = "\n".join([
                f"  {i+1}. «{b.titre}» — {b.auteur}  ({b.categorie})  ×{b.quantite_disponible}"
                for i, b in enumerate(avail)
            ])
            return f"✅  {len(avail)} livre(s) disponible(s) :\n\n{lines}"

        # 4. Author search
        author_match = re.search(
            r"(?:de|par|auteur|livres?\s+de|œuvres?\s+de|oeuvres?\s+de)\s+"
            r"([A-ZÀ-Ö][a-zà-ö]+(?:\s+[A-ZÀ-Öa-zà-ö]+)*)",
            msg
        )
        if author_match:
            name = author_match.group(1).strip()
            found = self.controller.search_by_author(name)
            if found:
                lines = []
                for i, b in enumerate(found, 1):
                    icon = "✅" if b.statut == "disponible" else ("📤" if b.statut == "emprunté" else "🔖")
                    lines.append(f"  {i}. «{b.titre}»  {icon} {b.statut.capitalize()} ({b.quantite_disponible} ex.)")
                return f"👤  Œuvres de {name} dans notre catalogue :\n\n" + "\n".join(lines)
            return f"❌  Aucun livre de «{name}» trouvé."

        # 5. Genre / category
        GENRE_MAP = {
            "roman historique": "Roman historique",
            "science-fiction":  "Science-Fiction",
            "science fiction":  "Science-Fiction",
            "sf":               "Science-Fiction",
            "informatique":     "Informatique",
            "fiction":          "Fiction",
            "roman":            "Roman",
            "histoire":         "Histoire",
            "philosophie":      "Philosophie",
            "poésie":           "Poésie",
            "poesie":           "Poésie",
            "biographie":       "Biographie",
        }
        for kw, cat in GENRE_MAP.items():
            if kw in ml:
                found = self.controller.get_by_category(cat)
                if found:
                    lines = []
                    for i, b in enumerate(found, 1):
                        icon = "✅" if b.statut == "disponible" else ("📤" if b.statut == "emprunté" else "🔖")
                        lines.append(f"  {i}. «{b.titre}» — {b.auteur}  {icon} {b.statut}  (×{b.quantite_disponible})")
                    return f"🗂️  Livres «{cat}» :\n\n" + "\n".join(lines)
                return f"😔  Aucun livre en catégorie «{cat}»."

        # 6. Availability for a specific title
        if any(w in ml for w in ["disponible", "emprunter", "peut-on", "puis-je", "emprunté"]):
            found = self._search_title_in_msg(msg, books_all)
            if found:
                b = found[0]
                if b.statut == "disponible":
                    return (
                        f"✅  «{b.titre}» est disponible !\n\n"
                        f"  ✍️  Auteur     : {b.auteur}\n"
                        f"  📦  Exemplaires: {b.quantite_disponible}\n\n"
                        f"Vous pouvez l'emprunter dès maintenant 😊"
                    )
                elif b.statut == "emprunté":
                    return (
                        f"📤  «{b.titre}» est actuellement emprunté.\n\n"
                        f"  ✍️  Auteur : {b.auteur}\n"
                        f"  ❌  Statut : Emprunté\n\n"
                        f"Souhaitez-vous le réserver ?"
                    )
                else:
                    return (
                        f"🔖  «{b.titre}» est actuellement réservé.\n\n"
                        f"  ✍️  Auteur : {b.auteur}\n"
                        f"  ⏳  Il sera disponible prochainement."
                    )

        # 7. Recommendations
        if any(w in ml for w in ["recommand", "suggère", "suggere", "propose", "conseil",
                                   "meilleur", "je cherche", "je veux"]):
            for kw, cat in GENRE_MAP.items():
                if kw in ml:
                    pool = [b for b in books_all if cat.lower() in b.categorie.lower()]
                    if pool:
                        return self._format_recommendations(pool, f"genre «{cat}»")
            pool = sorted(books_all, key=lambda b: (b.statut != "disponible", b.titre))
            return self._format_recommendations(pool[:6], "notre catalogue")

        # 8. Existence check
        if any(w in ml for w in ["existe", "avez-vous", "avez vous", "est-ce que",
                                   "cherche", "trouve", "trouver"]):
            found = self._search_title_in_msg(msg, books_all)
            if found:
                b = found[0]
                icon = "✅" if b.statut == "disponible" else ("📤" if b.statut == "emprunté" else "🔖")
                return (
                    f"📖  Oui, ce livre existe !\n\n"
                    f"  📕  Titre     : {b.titre}\n"
                    f"  ✍️  Auteur    : {b.auteur}\n"
                    f"  📅  Année     : {b.annee_publication or 'Inconnue'}\n"
                    f"  {icon}  Statut   : {b.statut.capitalize()}\n"
                    f"  📦  Quantité  : {b.quantite_disponible} exemplaire(s)"
                )

        # 9. Generic title search
        found = self._search_title_in_msg(msg, books_all)
        if found:
            b = found[0]
            icon = "✅" if b.statut == "disponible" else ("📤" if b.statut == "emprunté" else "🔖")
            extras = ""
            if len(found) > 1:
                extras = "\n\nRésultats similaires :\n" + "\n".join(
                    [f"  • «{x.titre}» — {x.auteur}" for x in found[1:4]]
                )
            return (
                f"📖  J'ai trouvé : «{b.titre}»\n\n"
                f"  ✍️  Auteur    : {b.auteur}\n"
                f"  🗂️  Catégorie : {b.categorie}\n"
                f"  📅  Année     : {b.annee_publication or 'Inconnue'}\n"
                f"  {icon}  Statut   : {b.statut.capitalize()}\n"
                f"  📦  Quantité  : {b.quantite_disponible} exemplaire(s)"
                + extras
            )

        # 10. Greetings
        if any(w in ml for w in ["bonjour", "salut", "bonsoir", "hello", "hi"]):
            return (
                "Bonjour ! 😊  Je suis votre assistant bibliothécaire Claude IA.\n\n"
                "Comment puis-je vous aider ?\n"
                "• Chercher un livre par titre ou ID\n"
                "• Vérifier la disponibilité\n"
                "• Recommandations par genre\n"
                "• Statistiques de la bibliothèque"
            )

        # 11. Help
        if any(w in ml for w in ["aide", "help", "comment", "que peux-tu"]):
            return (
                "🆘  Ce que je peux faire :\n\n"
                "🔍  «Est-ce que Dune existe ?»\n"
                "🔍  «Livre avec l'ID 5»\n"
                "✅  «Les Misérables est-il disponible ?»\n"
                "📚  «Recommande-moi un roman historique»\n"
                "👤  «Livres de Victor Hugo»\n"
                "📊  «Combien de livres avez-vous ?»"
            )

        # 12. Default
        s = self.controller.get_stats()
        return (
            f"🤔  Je n'ai pas bien compris.\n\n"
            f"La bibliothèque contient {s['total']} livres ({s['disponible']} disponibles).\n\n"
            f"Exemples :\n"
            f"  • «Est-ce que 1984 est disponible ?»\n"
            f"  • «Recommande-moi un roman»\n"
            f"  • «Livres de Victor Hugo»\n"
            f"  • «Livre avec l'ID 3»"
        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _search_title_in_msg(self, msg, books_all):
        ml = msg.lower()
        stop = {"le","la","les","un","une","des","de","du","est","ce","que","qui",
                "avec","dans","pour","sur","par","je","tu","il","elle","nous","vous",
                "ils","elles","et","ou","mais","si","the","a","avez","peut","puis",
                "cherche","livre","livres","auteur","titre","existe","disponible",
                "emprunté","réservé","quel","quels","est-ce"}
        scored = []
        for b in books_all:
            title_words = [
                w for w in re.sub(r"[^a-zà-ö\s]", "", b.titre.lower()).split()
                if w not in stop and len(w) > 2
            ]
            author_words = [
                w for w in b.auteur.lower().split()
                if w not in stop and len(w) > 2
            ]
            score = (sum(1   for w in title_words  if w in ml) +
                     sum(0.5 for w in author_words if w in ml))
            if score > 0:
                scored.append((score, b))
        scored.sort(key=lambda x: -x[0])
        return [b for _, b in scored]

    def _format_recommendations(self, pool, context_label):
        lines = []
        for i, b in enumerate(pool[:5], 1):
            icon = "✅" if b.statut == "disponible" else ("📤" if b.statut == "emprunté" else "🔖")
            lines.append(
                f"  {i}. «{b.titre}» — {b.auteur}\n"
                f"      {icon} {b.statut.capitalize()}  |  {b.categorie}"
            )
        return f"📚  Recommandations depuis {context_label} :\n\n" + "\n\n".join(lines)

    def clear_conversation(self):
        for w in self.chat_scroll.winfo_children():
            w.destroy()
        self.conversation_history.clear()
        self._welcome_message()