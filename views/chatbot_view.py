import customtkinter as ctk
import threading
import json
import urllib.request
import urllib.error
import datetime
import re
import os


# ─── Optional: set your API key here or in environment ────────────────────────
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")


class ChatbotView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.conversation_history = []
        self._build_ui()
        self._welcome_message()

    # ══════════════════════════════════════════════════════════════════════════
    #  UI
    # ══════════════════════════════════════════════════════════════════════════

    def _build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(25, 0))
        ctk.CTkLabel(header, text="🤖  Chatbot IA — Bibliothèque",
                     font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")

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

        chat_container = ctk.CTkFrame(self, corner_radius=14)
        chat_container.pack(fill="both", expand=True, padx=30, pady=(0, 16))

        # ── Suggestion chips ──────────────────────────────────────────────────
        sug_row = ctk.CTkFrame(chat_container, fg_color="transparent")
        sug_row.pack(fill="x", padx=16, pady=(14, 2))
        ctk.CTkLabel(sug_row, text="Suggestions :", font=ctk.CTkFont(size=12),
                     text_color="#888").pack(side="left", padx=(0, 8))

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

        # ── Chat scroll area ──────────────────────────────────────────────────
        self.chat_scroll = ctk.CTkScrollableFrame(chat_container, fg_color="transparent")
        self.chat_scroll.pack(fill="both", expand=True, padx=8, pady=8)

        # ── Input bar ─────────────────────────────────────────────────────────
        input_bar = ctk.CTkFrame(chat_container, fg_color=("#ececec", "#1c1c1c"), corner_radius=12)
        input_bar.pack(fill="x", padx=12, pady=(0, 14))

        self.input_var = ctk.StringVar()
        self.input_entry = ctk.CTkEntry(
            input_bar, textvariable=self.input_var,
            placeholder_text="Ex: Est-ce que Les Misérables est disponible ?  |  Recommande un roman",
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
            "Bonjour ! Je suis votre assistant bibliothécaire IA 📚\n\n"
            "Je peux vous aider à :\n"
            "🔍  Vérifier l'existence d'un livre (par titre ou ID)\n"
            "✅  Consulter la disponibilité d'un livre\n"
            "📖  Recommander des livres par genre ou auteur\n"
            "👤  Lister toutes les œuvres d'un auteur\n"
            "📊  Obtenir les statistiques de la collection\n\n"
            "Posez votre question librement !"
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
        ctk.CTkLabel(bubble, text=text, font=ctk.CTkFont(size=13),
                     text_color="#fff", wraplength=440, justify="left").pack(padx=14, pady=10)

        ctk.CTkLabel(right, text=self._ts(), font=ctk.CTkFont(size=10),
                     text_color="#555").pack(anchor="e", padx=12)
        self._scroll_bottom()

    def _add_bot_message(self, text):
        row = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        row.pack(fill="x", pady=5)

        left = ctk.CTkFrame(row, fg_color="transparent")
        left.pack(side="left", anchor="w")

        top = ctk.CTkFrame(left, fg_color="transparent")
        top.pack(anchor="w")

        ctk.CTkLabel(top, text="🤖", font=ctk.CTkFont(size=20)).pack(side="left", padx=(8, 4))
        ctk.CTkLabel(top, text="Assistant IA", font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="#6B7280").pack(side="left")

        bubble = ctk.CTkFrame(left, fg_color=("#dbeafe", "#162032"), corner_radius=16)
        bubble.pack(anchor="w", padx=(10, 80), pady=(2, 0))
        ctk.CTkLabel(bubble, text=text, font=ctk.CTkFont(size=13),
                     wraplength=480, justify="left").pack(padx=16, pady=12)

        ctk.CTkLabel(left, text=self._ts(), font=ctk.CTkFont(size=10),
                     text_color="#555").pack(anchor="w", padx=12)
        self._scroll_bottom()

    def _add_typing(self):
        row = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        row.pack(fill="x", pady=4)
        ctk.CTkLabel(row, text="🤖", font=ctk.CTkFont(size=20)).pack(side="left", padx=(8, 4))
        bubble = ctk.CTkFrame(row, fg_color=("#dbeafe", "#162032"), corner_radius=14)
        bubble.pack(side="left")
        ctk.CTkLabel(bubble, text="⏳  En train de répondre…",
                     font=ctk.CTkFont(size=12), text_color="#6B7280").pack(padx=14, pady=10)
        self._scroll_bottom()
        return row

    def _remove_typing(self, w):
        try:
            w.pack_forget(); w.destroy()
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
        # Try real Anthropic API first (only if key is set)
        if ANTHROPIC_API_KEY:
            reply = self._call_anthropic_api(user_msg)
        else:
            reply = None

        # Always fall back to our smart local engine
        if not reply:
            reply = self._smart_local_response(user_msg)

        self.conversation_history.append({"role": "assistant", "content": reply})
        self.after(0, lambda: self._deliver(reply, typing))

    def _deliver(self, reply, typing):
        self._remove_typing(typing)
        self._add_bot_message(reply)
        self.send_btn.configure(state="normal", text="Envoyer ➤")

    # ══════════════════════════════════════════════════════════════════════════
    #  Anthropic API call (optional — needs key)
    # ══════════════════════════════════════════════════════════════════════════

    def _call_anthropic_api(self, user_msg):
        try:
            stats  = self.controller.get_stats()
            books  = self.controller.get_all_books()
            catalog = "\n".join([
                f"ID {b.id_livre} | «{b.titre}» | {b.auteur} | {b.categorie} | {b.annee_publication or '?'} | {b.statut} | qté:{b.quantite_disponible}"
                for b in books
            ])
            system = (
                "Tu es un assistant bibliothécaire IA francophone expert.\n"
                f"Statistiques: total={stats['total']}, disponibles={stats['disponible']}, empruntés={stats['emprunte']}, réservés={stats['reserve']}\n\n"
                f"CATALOGUE:\n{catalog}\n\n"
                "Réponds en français, de façon précise et structurée. "
                "Pour chaque livre mentionné, indique toujours: titre, auteur, statut, quantité. "
                "Utilise des emojis pour rendre la réponse agréable."
            )
            payload = json.dumps({
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1024,
                "system": system,
                "messages": self.conversation_history[-8:],
            }).encode()

            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read())
                return data["content"][0]["text"]
        except Exception:
            return None

    # ══════════════════════════════════════════════════════════════════════════
    #  Smart local NLP engine  (works without any API key)
    # ══════════════════════════════════════════════════════════════════════════

    def _smart_local_response(self, msg: str) -> str:
        ml = msg.lower().strip()
        books_all = self.controller.get_all_books()

        # ── 1. Search by ID ───────────────────────────────────────────────────
        id_match = re.search(r"\b(?:id|numéro|numero|n°)\s*[:#]?\s*(\d+)\b", ml)
        if id_match:
            bid = int(id_match.group(1))
            b = self.controller.get_book_by_id(bid)
            if b:
                icon = "✅" if b.statut == "disponible" else ("📤" if b.statut == "emprunté" else "🔖")
                return (
                    f"📖  Livre trouvé (ID {b.id_livre}) :\n\n"
                    f"  📕  Titre    : {b.titre}\n"
                    f"  ✍️   Auteur   : {b.auteur}\n"
                    f"  🗂️   Catégorie: {b.categorie}\n"
                    f"  📅  Année    : {b.annee_publication or 'Inconnue'}\n"
                    f"  {icon}  Statut  : {b.statut.capitalize()}\n"
                    f"  📦  Quantité : {b.quantite_disponible} exemplaire(s)"
                )
            return f"❌  Aucun livre avec l'ID {bid} n'a été trouvé dans la bibliothèque."

        # ── 2. Statistics ─────────────────────────────────────────────────────
        if any(w in ml for w in ["statistique", "combien", "total", "bilan", "état", "etat", "résumé"]):
            s = self.controller.get_stats()
            cats = {}
            for b in books_all:
                cats[b.categorie] = cats.get(b.categorie, 0) + 1
            top_cats = sorted(cats.items(), key=lambda x: -x[1])[:4]
            cat_lines = "\n".join([f"    • {c} : {n} livre(s)" for c, n in top_cats])
            return (
                f"📊  Statistiques de la bibliothèque :\n\n"
                f"  📚  Total livres      : {s['total']}\n"
                f"  ✅  Disponibles       : {s['disponible']}\n"
                f"  📤  Empruntés         : {s['emprunte']}\n"
                f"  🔖  Réservés          : {s['reserve']}\n\n"
                f"  Top catégories :\n{cat_lines}"
            )

        # ── 3. List all available books ───────────────────────────────────────
        if re.search(r"\b(tous|liste|lister|affich|montre|quels?)\b.*\bdisponible", ml) or \
           (ml in ["livres disponibles", "disponibles"]):
            avail = [b for b in books_all if b.statut == "disponible"]
            if not avail:
                return "😔  Aucun livre n'est disponible pour le moment."
            lines = "\n".join([
                f"  {i+1}. «{b.titre}» — {b.auteur}  ({b.categorie})  ×{b.quantite_disponible}"
                for i, b in enumerate(avail)
            ])
            return f"✅  {len(avail)} livre(s) disponible(s) :\n\n{lines}"

        # ── 4. Author search ──────────────────────────────────────────────────
        author_match = re.search(
            r"(?:de|par|auteur|livres?\s+de|œuvres?\s+de|oeuvres?\s+de)\s+([A-ZÀ-Ö][a-zà-ö]+(?:\s+[A-ZÀ-Öa-zà-ö]+)*)",
            msg
        )
        if author_match:
            name = author_match.group(1).strip()
            found = self.controller.search_by_author(name)
            if found:
                lines = []
                for i, b in enumerate(found, 1):
                    icon = "✅" if b.statut == "disponible" else ("📤" if b.statut == "emprunté" else "🔖")
                    lines.append(f"  {i}. «{b.titre}» {icon} {b.statut.capitalize()} ({b.quantite_disponible} ex.)")
                return (
                    f"👤  {name} est dans notre catalogue.\n"
                    f"Voici ses œuvres disponibles :\n\n" + "\n".join(lines)
                )
            return f"❌  Aucun livre de «{name}» n'a été trouvé dans la bibliothèque."

        # ── 5. Category / genre search ────────────────────────────────────────
        GENRE_MAP = {
            "roman historique": "Roman historique",
            "science-fiction": "Science-Fiction",
            "science fiction": "Science-Fiction",
            "sf": "Science-Fiction",
            "informatique": "Informatique",
            "fiction": "Fiction",
            "roman": "Roman",
            "histoire": "Histoire",
            "philosophie": "Philosophie",
            "poésie": "Poésie",
            "poesie": "Poésie",
            "biographie": "Biographie",
        }
        for kw, cat in GENRE_MAP.items():
            if kw in ml:
                found = self.controller.get_by_category(cat)
                if found:
                    lines = []
                    for i, b in enumerate(found, 1):
                        icon = "✅" if b.statut == "disponible" else ("📤" if b.statut == "emprunté" else "🔖")
                        lines.append(f"  {i}. «{b.titre}» — {b.auteur}  {icon} {b.statut}  (×{b.quantite_disponible})")
                    return f"🗂️  Livres en catégorie «{cat}» :\n\n" + "\n".join(lines)
                return f"😔  Aucun livre en catégorie «{cat}» pour le moment."

        # ── 6. Availability check for a specific title ────────────────────────
        avail_kw = ["disponible", "emprunté", "emprunte", "peut-on", "puis-je", "emprunter"]
        if any(w in ml for w in avail_kw):
            # Try to find a book name in the sentence
            found = self._search_title_in_msg(msg, books_all)
            if found:
                b = found[0]
                if b.statut == "disponible":
                    return (
                        f"✅  «{b.titre}» est disponible !\n\n"
                        f"  ✍️  Auteur   : {b.auteur}\n"
                        f"  📦  Exemplaires disponibles : {b.quantite_disponible}\n"
                        f"  🗂️  Catégorie : {b.categorie}\n\n"
                        f"Vous pouvez l'emprunter dès maintenant 😊"
                    )
                elif b.statut == "emprunté":
                    return (
                        f"📤  «{b.titre}» est actuellement emprunté.\n\n"
                        f"  ✍️  Auteur : {b.auteur}\n"
                        f"  ❌  Statut : Emprunté\n\n"
                        f"Souhaitez-vous le réserver ? Je peux l'enregistrer pour vous."
                    )
                else:
                    return (
                        f"🔖  «{b.titre}» est actuellement réservé.\n\n"
                        f"  ✍️  Auteur : {b.auteur}\n"
                        f"  ⏳  Statut : Réservé\n\n"
                        f"Il sera disponible prochainement."
                    )

        # ── 7. Recommendations ────────────────────────────────────────────────
        rec_kw = ["recommand", "suggère", "suggere", "propose", "conseil", "meilleur", "facile à lire",
                  "aime lire", "je cherche", "je veux"]
        if any(w in ml for w in rec_kw):
            # Try to match a genre
            for kw, cat in GENRE_MAP.items():
                if kw in ml:
                    pool = [b for b in books_all if cat.lower() in b.categorie.lower()]
                    if pool:
                        return self._format_recommendations(pool, f"genre «{cat}»")
            # General recommendations — prefer available books
            pool = sorted(books_all, key=lambda b: (b.statut != "disponible", b.titre))
            return self._format_recommendations(pool[:6], "notre catalogue")

        # ── 8. Existence check for a title ────────────────────────────────────
        exist_kw = ["existe", "avez-vous", "avez vous", "est-ce que", "est ce que",
                    "cherche", "trouve", "trouver"]
        if any(w in ml for w in exist_kw):
            found = self._search_title_in_msg(msg, books_all)
            if found:
                b = found[0]
                icon = "✅" if b.statut == "disponible" else ("📤" if b.statut == "emprunté" else "🔖")
                return (
                    f"📖  Oui, ce livre existe dans la bibliothèque !\n\n"
                    f"  📕  Titre    : {b.titre}\n"
                    f"  ✍️  Auteur   : {b.auteur}\n"
                    f"  📅  Année    : {b.annee_publication or 'Inconnue'}\n"
                    f"  {icon}  Statut  : {b.statut.capitalize()}\n"
                    f"  📦  Quantité : {b.quantite_disponible} exemplaire(s)"
                )

        # ── 9. Generic title search (any non-stop word > 3 chars) ──────────────
        found = self._search_title_in_msg(msg, books_all)
        if found:
            b = found[0]
            icon = "✅" if b.statut == "disponible" else ("📤" if b.statut == "emprunté" else "🔖")
            others = ""
            if len(found) > 1:
                others = "\n\nAutres résultats similaires :\n" + "\n".join(
                    [f"  • «{x.titre}» — {x.auteur}" for x in found[1:4]]
                )
            return (
                f"📖  J'ai trouvé : «{b.titre}»\n\n"
                f"  ✍️  Auteur    : {b.auteur}\n"
                f"  🗂️  Catégorie : {b.categorie}\n"
                f"  📅  Année     : {b.annee_publication or 'Inconnue'}\n"
                f"  {icon}  Statut   : {b.statut.capitalize()}\n"
                f"  📦  Quantité  : {b.quantite_disponible} exemplaire(s)"
                + others
            )

        # ── 10. Greetings ─────────────────────────────────────────────────────
        if any(w in ml for w in ["bonjour", "salut", "bonsoir", "hello", "hi"]):
            return (
                "Bonjour ! 😊  Je suis votre assistant bibliothécaire.\n\n"
                "Comment puis-je vous aider aujourd'hui ?\n"
                "• Chercher un livre par titre ou ID\n"
                "• Vérifier la disponibilité\n"
                "• Recommandations par genre\n"
                "• Statistiques de la bibliothèque"
            )

        # ── 11. Help ──────────────────────────────────────────────────────────
        if any(w in ml for w in ["aide", "help", "comment", "que peux-tu", "que peut"]):
            return (
                "🆘  Voici ce que je peux faire :\n\n"
                "🔍  Chercher un livre :\n"
                "    → «Est-ce que Dune existe ?»\n"
                "    → «Livre avec l'ID 5»\n\n"
                "✅  Vérifier la disponibilité :\n"
                "    → «Les Misérables est-il disponible ?»\n\n"
                "📚  Recommandations :\n"
                "    → «Recommande-moi un roman historique»\n\n"
                "👤  Recherche par auteur :\n"
                "    → «Livres de Victor Hugo»\n\n"
                "📊  Statistiques :\n"
                "    → «Combien de livres avez-vous ?»"
            )

        # ── 12. Default ───────────────────────────────────────────────────────
        s = self.controller.get_stats()
        return (
            f"🤔  Je n'ai pas bien compris votre demande.\n\n"
            f"La bibliothèque contient actuellement {s['total']} livres "
            f"({s['disponible']} disponibles).\n\n"
            f"Essayez par exemple :\n"
            f"  • «Est-ce que 1984 est disponible ?»\n"
            f"  • «Recommande-moi un roman»\n"
            f"  • «Livres de Victor Hugo»\n"
            f"  • «Livre avec l'ID 3»\n"
            f"  • «Statistiques de la bibliothèque»"
        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _search_title_in_msg(self, msg, books_all):
        """Find books whose title words appear in the message."""
        ml = msg.lower()
        stop = {"le","la","les","un","une","des","de","du","est","ce","que","qui",
                "avec","dans","pour","sur","par","je","tu","il","elle","nous","vous",
                "ils","elles","et","ou","mais","donc","or","ni","car","si","the","a",
                "avez","vous","peut","puis","cherche","livre","livres","auteur","titre",
                "existe","trouvez","trouver","disponible","emprunté","réservé","quel"}
        scored = []
        for b in books_all:
            title_words = [w for w in re.sub(r"[^a-zà-ö\s]", "", b.titre.lower()).split() if w not in stop and len(w) > 2]
            author_words = [w for w in b.auteur.lower().split() if w not in stop and len(w) > 2]
            score = sum(1 for w in title_words if w in ml) + sum(0.5 for w in author_words if w in ml)
            if score > 0:
                scored.append((score, b))
        scored.sort(key=lambda x: -x[0])
        return [b for _, b in scored]

    def _format_recommendations(self, pool, context_label):
        lines = []
        for i, b in enumerate(pool[:6], 1):
            icon = "✅" if b.statut == "disponible" else ("📤" if b.statut == "emprunté" else "🔖")
            lines.append(f"  {i}. «{b.titre}» — {b.auteur}\n"
                         f"      {icon} {b.statut.capitalize()}  |  {b.categorie}")
        return (
            f"📚  Voici mes recommandations depuis {context_label} :\n\n"
            + "\n\n".join(lines)
        )

    def clear_conversation(self):
        for w in self.chat_scroll.winfo_children():
            w.destroy()
        self.conversation_history.clear()
        self._welcome_message()
