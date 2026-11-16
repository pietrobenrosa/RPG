import random
import tkinter as tk

import customtkinter as ctk

from combate import atacar, rolar_d20, testar_fuga
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
        self.mapa = None
        self.paredes = []
        self.interagiveis = []
        self.interacao_atual = None
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

        ctk.CTkLabel(self.topo, text=f"{self.jogador.nome} — {self.classe_atual}", font=("Consolas", 19, "bold"), text_color=DESTAQUE).pack(side="left", padx=16, pady=10)
        self.hp_label = ctk.CTkLabel(self.topo, text="HP: 0/0", font=("Consolas", 12, "bold"), text_color="#FDE2D2")
        self.hp_label.pack(side="left", padx=20)

        self.canvas = tk.Canvas(self.container, width=1040, height=650, bg="#11171D", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=14, pady=12)

        self.canvas.bind("<KeyPress>", self._on_key)
        self.canvas.focus_set()

        self.player_x = 200
        self.player_y = 260
        self.movimento = 24
        self.parede = []
        self._montar_mapa()
        self._desenhar_jogador()
        self._desenhar_npcs()
        self._desenhar_hud()
        self._atualizar_hud()

        self.canvas.bind("<space>", self._interagir)
        self.container.bind("<KeyPress>", self._on_key)

    def _montar_mapa(self):
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, 1040, 650, fill="#1B232E", outline="")

        # piso e paredes do bunker
        self.canvas.create_rectangle(40, 40, 1000, 610, fill="#202A38", outline="#2F3F51", width=2)
        self.canvas.create_rectangle(80, 80, 960, 570, fill="#0E1822", outline="#2A3D4B", width=2)

        # corredores e divisórias
        for rect in [
            (180, 70, 210, 520),
            (430, 110, 470, 560),
            (700, 80, 740, 530),
            (820, 180, 920, 220),
        ]:
            self.canvas.create_rectangle(*rect, fill="#28384A", outline="#344D67", width=2)
            self.parede.append(rect)

        # elementos de cenário
        self.canvas.create_rectangle(100, 120, 160, 180, fill="#7A9AA9", outline="#B8D1E0")
        self.canvas.create_rectangle(500, 300, 620, 420, fill="#8C6A4E", outline="#DAB286")
        self.canvas.create_rectangle(840, 400, 930, 510, fill="#3A586F", outline="#8FBCD6")

        # pontos de interação
        self.interagiveis = [
            {"id": "terminal", "nome": "Terminal", "x": 118, "y": 150, "tipo": "dialogo", "texto": "A gravação final da equipe está no terminal. Eles avisavam que a estação orbital estava infectada."},
            {"id": "escada", "nome": "Escada", "x": 845, "y": 190, "tipo": "teste", "texto": "A escada leva ao patamar superior. Se conseguir escalar, pode seguir para a superfície."},
            {"id": "gerador", "nome": "Gerador", "x": 560, "y": 365, "tipo": "item", "texto": "Você encontra um módulo de energia improvisado."},
            {"id": "npc1", "nome": "Técnica Nara", "x": 245, "y": 250, "tipo": "npc", "texto": "Nara: 'A ponte de evacuação foi destruída. O resto do bunker já foi abandonado.'"},
            {"id": "npc2", "nome": "Soldado Rog", "x": 780, "y": 460, "tipo": "npc", "texto": "Rog: 'Fique atento às sombras. Elas imitam vozes. Não confie em nada que se mexe.'"},
        ]

        for item in self.interagiveis:
            if item["tipo"] == "teste":
                self.canvas.create_rectangle(item["x"] - 20, item["y"] - 20, item["x"] + 20, item["y"] + 20, fill="#6FE7BE", outline="#3AA885")
            elif item["tipo"] == "item":
                self.canvas.create_oval(item["x"] - 15, item["y"] - 15, item["x"] + 15, item["y"] + 15, fill="#B5A7FF", outline="#D6CEFF")
            else:
                self.canvas.create_oval(item["x"] - 12, item["y"] - 12, item["x"] + 12, item["y"] + 12, fill="#F9D98A", outline="#E7B554")

        self.canvas.create_text(520, 30, text="BUNKER — Exile", fill=DESTAQUE, font=("Consolas", 18, "bold"))
        self.canvas.create_text(520, 610, text="Move com WASD/Setas. Interaja com E ou espaço.", fill=SUAVE, font=("Consolas", 11))

    def _desenhar_jogador(self):
        self.player = self.canvas.create_oval(self.player_x - 12, self.player_y - 12, self.player_x + 12, self.player_y + 12, fill="#7CE0BF", outline="#E8FFF5")
        self._desenhar_pessoa(self.canvas, self.player_x, self.player_y, self.jogador.nome, CLASSES[self.classe_atual]["pele"], CLASSES[self.classe_atual]["roupa"], CLASSES[self.classe_atual]["acessorio"], sex="m")

    def _desenhar_npcs(self):
        for npc in self.interagiveis:
            if npc["tipo"] == "npc":
                self._desenhar_pessoa(self.canvas, npc["x"], npc["y"], npc["nome"].split()[0], "#E8C5A6", "#607D99", "#93D7D0")

    def _desenhar_hud(self):
        self.d20_var = tk.StringVar(value="D20: —")
        self.d20_label = tk.Label(self.container, textvariable=self.d20_var, fg=DESTAQUE, bg=FUNDO, font=("Consolas", 18, "bold"))
        self.d20_label.place(x=18, y=70)

        self.dialogo_var = tk.StringVar(value="")
        self.dialogo = tk.Label(self.container, textvariable=self.dialogo_var, fg=TEXTO, bg=FUNDO, justify="left", wraplength=480, font=("Consolas", 11))
        self.dialogo.place(x=18, y=100)

    def _atualizar_hud(self):
        self.hp_label.configure(text=f"HP: {self.jogador.hp}/{CLASSES[self.classe_atual]['hp']}")

    def _posicao_valida(self, x, y):
        if x < 60 or y < 60 or x > 980 or y > 590:
            return False
        for rx1, ry1, rx2, ry2 in self.parede:
            if rx1 <= x <= rx2 and ry1 <= y <= ry2:
                return False
        return True

    def _on_key(self, event):
        if self._estado != "mundo":
            return
        dx = 0
        dy = 0
        keys = {"w": (0, -self.movimento), "W": (0, -self.movimento), "Up": (0, -self.movimento), "a": (-self.movimento, 0), "A": (-self.movimento, 0), "Left": (-self.movimento, 0), "s": (0, self.movimento), "S": (0, self.movimento), "Down": (0, self.movimento), "d": (self.movimento, 0), "D": (self.movimento, 0), "Right": (self.movimento, 0)}
        if event.keysym in keys:
            dx, dy = keys[event.keysym]
        nx = self.player_x + dx
        ny = self.player_y + dy
        if self._posicao_valida(nx, ny):
            self.player_x = nx
            self.player_y = ny
            self.canvas.coords(self.player, self.player_x - 12, self.player_y - 12, self.player_x + 12, self.player_y + 12)
            self._redesenhar_pessoa_jogador()
            self._verificar_interacao()

    def _redesenhar_pessoa_jogador(self):
        for item in self.canvas.find_all():
            if self.canvas.type(item) == "oval" and self.canvas.coords(item)[:2] == [self.player_x - 12, self.player_y - 12]:
                pass
        self.canvas.delete("jogador")
        self._desenhar_pessoa(self.canvas, self.player_x, self.player_y, self.jogador.nome, CLASSES[self.classe_atual]["pele"], CLASSES[self.classe_atual]["roupa"], CLASSES[self.classe_atual]["acessorio"], sexo="m")
        self.canvas.gettags(self.canvas.find_all()[-1])

    def _verificar_interacao(self):
        self.interacao_atual = None
        for item in self.interagiveis:
            dist = ((self.player_x - item["x"]) ** 2 + (self.player_y - item["y"]) ** 2) ** 0.5
            if dist < 42:
                self.interacao_atual = item
                self.dialogo_var.set(f"Pressione E ou espaço para interagir com {item['nome']}")
                return
        self.dialogo_var.set("")

    def _interagir(self, event=None):
        if self.interacao_atual is None:
            return
        item = self.interacao_atual
        if item["tipo"] == "dialogo":
            self.dialogo_var.set(item["texto"])
            return
        if item["tipo"] == "npc":
            self.dialogo_var.set(item["texto"])
            return
        if item["tipo"] == "item":
            self.dialogo_var.set("Você encontrou um módulo de energia para o mini-foguete.")
            self.pecas.add("Módulo de Energia")
            self.interagiveis.remove(item)
            self._montar_mapa()
            self._desenhar_jogador()
            self._desenhar_npcs()
            self._desenhar_hud()
            self._atualizar_hud()
            return
        if item["tipo"] == "teste":
            self._teste_escada()

    def _teste_escada(self):
        self.dialogo_var.set("Você tenta subir a escada. Rolagem do D20 em andamento...")
        self._animar_dado(lambda valor: self._resolver_escada(valor))

    def _animar_dado(self, depois):
        valores = [random.randint(1, 20) for _ in range(12)]

        def passo(i=0):
            if i < len(valores):
                self.d20_var.set(f"D20: {valores[i]}")
                self.container.after(60, lambda: passo(i + 1))
                return
            self.d20_var.set(f"D20: {valores[-1]}")
            depois(valores[-1])

        passo()

    def _resolver_escada(self, valor):
        bonus = 2 if self.classe_atual == "Engenheiro" else 0
        total = valor + bonus
        if total >= 12:
            self.dialogo_var.set(f"Sucesso! Você escalou com segurança. D20 {valor} + bônus {bonus} = {total}.")
            self.pecas.add("Plataforma da estação")
            self.jogador.hp = min(CLASSES[self.classe_atual]["hp"], self.jogador.hp + 6)
        else:
            dano = max(3, 10 - self.jogador.defesa)
            self.jogador.hp = max(0, self.jogador.hp - dano)
            self.dialogo_var.set(f"Falhou. Você escorrega, perde {dano} de vida e cai de volta. D20 {valor} + bônus {bonus} = {total}.")
        self._atualizar_hud()


if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("1100x720")
    container = ctk.CTkFrame(root, fg_color=FUNDO)
    container.pack(fill="both", expand=True)
    Jogo(container, ao_menu=lambda: None)
    root.mainloop()
