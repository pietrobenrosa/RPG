import customtkinter as ctk

from tela_menu import mostrar_menu
from jogo import Jogo


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

janela = ctk.CTk()
janela.title("Exile — A Última Chance da Humanidade")
janela.geometry("1100x720")
janela.minsize(900, 600)
container = ctk.CTkFrame(janela, fg_color="#090D16")
container.pack(fill="both", expand=True)


def comecar_aventura(_nome_jogador="Vance"):
    Jogo(container, ao_menu=lambda: mostrar_menu(container, comecar_aventura))


mostrar_menu(container, comecar_aventura)
janela.mainloop()
