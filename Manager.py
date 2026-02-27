import tkinter as tk
from aplicacion.constantes import style
from screens import *


'''
El manager va ser el que gestione nuestra aplicacion, aqui esta la ventana principal.
'''

class Manager(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Monitor")
        container= tk.Frame(self)
        container.pack(
            side= tk.TOP,
            fill= tk.BOTH,
            expand= True
        )
        container.configure(background= style.BACKGROUND)
        container.grid_columnconfigure(0,weight= 1)
        container.grid_rowconfigure(0, weight=1)

        self.frames= {}
        for F in (Home, Monitor):
            frame= F(container, self)#Dotamos a las pantallas de su parent y su controller
            self.frames[F]= frame
            frame.grid(row= 0, column= 0, sticky= tk.NSEW)
        self.show_frame(Home)

    def show_frame(self, container):#Nos va a permitir cambiar de pantalla
        frame= self.frames[container]
        frame.tkraise()