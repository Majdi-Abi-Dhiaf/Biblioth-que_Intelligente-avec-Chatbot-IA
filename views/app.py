import customtkinter as ctk
from config import APP_TITLE, APP_SIZE

class LibraryApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(APP_SIZE)
        self.grid_columnconfigure((0,1),weight=1)
        self.create_button()
    def create_button(self):
        button =ctk.CTkButton(self,text="chayma ya 7alofa")
        button.grid(row=0,column=0,padx=20,pady=20, sticky="ew", columnspan=2)

        checkbox_1 =ctk.CTkCheckBox(self,text="1")
        checkbox_1.grid(row=1,column=0,padx=20,pady=(0,20),sticky="w")
        checkbox_2 =ctk.CTkCheckBox(self,text="2")
        checkbox_2.grid(row=1,column=1,padx=10,pady=(0,20),sticky="w")
        checkbox_3 =ctk.CTkCheckBox(self,text="3")
        checkbox_3.grid(row=1,column=3,padx=20,pady=(0,20),sticky="w")
        

