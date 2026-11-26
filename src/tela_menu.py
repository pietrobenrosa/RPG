from pathlib import Path
import warnings

import customtkinter as ctk
from PIL import Image, ImageSequence


COR_FUNDO = "#090D16"
COR_PAINEL = "#111A27"
COR_DESTAQUE = "#42E8C4"
COR_TEXTO = "#E8F0F5"
COR_SECUNDARIA = "#91A4B5"
NOME_GIF = "portal-shard-game-asset.gif"


def _localizar_gif():
    """Procura a arte nas pastas comuns de assets do projeto."""
    pasta_src = Path(__file__).resolve().parent
    raiz = pasta_src.parent
    for caminho in (
        raiz / NOME_GIF,
        pasta_src / NOME_GIF,
        raiz / "assets" / NOME_GIF,
        raiz / "assets" / "cenarios" / NOME_GIF,
        raiz / "dados" / NOME_GIF,
    ):
        if caminho.is_file():
            return caminho
    return None


def _mostrar_como_jogar(container):
    janela = ctk.CTkToplevel(container.winfo_toplevel())
    janela.title("Como jogar — Exile")
    janela.geometry("520x390")
    janela.resizable(False, False)
    janela.configure(fg_color=COR_FUNDO)
    janela.transient(container.winfo_toplevel())
    janela.grab_set()

    ctk.CTkLabel(
        janela,
        text="COMO JOGAR",
        font=("Consolas", 24, "bold"),
        text_color=COR_DESTAQUE,
    ).pack(anchor="w", padx=32, pady=(30, 18))

    instrucoes = (
        "Acorde no bunker e descubra o que aconteceu com a Terra.\n\n"
        "• Explore os ambientes e reúna peças para consertar o mini-foguete.\n"
        "• Nos combates, escolha entre atacar, usar um item ou fugir.\n"
        "• Os testes e ataques usam um dado D20 — boa sorte nas rolagens!\n"
        "• Chegue à estação orbital e encontre uma forma de escapar.\n\n"
        "Sua jornada começa sozinha. Suas escolhas decidem como ela termina."
    )
    ctk.CTkLabel(
        janela,
        text=instrucoes,
        font=("Consolas", 14),
        text_color=COR_TEXTO,
        justify="left",
        wraplength=450,
    ).pack(anchor="w", padx=32, pady=4)

    ctk.CTkButton(
        janela,
        text="ENTENDI",
        font=("Consolas", 14, "bold"),
        fg_color=COR_DESTAQUE,
        hover_color="#2BC5A5",
        text_color=COR_FUNDO,
        height=42,
        command=janela.destroy,
    ).pack(fill="x", padx=32, pady=(22, 28))


def mostrar_menu(container, ao_iniciar, ao_continuar=None):
    for widget in container.winfo_children():
        widget.destroy()

    container.configure(fg_color=COR_FUNDO)

    cartao = ctk.CTkFrame(container, fg_color=COR_PAINEL, corner_radius=22)
    cartao.pack(fill="both", expand=True, padx=44, pady=36)
    cartao.grid_columnconfigure(0, weight=6, uniform="menu")
    cartao.grid_columnconfigure(1, weight=5, uniform="menu")
    cartao.grid_rowconfigure(0, weight=1)

    # O GIF é opcional para que o menu continue abrindo sem o arquivo.
    area_arte = ctk.CTkFrame(cartao, fg_color="#0C121D", corner_radius=18)
    area_arte.grid(row=0, column=0, sticky="nsew", padx=(14, 8), pady=14)

    caminho_gif = _localizar_gif()
    if caminho_gif:
        try:
            with Image.open(caminho_gif) as gif:
                quadros = [
                    quadro.convert("RGBA").copy()
                    for quadro in ImageSequence.Iterator(gif)
                ]
                duracao = max(40, gif.info.get("duration", 100))
            if not quadros:
                raise ValueError("O GIF não contém quadros.")

            # O GIF original tem 48x48: amplie mantendo a proporção quadrada.
            tamanho_maximo = max(
                48,
                min(
                    480,
                    area_arte.winfo_screenwidth() // 2,
                    area_arte.winfo_screenheight() - 180,
                ),
            )
            tamanho_original = quadros[0].size
            escala = min(
                tamanho_maximo / tamanho_original[0],
                tamanho_maximo / tamanho_original[1],
            )
            tamanho = (
                max(1, round(tamanho_original[0] * escala)),
                max(1, round(tamanho_original[1] * escala)),
            )
            quadros = [
                quadro.resize(tamanho, Image.Resampling.NEAREST)
                for quadro in quadros
            ]

            imagem_gif = ctk.CTkLabel(area_arte, text="")
            imagem_gif.pack(fill="both", expand=True, padx=10, pady=10)
            imagens_ctk = [
                ctk.CTkImage(light_image=quadro, dark_image=quadro, size=tamanho)
                for quadro in quadros
            ]
            imagem_gif.configure(image=imagens_ctk[0])
            imagem_gif._imagens_gif = imagens_ctk

            def animar(indice=0):
                if not imagem_gif.winfo_exists():
                    return
                imagem_gif.configure(image=imagens_ctk[indice])
                imagem_gif.after(duracao, animar, (indice + 1) % len(imagens_ctk))

            if len(imagens_ctk) > 1:
                imagem_gif.after(duracao, animar, 1 % len(imagens_ctk))
        except (EOFError, OSError, ValueError) as erro:
            warnings.warn(
                f"Não foi possível exibir a animação do menu "
                f"'{caminho_gif}': {erro}",
                RuntimeWarning,
                stacklevel=2,
            )
            _mostrar_fallback_arte(area_arte)
    else:
        _mostrar_fallback_arte(area_arte)

    painel_menu = ctk.CTkFrame(cartao, fg_color="transparent")
    painel_menu.grid(row=0, column=1, sticky="nsew", padx=(24, 42), pady=36)
    painel_menu.grid_columnconfigure(0, weight=1)
    painel_menu.grid_rowconfigure(0, weight=1)
    conteudo = ctk.CTkFrame(painel_menu, fg_color="transparent")
    conteudo.grid(row=1, column=0, sticky="ew")
    conteudo.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(
        conteudo,
        text="EXILE",
        font=("Consolas", 54, "bold"),
        text_color=COR_DESTAQUE,
    ).grid(row=0, column=0, sticky="w")
    ctk.CTkLabel(
        conteudo,
        text="A ÚLTIMA CHANCE DA HUMANIDADE",
        font=("Consolas", 12, "bold"),
        text_color=COR_SECUNDARIA,
    ).grid(row=1, column=0, sticky="w", pady=(2, 20))
    ctk.CTkLabel(
        conteudo,
        text="O bunker está em ruínas.\nA contagem regressiva já começou.",
        font=("Consolas", 16),
        text_color=COR_TEXTO,
        justify="left",
    ).grid(row=2, column=0, sticky="w", pady=(0, 30))

    linha_botao = 3
    if ao_continuar is not None:
        ctk.CTkButton(
            conteudo,
            text="↻   CONTINUAR JOGO",
            font=("Consolas", 15, "bold"),
            fg_color="#202D3B",
            hover_color="#2A3B4D",
            text_color=COR_TEXTO,
            height=48,
            corner_radius=10,
            command=ao_continuar,
        ).grid(row=linha_botao, column=0, sticky="ew", pady=(0, 10))
        linha_botao += 1

    ctk.CTkButton(
        conteudo,
        text="▶   COMEÇAR JOGO",
        font=("Consolas", 16, "bold"),
        fg_color=COR_DESTAQUE,
        hover_color="#2BC5A5",
        text_color=COR_FUNDO,
        height=54,
        corner_radius=10,
        command=lambda: ao_iniciar("Vance"),
    ).grid(row=linha_botao, column=0, sticky="ew", pady=(0, 12))
    linha_botao += 1
    ctk.CTkButton(
        conteudo,
        text="?   COMO JOGAR",
        font=("Consolas", 15, "bold"),
        fg_color="#202D3B",
        hover_color="#2A3B4D",
        text_color=COR_TEXTO,
        height=48,
        corner_radius=10,
        command=lambda: _mostrar_como_jogar(container),
    ).grid(row=linha_botao, column=0, sticky="ew", pady=(0, 12))
    linha_botao += 1
    ctk.CTkButton(
        conteudo,
        text="SAIR",
        font=("Consolas", 14),
        fg_color="transparent",
        hover_color="#26313C",
        text_color=COR_SECUNDARIA,
        height=42,
        corner_radius=10,
        command=container.winfo_toplevel().quit,
    ).grid(row=linha_botao, column=0, sticky="ew")

    ctk.CTkLabel(
        painel_menu,
        text="SOBREVIVA. ESCAPE. RECOMECE.",
        font=("Consolas", 10, "bold"),
        text_color="#526577",
    ).grid(row=2, column=0, sticky="sw", pady=(24, 0))


def _mostrar_fallback_arte(area_arte):
    ctk.CTkLabel(
        area_arte,
        text="✦\n\nPORTAL DE EVACUAÇÃO\n\nColoque o arquivo\n"
        f"{NOME_GIF}\nna pasta do projeto para exibir a animação.",
        font=("Consolas", 16, "bold"),
        text_color=COR_DESTAQUE,
        justify="center",
    ).pack(fill="both", expand=True, padx=24, pady=24)
