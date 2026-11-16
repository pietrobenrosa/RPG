import customtkinter as ctk

def mostrar_menu(container, ao_iniciar):
    for widget in container.winfo_children():
        widget.destroy()

    ctk.CTkLabel(container, text="Exile", font=("Consolas", 36, "bold"), text_color="#00FFCC").pack(pady=(80, 10))

    entry_nome = ctk.CTkEntry(container, placeholder_text="Nome do sobrevivente...", font=("Consolas", 14), width=280, height=40, justify="center")
    entry_nome.pack(pady=20)

    def clicar_jogar():
        nome = entry_nome.get().strip() or "Vance"
        ao_iniciar(nome)

    ctk.CTkButton(container, text="▶ INICIAR JOGO", font=("Consolas", 16, "bold"), fg_color="#00AA88", width=280, height=45, command=clicar_jogar).pack(pady=10)
    ctk.CTkButton(container, text="✖ SAIR", font=("Consolas", 14), fg_color="#AA3333", width=280, height=40, command=container.winfo_toplevel().quit).pack(pady=10)
