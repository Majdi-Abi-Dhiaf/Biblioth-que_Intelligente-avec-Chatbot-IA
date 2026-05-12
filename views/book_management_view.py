import customtkinter as ctk
from tkinter import ttk, messagebox


class BookManagementView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.pack(fill="both", expand=True, padx=20, pady=20)
        self.selected_book_id = None
        
        self.create_widgets()
        self.refresh_book_list()
    
    def create_widgets(self):
        """Create book management widgets"""
        # Title
        title = ctk.CTkLabel(
            self,
            text="Gestion des Livres",
            font=("Helvetica", 28, "bold"),
            text_color="#FFFFFF"
        )
        title.pack(pady=(0, 20))
        
        # Search frame
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill="x", pady=(0, 15))
        
        search_label = ctk.CTkLabel(
            search_frame,
            text="Rechercher:",
            font=("Helvetica", 12),
            text_color="#CCCCCC"
        )
        search_label.pack(side="left", padx=(0, 10))
        
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text="Titre, auteur, catégorie...",
            width=300,
            height=35,
            border_width=1,
            border_color="#0084FF"
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda e: self.search_books())
        
        search_btn = ctk.CTkButton(
            search_frame,
            text="Réinitialiser",
            command=self.reset_search,
            width=100,
            height=35
        )
        search_btn.pack(side="left")
        
        # Books Treeview
        tree_frame = ctk.CTkFrame(self, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Configure style for Treeview
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            'Treeview',
            background='#2a2a2a',
            foreground='#FFFFFF',
            fieldbackground='#2a2a2a',
            borderwidth=0
        )
        style.configure('Treeview.Heading', background='#1a1a1a', foreground='#FFFFFF')
        style.map('Treeview', background=[('selected', '#0084FF')])
        
        # Create Treeview
        columns = ('ID', 'Titre', 'Auteur', 'Catégorie', 'Année', 'Quantité', 'Statut')
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            height=15,
            show='headings'
        )
        
        # Define column headings and widths
        self.tree.column('ID', width=40, anchor='center')
        self.tree.column('Titre', width=150, anchor='w')
        self.tree.column('Auteur', width=120, anchor='w')
        self.tree.column('Catégorie', width=100, anchor='w')
        self.tree.column('Année', width=60, anchor='center')
        self.tree.column('Quantité', width=70, anchor='center')
        self.tree.column('Statut', width=100, anchor='center')
        
        for col in columns:
            self.tree.heading(col, text=col)
        
        self.tree.pack(fill="both", expand=True)
        self.tree.bind('<Double-1>', self.on_double_click)
        
        # Form frame
        form_frame = ctk.CTkFrame(self, fg_color="#2a2a2a", corner_radius=10)
        form_frame.pack(fill="x")
        
        form_title = ctk.CTkLabel(
            form_frame,
            text="Ajouter / Modifier un Livre",
            font=("Helvetica", 14, "bold"),
            text_color="#FFFFFF"
        )
        form_title.pack(pady=(15, 10), padx=20)
        
        # Form grid
        form_grid = ctk.CTkFrame(form_frame, fg_color="transparent")
        form_grid.pack(padx=20, pady=(10, 15), fill="x")
        
        # Input fields
        self.form_fields = {}
        fields = [
            ('Titre', 'titre'),
            ('Auteur', 'auteur'),
            ('Catégorie', 'categorie'),
            ('Année', 'annee'),
            ('Quantité', 'quantite'),
            ('Statut', 'statut')
        ]
        
        for i, (label, key) in enumerate(fields):
            row = i // 3
            col = i % 3
            
            label_widget = ctk.CTkLabel(
                form_grid,
                text=label + ":",
                font=("Helvetica", 10),
                text_color="#CCCCCC"
            )
            label_widget.grid(row=row*2, column=col, padx=10, pady=(10, 5), sticky="w")
            
            if key == 'statut':
                self.form_fields[key] = ctk.CTkComboBox(
                    form_grid,
                    values=['Disponible', 'Emprunté', 'Réparation'],
                    width=150,
                    height=35
                )
            else:
                self.form_fields[key] = ctk.CTkEntry(
                    form_grid,
                    placeholder_text=label,
                    width=150,
                    height=35,
                    border_width=1,
                    border_color="#0084FF"
                )
            
            self.form_fields[key].grid(row=row*2+1, column=col, padx=10, pady=(0, 15), sticky="ew")
        
        # Form buttons
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(padx=20, pady=(0, 15), fill="x", expand=True)
        
        add_btn = ctk.CTkButton(
            button_frame,
            text="Ajouter Livre",
            command=self.add_book,
            fg_color="#00D084",
            hover_color="#00B870"
        )
        add_btn.pack(side="left", padx=(0, 10))
        
        update_btn = ctk.CTkButton(
            button_frame,
            text="Modifier",
            command=self.update_book,
            fg_color="#0084FF",
            hover_color="#0066CC"
        )
        update_btn.pack(side="left", padx=(0, 10))
        
        delete_btn = ctk.CTkButton(
            button_frame,
            text="Supprimer",
            command=self.delete_book,
            fg_color="#FF6B6B",
            hover_color="#CC5555"
        )
        delete_btn.pack(side="left", padx=(0, 10))
        
        clear_btn = ctk.CTkButton(
            button_frame,
            text="Réinitialiser Formulaire",
            command=self.clear_form,
            fg_color="#FFB800",
            hover_color="#CC9200"
        )
        clear_btn.pack(side="left")
    
    def refresh_book_list(self):
        """Refresh the book list"""
        self.tree.delete(*self.tree.get_children())
        books = self.controller.get_all_books()
        for book in books:
            self.tree.insert('', 'end', values=(
                book[0], book[1], book[2], book[3],
                book[4], book[5], book[6]
            ))
    
    def search_books(self):
        """Search books"""
        query = self.search_var.get()
        if not query:
            self.refresh_book_list()
            return
        
        self.tree.delete(*self.tree.get_children())
        books = self.controller.search_books(query)
        for book in books:
            self.tree.insert('', 'end', values=(
                book.id, book.titre, book.auteur, book.categorie,
                book.annee_publication, book.quantite_disponible, book.statut
            ))
    
    def reset_search(self):
        """Reset search"""
        self.search_var.set('')
        self.refresh_book_list()
    
    def on_double_click(self, event):
        """Handle double click on tree item"""
        item = self.tree.selection()[0]
        values = self.tree.item(item, 'values')
        
        self.selected_book_id = values[0]
        self.form_fields['titre'].delete(0, 'end')
        self.form_fields['titre'].insert(0, values[1])
        self.form_fields['auteur'].delete(0, 'end')
        self.form_fields['auteur'].insert(0, values[2])
        self.form_fields['categorie'].delete(0, 'end')
        self.form_fields['categorie'].insert(0, values[3])
        self.form_fields['annee'].delete(0, 'end')
        self.form_fields['annee'].insert(0, values[4])
        self.form_fields['quantite'].delete(0, 'end')
        self.form_fields['quantite'].insert(0, values[5])
        self.form_fields['statut'].set(values[6])
    
    def add_book(self):
        """Add a new book"""
        try:
            titre = self.form_fields['titre'].get()
            auteur = self.form_fields['auteur'].get()
            categorie = self.form_fields['categorie'].get()
            annee = int(self.form_fields['annee'].get())
            quantite = int(self.form_fields['quantite'].get())
            statut = self.form_fields['statut'].get()
            
            if not all([titre, auteur, categorie, annee, quantite]):
                messagebox.showwarning("Validation", "Veuillez remplir tous les champs")
                return
            
            result = self.controller.create_book(titre, auteur, categorie, annee, quantite, statut)
            if result['success']:
                messagebox.showinfo("Succès", "Livre ajouté avec succès")
                self.clear_form()
                self.refresh_book_list()
            else:
                messagebox.showerror("Erreur", f"Erreur: {result.get('error', 'Inconnue')}")
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des nombres valides pour l'année et la quantité")
    
    def update_book(self):
        """Update selected book"""
        if not self.selected_book_id:
            messagebox.showwarning("Sélection", "Sélectionnez un livre à modifier")
            return
        
        try:
            titre = self.form_fields['titre'].get()
            auteur = self.form_fields['auteur'].get()
            categorie = self.form_fields['categorie'].get()
            annee = int(self.form_fields['annee'].get())
            quantite = int(self.form_fields['quantite'].get())
            statut = self.form_fields['statut'].get()
            
            if not all([titre, auteur, categorie, annee, quantite]):
                messagebox.showwarning("Validation", "Veuillez remplir tous les champs")
                return
            
            result = self.controller.update_book(
                self.selected_book_id, titre, auteur, categorie, annee, quantite, statut
            )
            if result['success']:
                messagebox.showinfo("Succès", "Livre modifié avec succès")
                self.clear_form()
                self.refresh_book_list()
            else:
                messagebox.showerror("Erreur", f"Erreur: {result.get('error', 'Inconnue')}")
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des nombres valides pour l'année et la quantité")
    
    def delete_book(self):
        """Delete selected book"""
        if not self.selected_book_id:
            messagebox.showwarning("Sélection", "Sélectionnez un livre à supprimer")
            return
        
        if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer ce livre?"):
            result = self.controller.delete_book(self.selected_book_id)
            if result['success']:
                messagebox.showinfo("Succès", "Livre supprimé avec succès")
                self.clear_form()
                self.refresh_book_list()
            else:
                messagebox.showerror("Erreur", f"Erreur: {result.get('error', 'Inconnue')}")
    
    def clear_form(self):
        """Clear the form"""
        for field in self.form_fields.values():
            if isinstance(field, ctk.CTkComboBox):
                field.set('')
            else:
                field.delete(0, 'end')
        self.selected_book_id = None
