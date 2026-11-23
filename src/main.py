import customtkinter as ctk
from tkinter import messagebox

from tela_menu import mostrar_menu
from jogo import Jogo
from savegame import ARQUIVO_SAVE, carregar_jogo


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

janela = ctk.CTk()
janela.title("Exile — A Última Chance da Humanidade")
janela.geometry("1100x720")
janela.minsize(900, 600)
janela.after(0, lambda: janela.state("zoomed"))
container = ctk.CTkFrame(janela, fg_color="#090D16")
container.pack(fill="both", expand=True)



def comecar_aventura(_nome_jogador="Vance"):
    Jogo(container, ao_menu=abrir_menu)


def continuar_aventura():
    try:
        dados = carregar_jogo()
    except (OSError, ValueError) as erro:
        messagebox.showerror(
            "Erro ao carregar",
            f"Não foi possível carregar o save:\n{erro}",
            parent=janela,
        )
        return
    try:
        Jogo(container, ao_menu=abrir_menu, save_data=dados)
    except ValueError as erro:
        messagebox.showerror(
            "Erro ao carregar",
            f"Não foi possível restaurar o save:\n{erro}",
            parent=janela,
        )


def abrir_menu():
    ao_continuar = continuar_aventura if ARQUIVO_SAVE.is_file() else None
    mostrar_menu(container, comecar_aventura, ao_continuar)


abrir_menu()
janela.mainloop()
