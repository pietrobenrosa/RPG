import logging
import tkinter as tk

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


def _reportar_erro_callback(tipo, erro, traceback_obj):
    logging.error(
        "Erro não tratado em callback da interface.",
        exc_info=(tipo, erro, traceback_obj),
    )
    try:
        messagebox.showerror(
            "Erro inesperado",
            f"Uma ação falhou:\n{erro}\n\nOs detalhes foram registrados no terminal.",
            parent=janela,
        )
    except tk.TclError:
        logging.exception("Não foi possível exibir o aviso do erro.")


janela.report_callback_exception = _reportar_erro_callback



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
    except (OSError, ValueError, tk.TclError) as erro:
        messagebox.showerror(
            "Erro ao carregar",
            f"Não foi possível restaurar o save:\n{erro}",
            parent=janela,
        )
        abrir_menu()
w

def abrir_menu():
    ao_continuar = continuar_aventura if ARQUIVO_SAVE.is_file() else None
    mostrar_menu(container, comecar_aventura, ao_continuar)


abrir_menu()
janela.mainloop()
