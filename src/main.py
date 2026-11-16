import customtkinter as ctk
from tela_menu import mostrar_menu

ctk.set_appearance_mode("dark")

janela = ctk.CTk()
janela.title("Exile")
janela.geometry("900x600")
janela.resizable(False, False)
janela.after(0, lambda: janela.state("zoomed")) 

container = ctk.CTkFrame(janela, fg_color="#121218")
container.pack(fill="both", expand=True)

def comecar_aventura(nome_jogador):
    print(f"O jogo começou para: {nome_jogador}")

mostrar_menu(container, comecar_aventura)
janela.mainloop()
