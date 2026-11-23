import math
from pathlib import Path
import tkinter as tk

import customtkinter as ctk
from PIL import Image, ImageTk

from audio import AudioPassos
from dice_anim import AnimadorD20
from models import Entidade


FUNDO = "#090D16"
PAINEL = "#111A27"
DESTAQUE = "#42E8C4"
TEXTO = "#E8F0F5"
SUAVE = "#91A4B5"

CLASSES = {
    "Engenheiro": {
        "hp": 34,
        "ataque": 6,
        "defesa": 8,
        "nivel": 1,
        "descricao": "Resistente; vive no improviso e domina o bunker.",
        "pele": "#E7C39B",
        "roupa": "#5C7D7A",
        "acessorio": "#42E8C4",
    },
    "Segurança": {
        "hp": 42,
        "ataque": 9,
        "defesa": 5,
        "nivel": 1,
        "descricao": "Mau em negociação, ótimo em sobreviver ao caos.",
        "pele": "#D4A07B",
        "roupa": "#7B2E2E",
        "acessorio": "#D9B36B",
    },
    "Cientista": {
        "hp": 27,
        "ataque": 7,
        "defesa": 4,
        "nivel": 2,
        "descricao": "Resolve problemas com lógica, não com força bruta.",
        "pele": "#EAC7A6",
        "roupa": "#47649B",
        "acessorio": "#B9D7FF",
    },
}

LARGURA_MUNDO = 960
ALTURA_MUNDO = 540
VELOCIDADE_JOGADOR = 3.9
SPAWN_INICIAL = (235, 410)
TAMANHO_PERSONAGEM = {
    "sala_hibernacao": 128,
    "corredor": 256,
}
RAIO_JOGADOR = {
    "sala_hibernacao": 18,
    "corredor": 36,
}

IMAGENS_SALAS = {
    "sala_hibernacao": Path(__file__).resolve().parents[1] / "assets" / "cenarios" / "Sala_Hibernação.png",
    "corredor": Path(__file__).resolve().parents[1] / "assets" / "cenarios" / "Corredor.png",
}
AUDIO_PASSOS = Path(__file__).resolve().parents[1] / "assets" / "audios" / "passos.mp3"

# Coordenadas (x, y, largura, altura) no mundo virtual de 960x540.
# Para bloquear uma área, ajuste ou acrescente retângulos nestas listas.
COLISOES = {
    "sala_hibernacao": [
        (0, 210, 625, 22),
        (770, 210, 190, 22),
        (38, 215, 100, 165),
        (185, 215, 105, 165),
        (350, 215, 105, 165),
        (510, 215, 100, 165),
    ],
    "corredor": [
        (385, 0, 190, 210),
        (0, 210, 334, 85),
        (626, 210, 334, 85),
        (0, 295, 284, 85),
        (676, 295, 284, 85),
        (0, 380, 234, 160),
        (726, 380, 234, 160),
    ],
}

# Cada retângulo de passagem leva o jogador para uma sala e posição de entrada.
# Para criar outra saída, copie um item e ajuste a área, o destino e o spawn.
ZONAS_TELEPORTE = {
    "sala_hibernacao": [
        {
            "retangulo": (620, 185, 155, 60),
            "destino": "corredor",
            "spawn": (480, 430),
        },
    ],
    "corredor": [
        {
            "retangulo": (380, 470, 200, 70),
            "destino": "sala_hibernacao",
            "spawn": (700, 260),
        },
    ],
}

PORTAS_CORREDOR = [
    {"numero": 1, "retangulo": (265, 400, 80, 100)},
    {"numero": 2, "retangulo": (350, 285, 70, 95)},
    {"numero": 3, "retangulo": (550, 210, 80, 70)},
    {"numero": 4, "retangulo": (650, 400, 80, 100)},
]

LIMITES_SALAS = {
    "sala_hibernacao": (20, 25, 940, 520),
    "corredor": (20, 25, 940, 520),
}

SPRITES_JOGADOR = {
    "baixo": (
        "Personagem_frente_parado.png",
        "Personagem_frente_perna_levantada_1.png",
        "Personagem_frente_perna_levantada_2.png",
    ),
    "cima": (
        "Personagem_costas_parado.png",
        "Personagem_costas_perna_direita_levantada.png",
        "Personagem_costas_perna_esquerda_levantada.png",
    ),
    "direita": (
        "personagem_olhando_direita_parado.png",
        "Personagem_olhando_direita_perna_levantada_1.png",
        "Personagem_olhando_direita_perna_levantada_2.png",
    ),
    "esquerda": (
        "Personagem_olhando_esquerda.png",
        "Personagem_olhando_esquerda_perna_levantada_1.png",
        "Personagem_olhando_esquerda_pernas_no_chao.png",
    ),
}

TECLAS_MOVIMENTO = {
    "w": ("cima", 0, -1),
    "up": ("cima", 0, -1),
    "s": ("baixo", 0, 1),
    "down": ("baixo", 0, 1),
    "a": ("esquerda", -1, 0),
    "left": ("esquerda", -1, 0),
    "d": ("direita", 1, 0),
    "right": ("direita", 1, 0),
}


class Jogo:
    def __init__(self, container, ao_menu):
        self.container = container
        self.ao_menu = ao_menu
        self.container.configure(fg_color=FUNDO)
        self.jogador = None
        self.inventario = {"Kit Médico": 1, "Adrenalina": 1, "EMP": 1}
        self.pecas = set()
        self.ataque_extra = 0
        self.log = "Você entrou no bunker. A missão começa agora."
        self._estado = "selecao"

        self._setup_tela_selecao()

    def _limpar(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        self.container.configure(fg_color=FUNDO)

    def _desenhar_pessoa(self, canvas, x, y, nome, cor_pele, cor_roupa, cor_acessorio, sexo="m"):
        px = x
        py = y
        # corpo e proporções mais realistas
        torso_h = 18
        head_r = 10
        canvas.create_oval(px - head_r, py - 30, px + head_r, py - 10, fill=cor_pele, outline="#1B1F2A")
        canvas.create_rectangle(px - 10, py - 10, px + 10, py + torso_h, fill=cor_roupa, outline="#1B1F2A")
        canvas.create_line(px, py + torso_h, px - 9, py + 35, fill="#1B1F2A", width=3)
        canvas.create_line(px, py + torso_h, px + 9, py + 35, fill="#1B1F2A", width=3)
        canvas.create_line(px - 8, py + 7, px - 16, py + 18, fill="#1B1F2A", width=3)
        canvas.create_line(px + 8, py + 7, px + 16, py + 18, fill="#1B1F2A", width=3)
        canvas.create_oval(px - 3, py - 25, px - 1, py - 23, fill="#0B0D12")
        canvas.create_oval(px + 1, py - 25, px + 3, py - 23, fill="#0B0D12")
        if sexo == "m":
            canvas.create_line(px - 2, py - 20, px + 2, py - 20, fill="#1D1D1D", width=2)
        canvas.create_rectangle(px - 5, py - 12, px + 5, py - 4, fill=cor_acessorio, outline="")
        if nome:
            canvas.create_text(px, py + 42, text=nome, fill=TEXTO, font=("Consolas", 8, "bold"))

    def _setup_tela_selecao(self):
        self._limpar()
        painel = ctk.CTkFrame(self.container, fg_color=PAINEL, corner_radius=24)
        painel.pack(fill="both", expand=True, padx=40, pady=26)

        titulo = ctk.CTkLabel(
            painel,
            text="EXILE — ESCOLHA A CLASSE",
            font=("Consolas", 28, "bold"),
            text_color=DESTAQUE,
        )
        titulo.pack(pady=(20, 10))

        nome_frame = ctk.CTkFrame(painel, fg_color="#0A1220", corner_radius=16)
        nome_frame.pack(fill="x", padx=24, pady=(10, 16))
        ctk.CTkLabel(nome_frame, text="Nome do sobrevivente", text_color=SUAVE, font=("Consolas", 12, "bold")).pack(anchor="w", padx=18, pady=(14, 6))
        self.entry_nome = ctk.CTkEntry(nome_frame, placeholder_text="Digite seu nome", width=300, height=38, border_color=DESTAQUE)
        self.entry_nome.pack(padx=18, pady=(0, 14), fill="x")

        for nome, dados in CLASSES.items():
            card = ctk.CTkFrame(painel, fg_color="#0E1622", corner_radius=18)
            card.pack(fill="x", padx=20, pady=8)
            linha = ctk.CTkFrame(card, fg_color="transparent")
            linha.pack(fill="x", padx=10, pady=10)

            # miniatura do personagem
            mini = tk.Canvas(linha, width=72, height=72, bg="#0E1622", highlightthickness=0)
            mini.pack(side="left", padx=(6, 14))
            self._desenhar_pessoa(mini, 36, 36, "", dados["pele"], dados["roupa"], dados["acessorio"], sexo="m")

            texto = (
                f"{nome}\n"
                f"HP {dados['hp']} | ATQ {dados['ataque']} | DEF {dados['defesa']} | NÍVEL {dados['nivel']}\n"
                f"{dados['descricao']}"
            )
            label = ctk.CTkLabel(linha, text=texto, justify="left", text_color=TEXTO, font=("Consolas", 13), anchor="w")
            label.pack(side="left", fill="x", expand=True)

            btn = ctk.CTkButton(
                card,
                text="SELECIONAR",
                command=lambda n=nome: self._iniciar_jogo(n),
                fg_color=DESTAQUE,
                hover_color="#2BC5A5",
                text_color="#050C14",
                font=("Consolas", 13, "bold"),
                height=36,
            )
            btn.pack(fill="x", padx=12, pady=(0, 12))

    def _iniciar_jogo(self, nome_classe):
        nome = self.entry_nome.get().strip() or "Vance"
        dados = CLASSES[nome_classe]
        self.jogador = Entidade(nome, dados["hp"], dados["ataque"], dados["defesa"], dados["nivel"])
        self.classe_atual = nome_classe
        self.jogador_nome = nome
        self._estado = "mundo"
        self._iniciar_mapa()

    def _iniciar_mapa(self):
        self._limpar()

        self.topo = ctk.CTkFrame(self.container, fg_color="#101B2C")
        self.topo.pack(fill="x", pady=(12, 0), padx=12)

        self.nome_sala_label = ctk.CTkLabel(
            self.topo,
            text=f"{self.jogador.nome} — {self.classe_atual}",
            font=("Consolas", 19, "bold"),
            text_color=DESTAQUE,
        )
        self.nome_sala_label.pack(side="left", padx=16, pady=10)
        self.hp_label = ctk.CTkLabel(self.topo, text="HP: 0/0", font=("Consolas", 12, "bold"), text_color="#FDE2D2")
        self.hp_label.pack(side="left", padx=20)

        self.sala_atual = "sala_hibernacao"
        self.player_x, self.player_y = SPAWN_INICIAL
        self.direcao = "cima"
        self.teclas_pressionadas = set()
        self._quadro_animacao = 0
        self._tempo_animacao = 0
        self._ultimo_tamanho = None
        self._fundo_canvas = None
        self._imagem_fundo = None
        self._porta_ocupada = None
        self.tela_porta = None
        self.audio_passos = AudioPassos(AUDIO_PASSOS)
        self._imagens_fundo = {
            sala: Image.open(caminho).convert("RGBA")
            for sala, caminho in IMAGENS_SALAS.items()
        }
        pasta_sprites = Path(__file__).resolve().parents[1] / "assets" / "personagem"
        self._sprites_originais = {
            direcao: tuple(
                Image.open(pasta_sprites / arquivo).convert("RGBA")
                for arquivo in arquivos
            )
            for direcao, arquivos in SPRITES_JOGADOR.items()
        }
        self._sprites_redimensionados = {}

        self.canvas = tk.Canvas(self.container, width=1040, height=585, bg="#11171D", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=14, pady=12)
        self.canvas.bind("<Configure>", self._redimensionar_cena)
        self.canvas.bind("<KeyPress>", self._on_key)
        self.canvas.bind("<KeyRelease>", self._on_key_release)
        self.canvas.focus_set()

        self._desenhar_hud()
        self._atualizar_hud()

    def _desenhar_hud(self):
        self.d20_label = tk.Label(
            self.container,
            text="D20: —",
            fg=DESTAQUE,
            bg=FUNDO,
            font=("Consolas", 12, "bold"),
            compound="top",
        )
        self.d20_label.place(relx=0.98, rely=0.97, anchor="se")
        self.animador_d20 = AnimadorD20(self.d20_label)

        self.dialogo_var = tk.StringVar(value="")
        self.dialogo = tk.Label(
            self.container,
            textvariable=self.dialogo_var,
            fg=TEXTO,
            bg=FUNDO,
            justify="left",
            wraplength=480,
            font=("Consolas", 11),
        )
        self.dialogo.place(relx=0.02, rely=0.97, anchor="sw")
        self._atualizar_nome_sala()
        self.container.after(20, self._atualizar_movimento)

    def _atualizar_hud(self):
        self.hp_label.configure(text=f"HP: {self.jogador.hp}/{CLASSES[self.classe_atual]['hp']}")

    def _atualizar_nome_sala(self):
        nome = "SALA DE HIBERNAÇÃO" if self.sala_atual == "sala_hibernacao" else "CORREDOR"
        self.nome_sala_label.configure(text=f"{self.jogador.nome} — {self.classe_atual}  |  {nome}")

    def _redimensionar_cena(self, event=None):
        largura = event.width if event is not None else self.canvas.winfo_width()
        altura = event.height if event is not None else self.canvas.winfo_height()
        if largura <= 1 or altura <= 1:
            return
        tamanho = (largura, altura)
        if tamanho == self._ultimo_tamanho:
            return
        self._ultimo_tamanho = tamanho
        escala_x = largura / LARGURA_MUNDO
        escala_y = altura / ALTURA_MUNDO

        fundo = self._imagens_fundo[self.sala_atual].resize(
            tamanho,
            Image.Resampling.LANCZOS,
        )
        self._imagem_fundo = ImageTk.PhotoImage(fundo)
        if self._fundo_canvas is None:
            self._fundo_canvas = self.canvas.create_image(0, 0, anchor="nw", image=self._imagem_fundo)
            self.player = self.canvas.create_image(0, 0, anchor="s")
        else:
            self.canvas.itemconfigure(self._fundo_canvas, image=self._imagem_fundo)
        self.canvas.tag_lower(self._fundo_canvas)

        tamanho_sprite = (
            max(1, round(TAMANHO_PERSONAGEM[self.sala_atual] * escala_x)),
            max(1, round(TAMANHO_PERSONAGEM[self.sala_atual] * escala_y)),
        )
        self._sprites_redimensionados = {
            direcao: tuple(
                ImageTk.PhotoImage(sprite.resize(tamanho_sprite, Image.Resampling.NEAREST))
                for sprite in quadros
            )
            for direcao, quadros in self._sprites_originais.items()
        }
        self._desenhar_jogador()

    def _desenhar_jogador(self):
        if not self._sprites_redimensionados:
            return
        escala_x = self.canvas.winfo_width() / LARGURA_MUNDO
        escala_y = self.canvas.winfo_height() / ALTURA_MUNDO
        indice = self._quadro_animacao + 1 if self.teclas_pressionadas else 0
        imagem = self._sprites_redimensionados[self.direcao][indice]
        self.canvas.coords(self.player, self.player_x * escala_x, self.player_y * escala_y)
        self.canvas.itemconfigure(self.player, image=imagem)
        self._imagem_jogador = imagem

    def _posicao_valida(self, x, y):
        raio = RAIO_JOGADOR[self.sala_atual]
        esquerda, topo, direita, base = LIMITES_SALAS[self.sala_atual]
        if (
            x - raio < esquerda
            or y - raio < topo
            or x + raio > direita
            or y + raio > base
        ):
            return False
        for rx, ry, largura, altura in COLISOES[self.sala_atual]:
            if (
                x + raio > rx
                and x - raio < rx + largura
                and y + raio > ry
                and y - raio < ry + altura
            ):
                return False
        return True

    def _on_key(self, event):
        if self._estado != "mundo":
            return
        tecla = event.keysym.lower()
        if tecla in TECLAS_MOVIMENTO:
            self.teclas_pressionadas.add(tecla)
        elif tecla == "r":
            self._rolar_teste()

    def _on_key_release(self, event):
        self.teclas_pressionadas.discard(event.keysym.lower())

    def _atualizar_movimento(self):
        if self._estado == "porta":
            self.container.after(20, self._atualizar_movimento)
            return
        if self._estado != "mundo":
            return
        dx = 0
        dy = 0
        for tecla in self.teclas_pressionadas:
            if tecla in TECLAS_MOVIMENTO:
                _, movimento_x, movimento_y = TECLAS_MOVIMENTO[tecla]
                dx += movimento_x
                dy += movimento_y

        moveu = False
        if dx or dy:
            direcao = "cima" if dy < 0 else "baixo" if dy > 0 else "esquerda" if dx < 0 else "direita"
            if direcao != self.direcao:
                self.direcao = direcao
                self._quadro_animacao = 0
                self._tempo_animacao = 0
            comprimento = math.hypot(dx, dy)
            dx = VELOCIDADE_JOGADOR * dx / comprimento
            dy = VELOCIDADE_JOGADOR * dy / comprimento

            novo_x = self.player_x + dx
            if self._posicao_valida(novo_x, self.player_y):
                self.player_x = novo_x
                moveu = True
            novo_y = self.player_y + dy
            if self._posicao_valida(self.player_x, novo_y):
                self.player_y = novo_y
                moveu = True

            self._tempo_animacao += 1
            if moveu and self._tempo_animacao >= 6:
                self._quadro_animacao = (self._quadro_animacao + 1) % 2
                self._tempo_animacao = 0
            elif not moveu:
                self._quadro_animacao = 0
                self._tempo_animacao = 0
        else:
            self._quadro_animacao = 0
            self._tempo_animacao = 0

        self.audio_passos.atualizar(moveu)
        self._desenhar_jogador()
        self._verificar_teleporte()
        self.container.after(20, self._atualizar_movimento)

    def _verificar_teleporte(self):
        for zona in ZONAS_TELEPORTE[self.sala_atual]:
            x, y, largura, altura = zona["retangulo"]
            if x <= self.player_x <= x + largura and y <= self.player_y <= y + altura:
                self._carregar_sala(zona["destino"], zona["spawn"])
                return
        self._verificar_porta_corredor()

    def _verificar_porta_corredor(self):
        if self.sala_atual != "corredor":
            return
        if self._porta_ocupada is not None:
            x, y, largura, altura = self._porta_ocupada["retangulo"]
            if x <= self.player_x <= x + largura and y <= self.player_y <= y + altura:
                return
            self._porta_ocupada = None

        for porta in PORTAS_CORREDOR:
            x, y, largura, altura = porta["retangulo"]
            if x <= self.player_x <= x + largura and y <= self.player_y <= y + altura:
                self._porta_ocupada = porta
                self._abrir_porta(porta["numero"])
                return

    def _abrir_porta(self, numero):
        self._estado = "porta"
        self.teclas_pressionadas.clear()
        self.audio_passos.parar()

        self.tela_porta = tk.Frame(self.container, bg="black", takefocus=True)
        self.tela_porta.place(relx=0, rely=0, relwidth=1, relheight=1)
        tk.Label(
            self.tela_porta,
            text=f"Você entrou na porta {numero}\n\nPressione ESC para voltar ao corredor",
            fg="white",
            bg="black",
            font=("Consolas", 24, "bold"),
            justify="center",
        ).pack(expand=True)
        self.tela_porta.bind("<KeyPress-Escape>", self._fechar_porta)
        self.tela_porta.lift()
        self.tela_porta.focus_set()

    def _fechar_porta(self, event=None):
        self.tela_porta.destroy()
        self.tela_porta = None
        self._estado = "mundo"
        self.teclas_pressionadas.clear()
        self.canvas.focus_set()
        return "break"

    def _carregar_sala(self, sala, spawn):
        self.sala_atual = sala
        self.player_x, self.player_y = spawn
        self.audio_passos.parar()
        self.direcao = "baixo"
        self._quadro_animacao = 0
        self._tempo_animacao = 0
        self.teclas_pressionadas.clear()
        self.dialogo_var.set("")
        self._atualizar_nome_sala()
        self._ultimo_tamanho = None
        self._redimensionar_cena()
        self.canvas.focus_set()

    def _rolar_teste(self, event=None):
        if self.animador_d20.rolando:
            return
        self.dialogo_var.set("Teste D20 em andamento...")
        self.animador_d20.rolar_teste(
            lambda valor: self.dialogo_var.set(f"Resultado do teste: {valor}.")
        )


if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("1100x720")
    container = ctk.CTkFrame(root, fg_color=FUNDO)
    container.pack(fill="both", expand=True)
    Jogo(container, ao_menu=lambda: None)
    root.mainloop()
