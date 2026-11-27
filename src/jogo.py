import math
from pathlib import Path
import secrets
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk
from PIL import Image, ImageTk

from audio import AudioPassos
from combate import atacar, rolar_d20
from dice_anim import AnimadorD20
from models import Entidade
from savegame import VERSAO_SAVE, salvar_jogo


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

INVENTARIOS_INICIAIS = {
    "Engenheiro": {"Kit Médico": 1, "EMP": 1},
    "Segurança": {"Kit Médico": 1, "Adrenalina": 1},
    "Cientista": {"Kit Médico": 1, "Adrenalina": 1, "EMP": 1},
}
ITENS_USAVEIS = {
    "Kit Médico": 12,
    "Adrenalina": 8,
}
NOME_CHAVE_PRATA = "Chave de Prata"
NOME_CHAVE_FENDA = "Chave de Fenda"
NOME_MODULO_CAPSULA = "Módulo de Energia da Cápsula"
HP_ANOMALIA_SALA2 = 24
ATAQUE_ANOMALIA_SALA2 = 5
DEFESA_ANOMALIA_SALA2 = 3
RAIO_ENCONTRO_SALA2 = 82
TEXTO_MORTE_GLITCH = (
    "Você sente o Glitch percorrer cada veia do seu corpo. A anomalia invade "
    "seus sentidos, devora sua força e, antes que possa gritar, consome tudo "
    "o que resta de você."
)

LARGURA_MUNDO = 960
ALTURA_MUNDO = 540
VELOCIDADE_JOGADOR = 3.9
SPAWN_INICIAL = (235, 410)
TAMANHO_PERSONAGEM = {
    "sala_hibernacao": 128,
    "corredor": 256,
    "sala_1": 128,
    "sala_2": 128,
}
RAIO_JOGADOR = {
    "sala_hibernacao": 18,
    "corredor": 36,
    "sala_1": 18,
    "sala_2": 18,
}

IMAGENS_SALAS = {
    "sala_hibernacao": Path(__file__).resolve().parents[1] / "assets" / "cenarios" / "Sala_Hibernação.png",
    "corredor": Path(__file__).resolve().parents[1] / "assets" / "cenarios" / "Corredor.png",
    "sala_1": Path(__file__).resolve().parents[1] / "assets" / "cenarios" / "Sala1.png",
    "sala_2": Path(__file__).resolve().parents[1] / "assets" / "cenarios" / "Sala2.png",
}
IMAGEM_SALA1_TV_LIGADA = (
    Path(__file__).resolve().parents[1]
    / "assets"
    / "cenarios"
    / "Sala1_TV_LIGADA.png"
)
IMAGEM_COFRE_SALA1 = (
    Path(__file__).resolve().parents[1]
    / "assets"
    / "cenarios"
    / "Cofre.png"
)
AUDIO_PASSOS = Path(__file__).resolve().parents[1] / "assets" / "audios" / "passos.mp3"
IMAGENS_ITENS = {
    "Kit Médico": Path(__file__).resolve().parents[1] / "assets" / "itens" / "kit_medico.png",
    "Chave Dourada": Path(__file__).resolve().parents[1] / "assets" / "itens" / "pixil-frame-0 (70).png",
    NOME_CHAVE_PRATA: Path(__file__).resolve().parents[1] / "assets" / "itens" / "Chave_prata.png",
}

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
    # Segmentos em degraus acompanham as bordas diagonais do piso do corredor.
    "corredor": [
        (385, 0, 190, 210),
        (0, 210, 354, 40),
        (0, 250, 344, 45),
        (0, 295, 304, 40),
        (0, 335, 294, 45),
        (0, 380, 254, 40),
        (0, 420, 244, 40),
        (0, 460, 224, 40),
        (0, 500, 204, 40),
        (610, 210, 350, 70),
        (635, 280, 325, 35),
        (660, 315, 300, 35),
        (684, 350, 276, 40),
        (708, 390, 252, 40),
        (730, 430, 230, 40),
        (752, 470, 208, 40),
        (774, 510, 186, 30),
    ],
    "sala_1": [
        (0, 0, 960, 210),
        (0, 210, 125, 35),
        (0, 245, 110, 50),
        (0, 295, 90, 55),
        (0, 350, 68, 60),
        (0, 410, 40, 65),
        (0, 475, 10, 65),
        (835, 210, 125, 40),
        (860, 250, 100, 50),
        (880, 300, 80, 50),
        (900, 350, 60, 60),
        (920, 410, 40, 60),
        (940, 470, 20, 70),
        (144, 205, 74, 38),
        (240, 205, 74, 38),
    ],
    "sala_2": [
        (195, 205, 137, 48),
        (405, 205, 145, 48),
        (628, 205, 137, 48),
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
    "sala_1": [
        {
            "retangulo": (390, 475, 180, 65),
            "destino": "corredor",
            "spawn": (350, 450),
        },
    ],
    "sala_2": [
        {
            "retangulo": (390, 495, 180, 45),
            "destino": "corredor",
            "spawn": (440, 350),
        },
    ],
}

PORTAS_CORREDOR = [
    {"numero": 1, "retangulo": (265, 400, 80, 100)},
    {"numero": 2, "retangulo": (350, 285, 70, 95)},
    {"numero": 3, "retangulo": (550, 210, 80, 70)},
    {"numero": 4, "retangulo": (650, 400, 80, 100)},
]
ITEM_CHAVE_DOURADA = {
    "nome": "Chave Dourada",
    "sala": "sala_1",
    "x": 850,
    "y": 470,
}
PISTA_COFRE_SALA1 = "Código do Cofre"
NOME_PECA_FOGUETE_SALA1 = "Módulo de Energia"
NOME_PECA_COFRE_SALA1 = "Módulo de Propulsão"
ZONA_CAPSULA_ESQUERDA = (30, 375, 150, 525)
POSICAO_GLITCH_SALA2 = (480, 360)
TAMANHO_GLITCH_SALA2 = 112
ZONAS_ESTANTES_SALA2 = (
    (190, 260, 345, 330),
    (400, 260, 555, 330),
    (620, 260, 775, 330),
)
RECOMPENSAS_ESTANTES_SALA2 = (
    NOME_CHAVE_PRATA,
    None,
    NOME_CHAVE_FENDA,
)
ZONA_TV_SALA1 = (395, 190, 565, 305)
ZONAS_ARMARIOS_SALA1 = (
    (115, 205, 235, 315),
    (225, 205, 355, 315),
)
ZONA_QUADRO_SALA1 = (650, 200, 800, 300)
POSICAO_COFRE_SALA1 = (720, 88)
TEXTO_TRANSMISSAO_SALA1 = (
    "Alerta de emergência: as anomalias romperam o perímetro da cidade e "
    "as equipes de contenção perderam contato com vários bairros. "
    "Evite as ruas e não tente atravessar as áreas isoladas.\n\n"
    "Não saia de casa. Tranque portas e janelas, apague as luzes e mantenha "
    "silêncio. Não abra a porta para vozes conhecidas vindas do lado de fora: "
    "há relatos de criaturas que imitam pessoas desaparecidas.\n\n"
    "A evacuação subterrânea foi transferida para o bunker. A última nave "
    "de transporte seguirá para a estação orbital, onde ainda existe abrigo "
    "e uma rota para deixar a Terra. Se você estiver ouvindo esta gravação, "
    "procure a saída do bunker e siga para a estação. Boa sorte."
)


def _gerar_codigo_cofre_sala1():
    return f"{secrets.randbelow(10_000):04d}"


def _ponto_dentro(retangulo, x, y):
    esquerda, topo, direita, base = retangulo
    return esquerda <= x <= direita and topo <= y <= base


def _ampliar_desenho_icone(imagem, escala=1.25):
    caixa = imagem.getchannel("A").getbbox()
    if caixa is None:
        return imagem.copy()

    desenho = imagem.crop(caixa)
    tamanho = (
        min(imagem.width, round(desenho.width * escala)),
        min(imagem.height, round(desenho.height * escala)),
    )
    desenho = desenho.resize(tamanho, Image.Resampling.NEAREST)
    ampliada = Image.new("RGBA", imagem.size)
    ampliada.alpha_composite(
        desenho,
        (
            (imagem.width - tamanho[0]) // 2,
            (imagem.height - tamanho[1]) // 2,
        ),
    )
    return ampliada


def _numero_finito(valor):
    try:
        return math.isfinite(valor)
    except OverflowError:
        return False


LIMITES_SALAS = {
    "sala_hibernacao": (20, 25, 940, 520),
    "corredor": (20, 25, 940, 520),
    "sala_1": (20, 25, 940, 520),
    "sala_2": (20, 230, 940, 520),
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
    def __init__(self, container, ao_menu, save_data=None):
        self.container = container
        self.ao_menu = ao_menu
        self.container.configure(fg_color=FUNDO)
        self.jogador = None
        self.inventario = {}
        self.itens_no_chao = []
        self.xp = 0
        self.xp_proximo_nivel = 100
        self.pecas = set()
        self.ataque_extra = 0
        self.log = "Você entrou no bunker. A missão começa agora."
        self._estado = "selecao"

        if save_data is None:
            self._setup_tela_selecao()
        else:
            self._restaurar_progresso(save_data)

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
        self.inventario = INVENTARIOS_INICIAIS[nome_classe].copy()
        self.jogador_nome = nome
        self.sala_atual = "sala_hibernacao"
        self.player_x, self.player_y = SPAWN_INICIAL
        self.direcao = "cima"
        self.itens_no_chao = [ITEM_CHAVE_DOURADA.copy()]
        self.tv_sala1_ligada = False
        self.armarios_sala1_investigados = False
        self.armarios_sala1_arrombados = False
        self.codigo_cofre_sala1 = _gerar_codigo_cofre_sala1()
        self.quadro_sala1_investigado = False
        self.cofre_sala1_aberto = False
        self.porta3_tentativa_usada = False
        self.porta3_aberta = False
        self.anomalia_sala2_derrotada = False
        self.estantes_sala2_investigadas = []
        self.modulo_capsula_retirado = False
        self.xp = 0
        self.xp_proximo_nivel = 100
        self.pecas = set()
        self.ataque_extra = 0
        self._estado = "mundo"
        try:
            self._iniciar_mapa()
        except (OSError, ValueError, tk.TclError) as erro:
            self._estado = "selecao"
            messagebox.showerror(
                "Erro ao iniciar",
                f"Não foi possível carregar o jogo:\n{erro}",
                parent=self.container.winfo_toplevel(),
            )
            self._setup_tela_selecao()

    def _restaurar_progresso(self, dados):
        if not isinstance(dados, dict):
            raise ValueError("O arquivo de save está incompleto ou inválido.")
        try:
            jogador = dados["jogador"]
            nome = jogador["nome"]
            classe = jogador["classe"]
            sala = dados["sala_atual"]
            posicao = dados["posicao"]
            direcao = dados["direcao"]
            inventario = dados["inventario"]
            itens_no_chao = dados["itens_no_chao"]
            xp = dados["xp"]
            xp_proximo_nivel = dados["xp_proximo_nivel"]
            pecas = dados["pecas"]
            ataque_extra = dados["ataque_extra"]
            hp = jogador["hp"]
            ataque = jogador["ataque"]
            defesa = jogador["defesa"]
            nivel = jogador["nivel"]
            porta3_tentativa_usada = dados.get("porta3_tentativa_usada", False)
            porta3_aberta = dados.get("porta3_aberta", False)
            tv_sala1_ligada = dados.get("tv_sala1_ligada", False)
            armarios_sala1_investigados = dados.get(
                "armarios_sala1_investigados",
                False,
            )
            armarios_sala1_arrombados = dados.get(
                "armarios_sala1_arrombados",
                False,
            )
            codigo_cofre_sala1 = dados.get("codigo_cofre_sala1")
            quadro_sala1_investigado = dados.get(
                "quadro_sala1_investigado",
                False,
            )
            cofre_sala1_aberto = dados.get("cofre_sala1_aberto", False)
            anomalia_sala2_derrotada = dados.get(
                "anomalia_sala2_derrotada",
                False,
            )
            estantes_sala2_investigadas = dados.get(
                "estantes_sala2_investigadas",
                [],
            )
            modulo_capsula_retirado = dados.get(
                "modulo_capsula_retirado",
                False,
            )
        except (KeyError, TypeError) as erro:
            raise ValueError("O arquivo de save está incompleto ou inválido.") from erro

        if dados.get("versao") != VERSAO_SAVE:
            raise ValueError("A versão do arquivo de save não é compatível.")
        if not isinstance(porta3_tentativa_usada, bool) or not isinstance(
            porta3_aberta, bool
        ):
            raise ValueError("O estado da porta 3 no save é inválido.")
        if any(
            not isinstance(valor, bool)
            for valor in (
                tv_sala1_ligada,
                armarios_sala1_investigados,
                armarios_sala1_arrombados,
                quadro_sala1_investigado,
                cofre_sala1_aberto,
                anomalia_sala2_derrotada,
                modulo_capsula_retirado,
            )
        ):
            raise ValueError("O estado das salas no save é inválido.")
        if (
            not isinstance(estantes_sala2_investigadas, list)
            or any(
                isinstance(indice, bool)
                or not isinstance(indice, int)
                or indice not in range(len(ZONAS_ESTANTES_SALA2))
                for indice in estantes_sala2_investigadas
            )
            or len(set(estantes_sala2_investigadas))
            != len(estantes_sala2_investigadas)
        ):
            raise ValueError("O estado das estantes da Sala 2 no save é inválido.")
        if codigo_cofre_sala1 is None:
            codigo_cofre_sala1 = _gerar_codigo_cofre_sala1()
        elif (
            not isinstance(codigo_cofre_sala1, str)
            or len(codigo_cofre_sala1) != 4
            or not codigo_cofre_sala1.isascii()
            or not codigo_cofre_sala1.isdigit()
        ):
            raise ValueError("O código do cofre no save é inválido.")
        if cofre_sala1_aberto and not quadro_sala1_investigado:
            raise ValueError("O estado do cofre no save é inválido.")
        if (
            not isinstance(nome, str)
            or not nome.strip()
            or not isinstance(classe, str)
            or classe not in CLASSES
        ):
            raise ValueError("O personagem do save é inválido.")
        if (
            not isinstance(sala, str)
            or sala not in IMAGENS_SALAS
            or not isinstance(direcao, str)
            or direcao not in SPRITES_JOGADOR
        ):
            raise ValueError("A sala ou direção do save é inválida.")
        if (
            not isinstance(posicao, list)
            or len(posicao) != 2
            or any(
                isinstance(coordenada, bool)
                or not isinstance(coordenada, (int, float))
                or not _numero_finito(coordenada)
                for coordenada in posicao
            )
        ):
            raise ValueError("A posição do personagem no save é inválida.")
        if not isinstance(inventario, dict) or any(
            not isinstance(item, str)
            or isinstance(quantidade, bool)
            or not isinstance(quantidade, int)
            or quantidade < 1
            for item, quantidade in inventario.items()
        ):
            raise ValueError("O inventário do save é inválido.")
        if not isinstance(itens_no_chao, list) or any(
            not isinstance(item, dict)
            or not isinstance(item.get("nome"), str)
            or not isinstance(item.get("sala"), str)
            or item.get("sala") not in IMAGENS_SALAS
            or isinstance(item.get("x"), bool)
            or not isinstance(item.get("x"), (int, float))
            or not _numero_finito(item["x"])
            or isinstance(item.get("y"), bool)
            or not isinstance(item.get("y"), (int, float))
            or not _numero_finito(item["y"])
            for item in itens_no_chao
        ):
            raise ValueError("Os itens no chão do save são inválidos.")
        if (
            isinstance(xp, bool)
            or not isinstance(xp, int)
            or xp < 0
            or isinstance(xp_proximo_nivel, bool)
            or not isinstance(xp_proximo_nivel, int)
            or xp_proximo_nivel < 1
            or not isinstance(pecas, list)
            or any(not isinstance(peca, str) for peca in pecas)
            or isinstance(ataque_extra, bool)
            or not isinstance(ataque_extra, int)
        ):
            raise ValueError("Os atributos de progressão do save são inválidos.")
        if any(
            isinstance(valor, bool) or not isinstance(valor, int)
            for valor in (hp, ataque, defesa, nivel)
        ):
            raise ValueError("Os atributos do personagem no save são inválidos.")
        if not 0 <= hp <= CLASSES[classe]["hp"] or nivel < 1:
            raise ValueError("A vida ou o nível do personagem no save é inválido.")

        self.jogador = Entidade(nome, hp, ataque, defesa, nivel)
        self.classe_atual = classe
        self.jogador_nome = nome
        self.sala_atual = sala
        self.player_x, self.player_y = posicao
        self.direcao = direcao
        self.inventario = inventario.copy()
        self.itens_no_chao = [item.copy() for item in itens_no_chao]
        self.porta3_tentativa_usada = porta3_tentativa_usada
        self.porta3_aberta = porta3_aberta
        self.tv_sala1_ligada = tv_sala1_ligada
        self.armarios_sala1_investigados = armarios_sala1_investigados
        self.armarios_sala1_arrombados = armarios_sala1_arrombados
        self.codigo_cofre_sala1 = codigo_cofre_sala1
        self.quadro_sala1_investigado = quadro_sala1_investigado
        self.cofre_sala1_aberto = cofre_sala1_aberto
        self.anomalia_sala2_derrotada = anomalia_sala2_derrotada
        self.estantes_sala2_investigadas = list(estantes_sala2_investigadas)
        self.modulo_capsula_retirado = modulo_capsula_retirado
        if (
            "tv_sala1_ligada" not in dados
            and "Chave Dourada" not in self.inventario
        ):
            chave_no_chao = next(
                (
                    item
                    for item in self.itens_no_chao
                    if item["nome"] == "Chave Dourada"
                ),
                None,
            )
            if chave_no_chao is None:
                self.itens_no_chao.append(ITEM_CHAVE_DOURADA.copy())
            else:
                chave_no_chao.update(ITEM_CHAVE_DOURADA)
        for nome_item in tuple(self.inventario):
            if nome_item == PISTA_COFRE_SALA1 or nome_item.startswith(
                f"{PISTA_COFRE_SALA1}:"
            ):
                del self.inventario[nome_item]
        if self.armarios_sala1_investigados:
            self.inventario[self._nome_pista_cofre_sala1()] = 1
        self.xp = xp
        self.xp_proximo_nivel = xp_proximo_nivel
        self.pecas = set(pecas)
        if self.armarios_sala1_arrombados:
            self.pecas.add(NOME_PECA_FOGUETE_SALA1)
        if self.cofre_sala1_aberto:
            self.pecas.add(NOME_PECA_COFRE_SALA1)
        if self.modulo_capsula_retirado:
            self.pecas.add(NOME_MODULO_CAPSULA)
        self.ataque_extra = ataque_extra
        self._estado = "mundo"
        if not self._posicao_valida(self.player_x, self.player_y):
            raise ValueError("A posição do personagem no save está bloqueada.")
        self._iniciar_mapa()

    def _dados_salvamento(self):
        return {
            "versao": VERSAO_SAVE,
            "jogador": {
                "nome": self.jogador.nome,
                "classe": self.classe_atual,
                "hp": self.jogador.hp,
                "ataque": self.jogador.ataque,
                "defesa": self.jogador.defesa,
                "nivel": self.jogador.nivel,
            },
            "sala_atual": self.sala_atual,
            "posicao": [self.player_x, self.player_y],
            "direcao": self.direcao,
            "inventario": self.inventario.copy(),
            "itens_no_chao": [item.copy() for item in self.itens_no_chao],
            "porta3_tentativa_usada": self.porta3_tentativa_usada,
            "porta3_aberta": self.porta3_aberta,
            "tv_sala1_ligada": self.tv_sala1_ligada,
            "armarios_sala1_investigados": self.armarios_sala1_investigados,
            "armarios_sala1_arrombados": self.armarios_sala1_arrombados,
            "codigo_cofre_sala1": self.codigo_cofre_sala1,
            "quadro_sala1_investigado": self.quadro_sala1_investigado,
            "cofre_sala1_aberto": self.cofre_sala1_aberto,
            "anomalia_sala2_derrotada": self.anomalia_sala2_derrotada,
            "estantes_sala2_investigadas": list(
                self.estantes_sala2_investigadas
            ),
            "modulo_capsula_retirado": self.modulo_capsula_retirado,
            "xp": self.xp,
            "xp_proximo_nivel": self.xp_proximo_nivel,
            "pecas": sorted(self.pecas),
            "ataque_extra": self.ataque_extra,
        }

    def _salvar_progresso(self):
        try:
            salvar_jogo(self._dados_salvamento())
        except (OSError, TypeError, ValueError) as erro:
            messagebox.showerror(
                "Erro ao salvar",
                f"Não foi possível salvar o jogo:\n{erro}",
                parent=self.container.winfo_toplevel(),
            )
            return False
        self.dialogo_var.set("Jogo salvo.")
        return True

    def _voltar_menu(self):
        if not self._salvar_progresso():
            return
        self._parar_animacao_anomalia_sala2()
        self._cancelar_animacao_morte()
        self.audio_passos.parar()
        self._estado = "menu"
        self.ao_menu()

    def _sair_do_jogo(self):
        salvar = messagebox.askyesnocancel(
            "Sair do jogo",
            "Deseja salvar o progresso antes de sair?",
            parent=self.container.winfo_toplevel(),
        )
        if salvar is None:
            return
        if salvar and not self._salvar_progresso():
            return
        self._parar_animacao_anomalia_sala2()
        self._cancelar_animacao_morte()
        self.audio_passos.parar()
        self.container.winfo_toplevel().destroy()

    def _iniciar_mapa(self):
        self._limpar()

        self.topo = ctk.CTkFrame(self.container, fg_color="#101B2C")
        self.topo.pack(fill="x", pady=(12, 0), padx=12)

        self.hud_vida = ctk.CTkFrame(self.topo, fg_color="transparent")
        self.hud_vida.pack(side="left", padx=(14, 8), pady=8)
        self.hp_label = ctk.CTkLabel(
            self.hud_vida,
            text="HP: 0/0",
            font=("Consolas", 11, "bold"),
            text_color="#FDE2D2",
        )
        self.hp_label.pack(anchor="w")
        self.hp_bar = ctk.CTkProgressBar(
            self.hud_vida,
            width=180,
            height=12,
            fg_color="#3A1820",
            progress_color="#EF4444",
        )
        self.hp_bar.pack(pady=(3, 0))

        self.acoes_jogo = ctk.CTkFrame(self.topo, fg_color="transparent")
        self.acoes_jogo.pack(side="right", padx=(4, 10), pady=8)
        ctk.CTkButton(
            self.acoes_jogo,
            text="SALVAR",
            width=62,
            height=30,
            font=("Consolas", 10, "bold"),
            fg_color=DESTAQUE,
            hover_color="#2BC5A5",
            text_color=FUNDO,
            command=self._salvar_progresso,
        ).pack(side="left", padx=2)
        ctk.CTkButton(
            self.acoes_jogo,
            text="MENU",
            width=56,
            height=30,
            font=("Consolas", 10, "bold"),
            fg_color="#263244",
            hover_color="#34445B",
            text_color=TEXTO,
            command=self._voltar_menu,
        ).pack(side="left", padx=2)
        ctk.CTkButton(
            self.acoes_jogo,
            text="SAIR",
            width=48,
            height=30,
            font=("Consolas", 10, "bold"),
            fg_color="#7B2E2E",
            hover_color="#A33A3A",
            text_color=TEXTO,
            command=self._sair_do_jogo,
        ).pack(side="left", padx=2)

        self.xp_frame = ctk.CTkFrame(self.topo, fg_color="transparent")
        self.xp_frame.pack(side="right", padx=(8, 14), pady=8)
        self.xp_label = ctk.CTkLabel(
            self.xp_frame,
            text="NÍVEL 1 | XP 0/100",
            font=("Consolas", 11, "bold"),
            text_color=DESTAQUE,
        )
        self.xp_label.pack(anchor="e")
        self.xp_bar = ctk.CTkProgressBar(
            self.xp_frame,
            width=180,
            height=12,
            fg_color="#17312E",
            progress_color=DESTAQUE,
        )
        self.xp_bar.pack(pady=(3, 0))

        self.nome_sala_label = ctk.CTkLabel(
            self.topo,
            text=f"{self.jogador.nome} — {self.classe_atual}",
            font=("Consolas", 19, "bold"),
            text_color=DESTAQUE,
        )
        self.nome_sala_label.pack(side="left", fill="x", expand=True, padx=8, pady=10)

        self.teclas_pressionadas = set()
        self._quadro_animacao = 0
        self._tempo_animacao = 0
        self._ultimo_tamanho = None
        self._fundo_canvas = None
        self._imagem_fundo = None
        self._porta_ocupada = None
        self._porta3_popup_visivel = False
        self._porta4_popup_visivel = False
        self._objeto_interativo_sala1 = None
        self._interacao_sala1_rolando = False
        self._estante_sala2_interativa = None
        self._glitch_popup_visivel = False
        self._anomalia_after_id = None
        self._anomalia_frame = 0
        self._anomalia_paralisada = False
        self._tamanho_sprites_anomalia = None
        self._capsula_popup_visivel = False
        self.anomalia_sala2 = Entidade(
            "Glitch",
            HP_ANOMALIA_SALA2,
            ATAQUE_ANOMALIA_SALA2,
            DEFESA_ANOMALIA_SALA2,
            1,
        )
        self._janela_combate = None
        self._combate_rolando = False
        self._cofre_sala1_canvas = None
        self._imagem_cofre_sala1_tk = None
        self._tela_tv_sala1_aberta = False
        self._senha_cofre_digitada = ""
        self.tela_porta = None
        self.audio_passos = AudioPassos(AUDIO_PASSOS)
        self._imagens_fundo = {
            sala: Image.open(caminho).convert("RGBA")
            for sala, caminho in IMAGENS_SALAS.items()
        }
        self._imagem_tv_ligada = Image.open(IMAGEM_SALA1_TV_LIGADA).convert("RGBA")
        self._imagem_cofre_sala1 = Image.open(IMAGEM_COFRE_SALA1).convert("RGBA")
        pasta_sprites = Path(__file__).resolve().parents[1] / "assets" / "personagem"
        pasta_anomalia = pasta_sprites / "anomalia(glitch)"
        self._sprites_anomalia_originais = tuple(
            Image.open(
                pasta_anomalia / f"Glitch_Posição_{indice}.png"
            ).convert("RGBA")
            for indice in range(1, 4)
        )
        self._sprites_anomalia_redimensionados = ()
        self._imagem_anomalia_tk = None
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
        self._icones_itens = {
            nome: _ampliar_desenho_icone(Image.open(caminho).convert("RGBA"))
            for nome, caminho in IMAGENS_ITENS.items()
        }
        self._icones_itens_chao = {
            nome: ImageTk.PhotoImage(
                imagem.resize((48, 48), Image.Resampling.NEAREST)
            )
            for nome, imagem in self._icones_itens.items()
        }
        self._icones_itens_inventario = {
            nome: ImageTk.PhotoImage(
                imagem.resize((56, 56), Image.Resampling.NEAREST)
            )
            for nome, imagem in self._icones_itens.items()
        }
        self.canvas.bind("<Configure>", self._redimensionar_cena)
        self.canvas.bind("<KeyPress>", self._on_key)
        self.canvas.bind("<KeyRelease>", self._on_key_release)
        self.canvas.focus_set()

        self._desenhar_hud()
        self._atualizar_hud()
        self._iniciar_animacao_anomalia_sala2()

    def _desenhar_hud(self):
        self.d20_imagem = self.canvas.create_image(
            0,
            0,
            anchor="se",
            tags=("hud_d20",),
        )
        self.d20_texto = self.canvas.create_text(
            0,
            0,
            anchor="se",
            fill=DESTAQUE,
            font=("Consolas", 12, "bold"),
            tags=("hud_d20",),
        )
        self.animador_d20 = AnimadorD20(
            self.canvas,
            self.d20_imagem,
            self.d20_texto,
        )
        self.d20_rolagem_imagem = self.canvas.create_image(
            0,
            0,
            anchor="center",
            state="hidden",
            tags=("hud_dado_rolagem",),
        )
        self.d20_rolagem_texto = self.canvas.create_text(
            0,
            0,
            anchor="n",
            fill=DESTAQUE,
            font=("Consolas", 18, "bold"),
            state="hidden",
            tags=("hud_dado_rolagem",),
        )
        self.d20_rolagem_titulo = self.canvas.create_text(
            0,
            0,
            text="TESTE D20: ARROMBAR (18+)",
            anchor="s",
            fill=TEXTO,
            font=("Consolas", 15, "bold"),
            state="hidden",
            tags=("hud_dado_rolagem",),
        )
        self.animador_d20_grande = AnimadorD20(
            self.canvas,
            self.d20_rolagem_imagem,
            self.d20_rolagem_texto,
            ampliacao=4,
        )

        self.mochila_label = tk.Label(
            self.container,
            text="MOCHILA [E]",
            fg=TEXTO,
            bg=FUNDO,
            font=("Consolas", 12, "bold"),
            cursor="hand2",
        )
        self.mochila_label.place(relx=0.98, rely=0.74, anchor="se")
        self.mochila_label.bind("<Button-1>", lambda _event: self._abrir_inventario())

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
        hp_maximo = CLASSES[self.classe_atual]["hp"]
        self.hp_label.configure(text=f"HP: {self.jogador.hp}/{hp_maximo}")
        self.hp_bar.set(max(0, self.jogador.hp / hp_maximo))
        self.xp_label.configure(
            text=f"NÍVEL {self.jogador.nivel} | XP {self.xp}/{self.xp_proximo_nivel}"
        )
        self.xp_bar.set(min(1, self.xp / self.xp_proximo_nivel))

    def _abrir_inventario(self, event=None):
        if self._estado != "mundo":
            return
        self._estado = "inventario"
        self.teclas_pressionadas.clear()
        self.audio_passos.parar()

        self.tela_inventario = tk.Frame(self.container, bg=FUNDO, takefocus=True)
        self.tela_inventario.place(relx=0, rely=0, relwidth=1, relheight=1)
        painel = tk.Frame(self.tela_inventario, bg=PAINEL, padx=24, pady=20)
        painel.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            painel,
            text="MOCHILA",
            fg=DESTAQUE,
            bg=PAINEL,
            font=("Consolas", 22, "bold"),
        ).pack(pady=(0, 12))

        lista_frame = tk.Frame(painel, bg=PAINEL)
        lista_frame.pack()
        self.lista_inventario = tk.Listbox(
            lista_frame,
            width=38,
            height=8,
            selectmode=tk.SINGLE,
            exportselection=False,
            activestyle="none",
            bg="#0E1622",
            fg=TEXTO,
            selectbackground=DESTAQUE,
            selectforeground="#050C14",
            font=("Consolas", 14),
            borderwidth=0,
            highlightthickness=0,
        )
        self.lista_inventario.pack(side="left", fill="both", expand=True)
        barra = tk.Scrollbar(lista_frame, command=self.lista_inventario.yview)
        barra.pack(side="right", fill="y")
        self.lista_inventario.configure(yscrollcommand=barra.set)
        self.lista_inventario.bind("<<ListboxSelect>>", self._atualizar_opcoes_inventario)
        self.lista_inventario.bind("<Double-Button-1>", self._usar_item)
        self.lista_inventario.bind("<Return>", self._usar_item)
        self.lista_inventario.bind("<Delete>", self._jogar_item_no_chao)
        self.lista_inventario.bind("<KeyPress-Escape>", self._fechar_inventario)

        detalhes_item = tk.Frame(painel, bg=PAINEL)
        detalhes_item.pack(fill="x", pady=(10, 4))
        self._icone_item_vazio = tk.PhotoImage(
            master=self.tela_inventario,
            width=56,
            height=56,
        )
        self.inventario_icone = tk.Label(
            detalhes_item,
            image=self._icone_item_vazio,
            bg=PAINEL,
            width=56,
            height=56,
        )
        self.inventario_icone.pack(side="left", padx=(0, 10))
        self.inventario_feedback = tk.Label(
            detalhes_item,
            text="Use as setas para escolher um item.",
            fg=SUAVE,
            bg=PAINEL,
            font=("Consolas", 10),
            anchor="w",
            justify="left",
        )
        self.inventario_feedback.pack(side="left", fill="x", expand=True)

        botoes = tk.Frame(painel, bg=PAINEL)
        botoes.pack(fill="x", pady=(8, 0))
        self.botao_usar = tk.Button(
            botoes,
            text="Usar",
            command=self._usar_item,
            state="disabled",
            fg="#050C14",
            bg=DESTAQUE,
            activebackground="#2BC5A5",
            relief="flat",
            font=("Consolas", 11, "bold"),
            padx=18,
            pady=6,
        )
        self.botao_usar.pack(side="left", padx=(0, 8))
        self.botao_jogar = tk.Button(
            botoes,
            text="Jogar no chão",
            command=self._jogar_item_no_chao,
            state="disabled",
            fg=TEXTO,
            bg="#334155",
            activebackground="#475569",
            relief="flat",
            font=("Consolas", 11, "bold"),
            padx=18,
            pady=6,
        )
        self.botao_jogar.pack(side="left", padx=8)
        tk.Button(
            botoes,
            text="Fechar (ESC)",
            command=self._fechar_inventario,
            fg=TEXTO,
            bg="#263244",
            activebackground="#34445B",
            relief="flat",
            font=("Consolas", 11, "bold"),
            padx=18,
            pady=6,
        ).pack(side="right")

        self._atualizar_lista_inventario()
        self.lista_inventario.focus_set()

    def _itens_inventario_visiveis(self):
        return list(self.inventario.items())

    def _item_selecionado(self):
        selecao = self.lista_inventario.curselection()
        if not selecao or not 0 <= selecao[0] < len(self._itens_inventario):
            return None
        return self._itens_inventario[selecao[0]][0]

    def _atualizar_lista_inventario(self, indice=0):
        self._itens_inventario = self._itens_inventario_visiveis()
        self.lista_inventario.delete(0, tk.END)
        for nome, quantidade in self._itens_inventario:
            texto = nome if nome.startswith("Código do Cofre:") else f"{nome}  x{quantidade}"
            self.lista_inventario.insert(tk.END, texto)
        if self._itens_inventario:
            indice = min(indice, len(self._itens_inventario) - 1)
            self.lista_inventario.selection_set(indice)
            self.lista_inventario.activate(indice)
            self.lista_inventario.see(indice)
        else:
            self.lista_inventario.insert(tk.END, "Inventário vazio")
        self._atualizar_opcoes_inventario()

    def _atualizar_opcoes_inventario(self, event=None):
        item = self._item_selecionado()
        self.botao_usar.configure(
            state="normal" if item in ITENS_USAVEIS else "disabled"
        )
        pode_descartar = item is not None and not item.startswith("Código do Cofre:")
        self.botao_jogar.configure(
            state="normal" if pode_descartar else "disabled"
        )
        if item:
            icone = self._icones_itens_inventario.get(
                item,
                self._icone_item_vazio,
            )
            self.inventario_icone.configure(image=icone)
            self.inventario_feedback.configure(text=f"Selecionado: {item}")
        else:
            self.inventario_icone.configure(image=self._icone_item_vazio)
            self.inventario_feedback.configure(text="Inventário vazio.")

    def _consumir_item(self, nome):
        quantidade = self.inventario[nome] - 1
        if quantidade:
            self.inventario[nome] = quantidade
        else:
            del self.inventario[nome]

    def _usar_item(self, event=None):
        nome = self._item_selecionado()
        if nome not in ITENS_USAVEIS:
            return "break"

        hp_maximo = CLASSES[self.classe_atual]["hp"]
        if self.jogador.hp >= hp_maximo:
            self.inventario_feedback.configure(text="Sua vida já está cheia.")
            return "break"

        cura = min(ITENS_USAVEIS[nome], hp_maximo - self.jogador.hp)
        self.jogador.hp += cura
        self._consumir_item(nome)
        self._atualizar_hud()
        self.inventario_feedback.configure(text=f"{nome}: recuperou {cura} HP.")
        indice = self.lista_inventario.curselection()
        self._atualizar_lista_inventario(indice[0] if indice else 0)
        return "break"

    def _jogar_item_no_chao(self, event=None):
        nome = self._item_selecionado()
        if not nome or nome.startswith("Código do Cofre:"):
            return "break"

        indice = self.lista_inventario.curselection()
        self._consumir_item(nome)
        self.itens_no_chao.append(
            {
                "nome": nome,
                "sala": self.sala_atual,
                "x": self.player_x,
                "y": self.player_y,
            }
        )
        self._desenhar_itens_chao()
        self._atualizar_lista_inventario(indice[0] if indice else 0)
        self.inventario_feedback.configure(text=f"{nome} foi jogado no chão.")
        return "break"

    def _fechar_inventario(self, event=None):
        self.tela_inventario.destroy()
        self._estado = "mundo"
        self.teclas_pressionadas.clear()
        self.canvas.focus_set()
        return "break"

    def _pegar_item_chao(self, indice):
        if not 0 <= indice < len(self.itens_no_chao):
            return
        if self.itens_no_chao[indice]["sala"] != self.sala_atual:
            return
        item = self.itens_no_chao[indice]
        self.inventario[item["nome"]] = self.inventario.get(item["nome"], 0) + 1
        del self.itens_no_chao[indice]
        self._desenhar_itens_chao()
        self.dialogo_var.set(f"Você pegou {item['nome']}.")

    def _desenhar_itens_chao(self):
        self.canvas.delete("item_chao")
        escala_x = self.canvas.winfo_width() / LARGURA_MUNDO
        escala_y = self.canvas.winfo_height() / ALTURA_MUNDO
        visiveis = [
            (indice, item)
            for indice, item in enumerate(self.itens_no_chao)
            if item["sala"] == self.sala_atual
        ]
        for deslocamento, (indice, item) in enumerate(visiveis):
            tag = f"item_chao_{indice}"
            x = (item["x"] + 30 + deslocamento * 8) * escala_x
            y = (item["y"] - 20 - deslocamento * 12) * escala_y
            icone = self._icones_itens_chao.get(item["nome"])
            if icone:
                self.canvas.create_image(
                    x,
                    y,
                    image=icone,
                    tags=("item_chao", tag),
                )
            else:
                meia_largura = 10 * escala_x
                meia_altura = 10 * escala_y
                self.canvas.create_polygon(
                    x,
                    y - meia_altura,
                    x + meia_largura,
                    y,
                    x,
                    y + meia_altura,
                    x - meia_largura,
                    y,
                    fill="#FFE08A",
                    outline="#FFF2C2",
                    tags=("item_chao", tag),
                )
            self.canvas.tag_bind(
                tag,
                "<Button-1>",
                lambda _event, item_indice=indice: self._pegar_item_chao(item_indice),
            )
            self.canvas.tag_bind(
                tag,
                "<Enter>",
                lambda _event: self.canvas.configure(cursor="hand2"),
            )
            self.canvas.tag_bind(
                tag,
                "<Leave>",
                lambda _event: self.canvas.configure(cursor=""),
            )
        if hasattr(self, "player"):
            self.canvas.tag_raise(self.player)
        if hasattr(self, "d20_imagem"):
            self.canvas.tag_raise("hud_d20")
        if self._porta3_popup_visivel:
            self.canvas.tag_raise("porta3_popup")
        if getattr(self, "_glitch_popup_visivel", False):
            self.canvas.tag_raise("glitch_sala2_popup")
        self._desenhar_anomalia_sala2()

    def _posicionar_dado_hud(self):
        largura = self.canvas.winfo_width()
        altura = self.canvas.winfo_height()
        self.canvas.coords(self.d20_imagem, largura - 14, altura - 34)
        self.canvas.coords(self.d20_texto, largura - 14, altura - 8)
        centro_x = largura / 2
        centro_y = altura / 2 - 20
        self.canvas.coords(self.d20_rolagem_imagem, centro_x, centro_y)
        self.canvas.coords(self.d20_rolagem_titulo, centro_x, centro_y - 145)
        self.canvas.coords(self.d20_rolagem_texto, centro_x, centro_y + 132)
        self.canvas.tag_raise("hud_d20")
        self.canvas.tag_raise("hud_dado_rolagem")

    def _atualizar_nome_sala(self):
        nomes = {
            "sala_hibernacao": "SALA DE HIBERNAÇÃO",
            "corredor": "CORREDOR",
            "sala_1": "SALA 1",
            "sala_2": "SALA 2 — ESTANTES",
        }
        nome = nomes[self.sala_atual]
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

        imagem_fundo = self._imagens_fundo[self.sala_atual]
        if self.sala_atual == "sala_1" and self.tv_sala1_ligada:
            imagem_fundo = self._imagem_tv_ligada
        fundo = imagem_fundo.resize((largura, altura), Image.Resampling.LANCZOS)
        self._imagem_fundo = ImageTk.PhotoImage(fundo)
        if self._fundo_canvas is None:
            self._fundo_canvas = self.canvas.create_image(0, 0, anchor="nw", image=self._imagem_fundo)
            self.player = self.canvas.create_image(0, 0, anchor="s")
        else:
            self.canvas.itemconfigure(self._fundo_canvas, image=self._imagem_fundo)
        self.canvas.tag_lower(self._fundo_canvas)
        self._desenhar_itens_chao()

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
        self._posicionar_dado_hud()
        if self._porta3_popup_visivel:
            self._desenhar_opcoes_porta3()
        if self._porta4_popup_visivel:
            self._desenhar_opcoes_porta4()
        if self._glitch_popup_visivel:
            self._desenhar_opcoes_glitch_sala2()
        if self._estante_sala2_interativa is not None:
            self._desenhar_opcoes_estantes_sala2()
        if self._capsula_popup_visivel:
            self._desenhar_opcoes_capsula_esquerda()
        self._desenhar_cofre_sala1(escala_x, escala_y)
        if self._tela_tv_sala1_aberta:
            self._desenhar_transmissao_tv_sala1()

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

    def _desenhar_anomalia_sala2(self):
        if self.sala_atual != "sala_2" or self.anomalia_sala2_derrotada:
            if getattr(self, "_anomalia_canvas", None) is not None:
                self.canvas.delete(self._anomalia_canvas)
                self._anomalia_canvas = None
            return
        if not self._sprites_anomalia_originais:
            return

        escala_x = self.canvas.winfo_width() / LARGURA_MUNDO
        escala_y = self.canvas.winfo_height() / ALTURA_MUNDO
        tamanho = (
            max(1, round(TAMANHO_GLITCH_SALA2 * escala_x)),
            max(1, round(TAMANHO_GLITCH_SALA2 * escala_y)),
        )
        if tamanho != self._tamanho_sprites_anomalia:
            self._sprites_anomalia_redimensionados = tuple(
                ImageTk.PhotoImage(
                    sprite.resize(tamanho, Image.Resampling.NEAREST)
                )
                for sprite in self._sprites_anomalia_originais
            )
            self._tamanho_sprites_anomalia = tamanho
        self._imagem_anomalia_tk = self._sprites_anomalia_redimensionados[
            self._anomalia_frame
        ]
        x, y = POSICAO_GLITCH_SALA2
        coordenadas = (x * escala_x, y * escala_y)
        if getattr(self, "_anomalia_canvas", None) is None:
            self._anomalia_canvas = self.canvas.create_image(
                *coordenadas,
                image=self._imagem_anomalia_tk,
                tags=("anomalia_sala2",),
            )
        else:
            self.canvas.coords(self._anomalia_canvas, *coordenadas)
            self.canvas.itemconfigure(
                self._anomalia_canvas,
                image=self._imagem_anomalia_tk,
                state="normal",
            )
        if hasattr(self, "player"):
            self.canvas.tag_lower(self._anomalia_canvas, self.player)

    def _iniciar_animacao_anomalia_sala2(self):
        self._desenhar_anomalia_sala2()
        if (
            self.sala_atual == "sala_2"
            and not self.anomalia_sala2_derrotada
            and self._anomalia_after_id is None
        ):
            atraso = 100 + secrets.randbelow(301)
            self._anomalia_after_id = self.container.after(
                atraso,
                self._avancar_animacao_anomalia_sala2,
            )

    def _avancar_animacao_anomalia_sala2(self):
        self._anomalia_after_id = None
        if self.sala_atual != "sala_2" or self.anomalia_sala2_derrotada:
            return
        quadros_possiveis = [
            indice
            for indice in range(3)
            if indice != self._anomalia_frame
        ]
        self._anomalia_frame = secrets.choice(quadros_possiveis)
        self._iniciar_animacao_anomalia_sala2()

    def _parar_animacao_anomalia_sala2(self):
        identificador = getattr(self, "_anomalia_after_id", None)
        if identificador is not None:
            self.container.after_cancel(identificador)
            self._anomalia_after_id = None

    def _desenhar_cofre_sala1(self, escala_x, escala_y):
        if self.sala_atual != "sala_1" or not self.quadro_sala1_investigado:
            if self._cofre_sala1_canvas is not None:
                self.canvas.delete(self._cofre_sala1_canvas)
                self._cofre_sala1_canvas = None
            self._imagem_cofre_sala1_tk = None
            return

        tamanho = (
            round(
                self._imagem_cofre_sala1.width
                * LARGURA_MUNDO
                / self._imagens_fundo["sala_1"].width
                * escala_x
            ),
            round(
                self._imagem_cofre_sala1.height
                * ALTURA_MUNDO
                / self._imagens_fundo["sala_1"].height
                * escala_y
            ),
        )
        imagem = self._imagem_cofre_sala1.resize(
            tamanho,
            Image.Resampling.NEAREST,
        )
        self._imagem_cofre_sala1_tk = ImageTk.PhotoImage(imagem)
        x, y = POSICAO_COFRE_SALA1
        coordenadas = (x * escala_x, y * escala_y)
        if self._cofre_sala1_canvas is None:
            self._cofre_sala1_canvas = self.canvas.create_image(
                *coordenadas,
                image=self._imagem_cofre_sala1_tk,
                tags=("cofre_sala1",),
            )
        else:
            self.canvas.coords(self._cofre_sala1_canvas, *coordenadas)
            self.canvas.itemconfigure(
                self._cofre_sala1_canvas,
                image=self._imagem_cofre_sala1_tk,
            )

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
        tecla = event.keysym.lower()
        if self._estado == "transmissao_tv":
            if tecla in {"return", "escape"}:
                self._fechar_transmissao_tv_sala1()
            return "break"
        if self._estado == "senha_cofre":
            if tecla == "return":
                self._confirmar_senha_cofre_sala1()
            elif tecla == "escape":
                self._fechar_entrada_senha_cofre_sala1()
            elif tecla == "backspace":
                self._senha_cofre_digitada = self._senha_cofre_digitada[:-1]
                self._desenhar_entrada_senha_cofre_sala1()
            elif event.char in "0123456789" and len(self._senha_cofre_digitada) < 4:
                self._senha_cofre_digitada += event.char
                self._desenhar_entrada_senha_cofre_sala1()
            return "break"
        if self._estado != "mundo":
            return
        if tecla in TECLAS_MOVIMENTO:
            self.teclas_pressionadas.add(tecla)
        elif tecla == "r":
            self._rolar_teste()
        elif tecla == "e":
            self._abrir_inventario()

    def _on_key_release(self, event):
        self.teclas_pressionadas.discard(event.keysym.lower())

    def _atualizar_movimento(self):
        if self._estado in {
            "porta",
            "inventario",
            "teste_porta",
            "teste_interacao",
            "transmissao_tv",
            "senha_cofre",
            "combate",
        }:
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
            if _ponto_dentro(
                (
                    zona["retangulo"][0],
                    zona["retangulo"][1],
                    zona["retangulo"][0] + zona["retangulo"][2],
                    zona["retangulo"][1] + zona["retangulo"][3],
                ),
                self.player_x,
                self.player_y,
            ):
                self._carregar_sala(zona["destino"], zona["spawn"])
                return
        if self.sala_atual == "corredor":
            self._verificar_porta_corredor()
        elif self.sala_atual == "sala_1":
            self._verificar_interacoes_sala1()
        elif self.sala_atual == "sala_2":
            self._verificar_interacoes_sala2()
        elif self.sala_atual == "sala_hibernacao":
            self._verificar_interacao_capsula_esquerda()

    def _verificar_interacoes_sala1(self):
        perto_da_tv = _ponto_dentro(
            ZONA_TV_SALA1,
            self.player_x,
            self.player_y,
        )
        if perto_da_tv and not self.tv_sala1_ligada:
            self._ligar_tv_sala1()

        perto_do_quadro = self._perto_do_quadro_sala1()
        perto_dos_armarios = any(
            _ponto_dentro(zona, self.player_x, self.player_y)
            for zona in ZONAS_ARMARIOS_SALA1
        )
        if perto_do_quadro:
            if self._objeto_interativo_sala1 == "armarios":
                self._remover_opcoes_armarios_sala1()
            if self._objeto_interativo_sala1 != "cofre":
                self._objeto_interativo_sala1 = "cofre"
                self._desenhar_opcoes_cofre_sala1()
        elif perto_dos_armarios:
            if self._objeto_interativo_sala1 == "cofre":
                self._remover_opcoes_cofre_sala1()
            if self._objeto_interativo_sala1 != "armarios":
                self._objeto_interativo_sala1 = "armarios"
                self._desenhar_opcoes_armarios_sala1()
        elif self._objeto_interativo_sala1 == "armarios":
            self._remover_opcoes_armarios_sala1()
        elif self._objeto_interativo_sala1 == "cofre":
            self._remover_opcoes_cofre_sala1()

    def _verificar_interacoes_sala2(self):
        perto_de_estante = any(
            _ponto_dentro(zona, self.player_x, self.player_y)
            for zona in ZONAS_ESTANTES_SALA2
        )
        distancia_glitch = math.hypot(
            self.player_x - POSICAO_GLITCH_SALA2[0],
            self.player_y - POSICAO_GLITCH_SALA2[1],
        )
        if not self.anomalia_sala2_derrotada:
            if distancia_glitch <= RAIO_ENCONTRO_SALA2 or perto_de_estante:
                if not self._glitch_popup_visivel:
                    self._glitch_popup_visivel = True
                    self._desenhar_opcoes_glitch_sala2()
            elif self._glitch_popup_visivel:
                self._remover_opcoes_glitch_sala2()
            return
        if self._glitch_popup_visivel:
            self._remover_opcoes_glitch_sala2()

        estante = next(
            (
                indice
                for indice, zona in enumerate(ZONAS_ESTANTES_SALA2)
                if _ponto_dentro(zona, self.player_x, self.player_y)
            ),
            None,
        )
        if estante == self._estante_sala2_interativa:
            return
        if self._estante_sala2_interativa is not None:
            self._remover_opcoes_estantes_sala2()
        if estante is not None:
            self._estante_sala2_interativa = estante
            self._desenhar_opcoes_estantes_sala2()

    def _desenhar_opcoes_glitch_sala2(self):
        if not self._glitch_popup_visivel or self.anomalia_sala2_derrotada:
            return
        self.canvas.delete("glitch_sala2_popup")
        escala_x = self.canvas.winfo_width() / LARGURA_MUNDO
        escala_y = self.canvas.winfo_height() / ALTURA_MUNDO
        centro_x = self.canvas.winfo_width() / 2
        topo = 206 * escala_y
        meia_largura = 190 * escala_x
        self.canvas.create_rectangle(
            centro_x - meia_largura,
            topo,
            centro_x + meia_largura,
            topo + 78 * escala_y,
            fill=FUNDO,
            outline="#FF5C69",
            width=2,
            tags=("glitch_sala2_popup",),
        )
        self.canvas.create_text(
            centro_x,
            topo + 22 * escala_y,
            text="O GLITCH BLOQUEIA O CAMINHO",
            fill=TEXTO,
            font=("Consolas", 11, "bold"),
            tags=("glitch_sala2_popup",),
        )
        self.canvas.create_text(
            centro_x,
            topo + 53 * escala_y,
            text="CLIQUE PARA INTERAGIR E LUTAR",
            fill="#FF5C69",
            font=("Consolas", 10, "bold"),
            tags=("glitch_sala2_popup", "glitch_sala2_acao"),
        )
        self.canvas.tag_bind(
            "glitch_sala2_acao",
            "<Button-1>",
            lambda _event: self._interagir_com_glitch_sala2(),
        )
        self.canvas.tag_bind(
            "glitch_sala2_acao",
            "<Enter>",
            lambda _event: self.canvas.configure(cursor="hand2"),
        )
        self.canvas.tag_bind(
            "glitch_sala2_acao",
            "<Leave>",
            lambda _event: self.canvas.configure(cursor=""),
        )
        self.canvas.tag_raise("glitch_sala2_popup")

    def _remover_opcoes_glitch_sala2(self):
        self.canvas.delete("glitch_sala2_popup")
        self.canvas.configure(cursor="")
        self._glitch_popup_visivel = False

    def _interagir_com_glitch_sala2(self):
        perto_do_glitch = math.hypot(
            self.player_x - POSICAO_GLITCH_SALA2[0],
            self.player_y - POSICAO_GLITCH_SALA2[1],
        ) <= RAIO_ENCONTRO_SALA2
        perto_de_estante = any(
            _ponto_dentro(zona, self.player_x, self.player_y)
            for zona in ZONAS_ESTANTES_SALA2
        )
        if (
            self._estado != "mundo"
            or self.sala_atual != "sala_2"
            or self.anomalia_sala2_derrotada
            or not self._glitch_popup_visivel
            or not (perto_do_glitch or perto_de_estante)
        ):
            return
        self._remover_opcoes_glitch_sala2()
        self._iniciar_combate_anomalia_sala2()

    def _desenhar_opcoes_estantes_sala2(self):
        indice = self._estante_sala2_interativa
        if indice is None or not self.anomalia_sala2_derrotada:
            return

        self.canvas.delete("estantes_sala2_popup")
        escala_x = self.canvas.winfo_width() / LARGURA_MUNDO
        escala_y = self.canvas.winfo_height() / ALTURA_MUNDO
        centro_x = (270, 477, 697)[indice] * escala_x
        topo = 290 * escala_y
        recompensa = RECOMPENSAS_ESTANTES_SALA2[indice]
        investigada = indice in self.estantes_sala2_investigadas
        if investigada:
            texto = (
                "A ESTANTE ESTÁ VAZIA"
                if recompensa is None
                else f"ENCONTRADO: {recompensa}"
            )
        else:
            texto = "Investigar (D20 10+)"
        largura = 190 * escala_x
        self.canvas.create_rectangle(
            centro_x - largura / 2,
            topo,
            centro_x + largura / 2,
            topo + 62 * escala_y,
            fill=FUNDO,
            outline=DESTAQUE,
            width=2,
            tags=("estantes_sala2_popup",),
        )
        self.canvas.create_text(
            centro_x,
            topo + 18 * escala_y,
            text=texto,
            fill=SUAVE if investigada else TEXTO,
            font=("Consolas", 10, "bold"),
            tags=("estantes_sala2_popup",),
        )
        if not investigada:
            self.canvas.create_text(
                centro_x,
                topo + 43 * escala_y,
                text="CLIQUE PARA INVESTIGAR",
                fill=DESTAQUE,
                font=("Consolas", 9, "bold"),
                tags=("estantes_sala2_popup", "estante_sala2_acao"),
            )
            self.canvas.tag_bind(
                "estante_sala2_acao",
                "<Button-1>",
                lambda _event, estante_indice=indice: (
                    self._investigar_estante_sala2(estante_indice)
                ),
            )
            self.canvas.tag_bind(
                "estante_sala2_acao",
                "<Enter>",
                lambda _event: self.canvas.configure(cursor="hand2"),
            )
            self.canvas.tag_bind(
                "estante_sala2_acao",
                "<Leave>",
                lambda _event: self.canvas.configure(cursor=""),
            )
        self.canvas.tag_raise("estantes_sala2_popup")

    def _investigar_estante_sala2(self, indice):
        if (
            self._estado != "mundo"
            or self.sala_atual != "sala_2"
            or not self.anomalia_sala2_derrotada
            or indice not in range(len(RECOMPENSAS_ESTANTES_SALA2))
            or indice in self.estantes_sala2_investigadas
            or not _ponto_dentro(
                ZONAS_ESTANTES_SALA2[indice],
                self.player_x,
                self.player_y,
            )
        ):
            return

        self._remover_opcoes_estantes_sala2()
        self._iniciar_teste_interacao(
            10,
            "INVESTIGAR ESTANTE",
            lambda sucesso, _resultado: (
                self._resultado_investigacao_estante_sala2(indice, sucesso)
            ),
        )

    def _resultado_investigacao_estante_sala2(self, indice, sucesso):
        if self.sala_atual != "sala_2":
            return

        if not sucesso:
            self.dialogo_var.set(
                "Você não conseguiu investigar. Pode tentar novamente."
            )
        else:
            self.estantes_sala2_investigadas.append(indice)
            recompensa = RECOMPENSAS_ESTANTES_SALA2[indice]
            if recompensa is None:
                self.dialogo_var.set(
                    "Você investigou a estante, mas não encontrou nada."
                )
            else:
                self.inventario[recompensa] = self.inventario.get(recompensa, 0) + 1
                self.dialogo_var.set(f"Você encontrou: {recompensa}.")

        if _ponto_dentro(
            ZONAS_ESTANTES_SALA2[indice],
            self.player_x,
            self.player_y,
        ):
            self._estante_sala2_interativa = indice
            self._desenhar_opcoes_estantes_sala2()

    def _remover_opcoes_estantes_sala2(self):
        self.canvas.delete("estantes_sala2_popup")
        self.canvas.configure(cursor="")
        self._estante_sala2_interativa = None

    def _verificar_interacao_capsula_esquerda(self):
        perto = _ponto_dentro(
            ZONA_CAPSULA_ESQUERDA,
            self.player_x,
            self.player_y,
        )
        if not perto or self.modulo_capsula_retirado:
            if self._capsula_popup_visivel:
                self._remover_opcoes_capsula_esquerda()
            return
        if not self._capsula_popup_visivel:
            self._capsula_popup_visivel = True
            self._desenhar_opcoes_capsula_esquerda()

    def _desenhar_opcoes_capsula_esquerda(self):
        if not self._capsula_popup_visivel:
            return
        self.canvas.delete("capsula_esquerda_popup")
        escala_x = self.canvas.winfo_width() / LARGURA_MUNDO
        escala_y = self.canvas.winfo_height() / ALTURA_MUNDO
        centro_x = 165 * escala_x
        topo = 300 * escala_y
        tem_ferramenta = self.inventario.get(NOME_CHAVE_FENDA, 0) > 0
        texto = (
            "Retirar módulo (D20 10+)"
            if tem_ferramenta
            else "Precisa de uma Chave de Fenda"
        )
        self.canvas.create_rectangle(
            centro_x - 145 * escala_x,
            topo,
            centro_x + 145 * escala_x,
            topo + 72 * escala_y,
            fill=FUNDO,
            outline=DESTAQUE,
            width=2,
            tags=("capsula_esquerda_popup",),
        )
        self.canvas.create_text(
            centro_x,
            topo + 20 * escala_y,
            text="CÁPSULA DESATIVADA",
            fill=TEXTO,
            font=("Consolas", 10, "bold"),
            tags=("capsula_esquerda_popup",),
        )
        acao_tag = "capsula_esquerda_acao"
        self.canvas.create_text(
            centro_x,
            topo + 49 * escala_y,
            text=texto,
            fill=DESTAQUE if tem_ferramenta else SUAVE,
            font=("Consolas", 9, "bold"),
            tags=("capsula_esquerda_popup", acao_tag),
        )
        if tem_ferramenta:
            self.canvas.tag_bind(
                acao_tag,
                "<Button-1>",
                lambda _event: self._iniciar_retirada_modulo_capsula(),
            )
            self.canvas.tag_bind(
                acao_tag,
                "<Enter>",
                lambda _event: self.canvas.configure(cursor="hand2"),
            )
            self.canvas.tag_bind(
                acao_tag,
                "<Leave>",
                lambda _event: self.canvas.configure(cursor=""),
            )
        self.canvas.tag_raise("capsula_esquerda_popup")

    def _remover_opcoes_capsula_esquerda(self):
        self.canvas.delete("capsula_esquerda_popup")
        self.canvas.configure(cursor="")
        self._capsula_popup_visivel = False

    def _iniciar_retirada_modulo_capsula(self):
        if (
            self._estado != "mundo"
            or self.sala_atual != "sala_hibernacao"
            or self.modulo_capsula_retirado
            or self.inventario.get(NOME_CHAVE_FENDA, 0) < 1
            or not _ponto_dentro(
                ZONA_CAPSULA_ESQUERDA,
                self.player_x,
                self.player_y,
            )
        ):
            return
        self._remover_opcoes_capsula_esquerda()
        self._iniciar_teste_interacao(
            10,
            "RETIRAR MÓDULO DA CÁPSULA",
            self._resultado_retirada_modulo_capsula,
        )

    def _resultado_retirada_modulo_capsula(self, sucesso, _resultado):
        if sucesso:
            self.modulo_capsula_retirado = True
            self.pecas.add(NOME_MODULO_CAPSULA)
            self.dialogo_var.set(
                f"Você retirou {NOME_MODULO_CAPSULA} da cápsula."
            )
        else:
            self.dialogo_var.set(
                "O módulo continua preso. Você pode tentar novamente."
            )
        if not self.modulo_capsula_retirado and _ponto_dentro(
            ZONA_CAPSULA_ESQUERDA,
            self.player_x,
            self.player_y,
        ):
            self._capsula_popup_visivel = True
            self._desenhar_opcoes_capsula_esquerda()

    def _iniciar_combate_anomalia_sala2(self):
        if (
            self._estado != "mundo"
            or self.sala_atual != "sala_2"
            or self.anomalia_sala2_derrotada
        ):
            return

        self._estado = "combate"
        self.teclas_pressionadas.clear()
        self.audio_passos.parar()
        if self._glitch_popup_visivel:
            self._remover_opcoes_glitch_sala2()
        self._estante_sala2_interativa = None
        self._janela_combate = tk.Frame(
            self.container,
            bg=PAINEL,
            padx=18,
            pady=16,
            highlightbackground="#B0204A",
            highlightthickness=2,
            takefocus=True,
        )
        self._janela_combate.place(
            relx=0.985,
            rely=0.15,
            anchor="ne",
        )
        painel = self._janela_combate
        tk.Label(
            painel,
            text="ANOMALIA — GLITCH",
            fg="#FF5C69",
            bg=PAINEL,
            font=("Consolas", 22, "bold"),
        ).pack(pady=(0, 10))
        tk.Label(
            painel,
            text="A criatura bloqueia o caminho. Ataque ou use um item.",
            fg=TEXTO,
            bg=PAINEL,
            font=("Consolas", 11),
        ).pack(pady=(0, 12))
        self._combate_estado_label = tk.Label(
            painel,
            text="",
            fg=DESTAQUE,
            bg=PAINEL,
            font=("Consolas", 12, "bold"),
        )
        self._combate_estado_label.pack(pady=(0, 12))
        self._combate_mensagem_label = tk.Label(
            painel,
            text="",
            fg=TEXTO,
            bg=PAINEL,
            font=("Consolas", 10),
            justify="center",
            wraplength=310,
        )
        self._combate_mensagem_label.pack(pady=(0, 12))

        botoes = tk.Frame(painel, bg=PAINEL)
        botoes.pack(fill="x")
        self._combate_botoes = {}
        self._combate_rolando = False
        acoes = (
            ("punho", "Atacar com as mãos", self._acao_combate_ataque),
            (
                "Kit Médico",
                "Usar Kit Médico",
                lambda: self._acao_combate_item("Kit Médico"),
            ),
            (
                "Adrenalina",
                "Usar Adrenalina",
                lambda: self._acao_combate_item("Adrenalina"),
            ),
            ("EMP", "Usar EMP", lambda: self._acao_combate_item("EMP")),
        )
        for indice, (chave, texto, comando) in enumerate(acoes):
            botao = tk.Button(
                botoes,
                text=texto,
                command=comando,
                fg="#050C14" if chave == "punho" else TEXTO,
                bg=DESTAQUE if chave == "punho" else "#263244",
                activebackground="#2BC5A5",
                relief="flat",
                font=("Consolas", 10, "bold"),
                padx=10,
                pady=8,
            )
            botao.grid(row=indice // 2, column=indice % 2, padx=5, pady=5, sticky="ew")
            self._combate_botoes[chave] = botao
        botoes.grid_columnconfigure(0, weight=1)
        botoes.grid_columnconfigure(1, weight=1)
        self._atualizar_tela_combate(
            "A luta acontece aqui na Sala 2. Escolha uma ação."
        )
        self._janela_combate.lift()
        self._janela_combate.focus_set()

    def _atualizar_tela_combate(self, mensagem):
        self._combate_estado_label.configure(
            text=(
                f"{self.jogador.nome}: {self.jogador.hp} HP"
                f"     |     Glitch: {self.anomalia_sala2.hp} HP"
            )
        )
        self._combate_mensagem_label.configure(text=mensagem)
        bloqueado = getattr(self, "_combate_rolando", False)
        self._combate_botoes["punho"].configure(
            state="disabled" if bloqueado else "normal"
        )
        for item in ITENS_USAVEIS:
            botao = self._combate_botoes[item]
            pode_usar = (
                not bloqueado
                and self.inventario.get(item, 0) > 0
                and self.jogador.hp < CLASSES[self.classe_atual]["hp"]
            )
            botao.configure(state="normal" if pode_usar else "disabled")
        self._combate_botoes["EMP"].configure(
            state=(
                "normal"
                if not bloqueado and self.inventario.get("EMP", 0) > 0
                else "disabled"
            )
        )

    @staticmethod
    def _resumo_ataque_combate(atacante, resultado):
        if resultado.falha_critica:
            return f"{atacante} errou (D20 {resultado.dado})."
        if resultado.critico:
            return (
                f"{atacante} acertou um crítico (D20 {resultado.dado}) "
                f"e causou {resultado.dano} de dano."
            )
        return (
            f"{atacante} tirou {resultado.dado} no D20 "
            f"e causou {resultado.dano} de dano."
        )

    def _acao_combate_ataque(self):
        if self._estado != "combate" or self._combate_rolando:
            return
        self._iniciar_rolagem_combate(
            "ATAQUE DO PLAYER",
            self.jogador,
            self.anomalia_sala2,
            self._resultado_ataque_jogador,
        )

    def _iniciar_rolagem_combate(self, titulo, atacante, defensor, ao_resolver):
        if self._estado != "combate" or self._combate_rolando:
            return

        self._combate_rolando = True
        self._atualizar_tela_combate(f"{titulo}: o D20 está rolando...")
        self._posicionar_dado_hud()
        self.canvas.itemconfigure(self.d20_rolagem_titulo, text=titulo)
        for item in (
            self.d20_rolagem_imagem,
            self.d20_rolagem_texto,
            self.d20_rolagem_titulo,
        ):
            self.canvas.itemconfigure(item, state="normal")
        self.canvas.tag_raise("hud_dado_rolagem")

        def finalizar_rolagem(resultado):
            if self._estado != "combate":
                self._ocultar_dado_rolagem()
                self._combate_rolando = False
                return
            self.animador_d20.mostrar(resultado)
            resultado_ataque = atacar(atacante, defensor, dado=resultado)
            self._atualizar_hud()
            resumo = self._resumo_ataque_combate(
                "Seu soco" if atacante is self.jogador else "A anomalia",
                resultado_ataque,
            )
            self._atualizar_tela_combate(f"{titulo}\n{resumo}")

            def continuar_turno():
                self._ocultar_dado_rolagem()
                self._combate_rolando = False
                if self._estado == "combate":
                    ao_resolver(resultado_ataque)

            self.container.after(2500, continuar_turno)

        try:
            self.animador_d20_grande.rolar_teste(
                finalizar_rolagem,
                resultado=rolar_d20(),
            )
        except (RuntimeError, ValueError, tk.TclError) as erro:
            self._ocultar_dado_rolagem()
            self._combate_rolando = False
            self._atualizar_tela_combate("Não foi possível concluir a rolagem.")
            messagebox.showerror(
                "Erro no combate",
                f"Não foi possível concluir a rolagem de D20:\n{erro}",
                parent=self.container.winfo_toplevel(),
            )
            self.canvas.focus_set()

    def _resultado_ataque_jogador(self, resultado):
        mensagem = self._resumo_ataque_combate("Seu soco", resultado)
        self._resolver_turno_anomalia_sala2(mensagem)

    def _acao_combate_item(self, nome):
        if (
            self._estado != "combate"
            or self._combate_rolando
            or self.inventario.get(nome, 0) < 1
        ):
            return
        if nome in ITENS_USAVEIS:
            hp_maximo = CLASSES[self.classe_atual]["hp"]
            if self.jogador.hp >= hp_maximo:
                return
            cura = min(
                ITENS_USAVEIS[nome],
                hp_maximo - self.jogador.hp,
            )
            self.jogador.hp += cura
            self._consumir_item(nome)
            self._atualizar_hud()
            mensagem = f"{nome}: você recuperou {cura} HP."
        elif nome == "EMP":
            self._consumir_item(nome)
            self._anomalia_paralisada = True
            mensagem = "O EMP atinge o Glitch e o paralisa."
        else:
            return
        self._resolver_turno_anomalia_sala2(mensagem)

    def _resolver_turno_anomalia_sala2(self, mensagem):
        if self.anomalia_sala2.hp <= 0:
            self._vencer_combate_anomalia_sala2()
            return
        if self._anomalia_paralisada:
            self._anomalia_paralisada = False
            self._atualizar_tela_combate(
                f"{mensagem}\nO Glitch perde este turno por causa do EMP."
            )
            return

        self._iniciar_rolagem_combate(
            "ATAQUE DA ANOMALIA",
            self.anomalia_sala2,
            self.jogador,
            lambda resultado: self._resultado_ataque_glitch(
                mensagem,
                resultado,
            ),
        )

    def _resultado_ataque_glitch(self, mensagem, resultado):
        mensagem_inimigo = self._resumo_ataque_combate("O Glitch", resultado)
        if self.jogador.hp <= 0:
            self._atualizar_hud()
            self._fechar_combate_anomalia_sala2()
            self._mostrar_tela_morte(
                TEXTO_MORTE_GLITCH,
                "VOCÊ FOI CONSUMIDO",
            )
            return
        self._atualizar_hud()
        self._atualizar_tela_combate(
            f"{mensagem}\n{mensagem_inimigo}"
        )

    def _vencer_combate_anomalia_sala2(self):
        self.anomalia_sala2_derrotada = True
        self._fechar_combate_anomalia_sala2()
        self.dialogo_var.set(
            "O Glitch cai. As três estantes estão livres para investigação."
        )
        self._desenhar_anomalia_sala2()

    def _fechar_combate_anomalia_sala2(self):
        if getattr(self, "_janela_combate", None) is not None:
            self._janela_combate.destroy()
            self._janela_combate = None
        self._combate_rolando = False
        self._estado = "mundo"
        self.teclas_pressionadas.clear()
        self.canvas.focus_set()

    def _ligar_tv_sala1(self):
        if self.tv_sala1_ligada:
            return
        self.tv_sala1_ligada = True
        self._ultimo_tamanho = None
        self._redimensionar_cena()
        self.dialogo_var.set("A TV exibe uma transmissão de emergência.")
        self._mostrar_transmissao_tv_sala1()

    def _mostrar_transmissao_tv_sala1(self):
        self._estado = "transmissao_tv"
        self.teclas_pressionadas.clear()
        self.audio_passos.parar()
        self._tela_tv_sala1_aberta = True
        self._desenhar_transmissao_tv_sala1()
        self.canvas.focus_set()

    def _desenhar_transmissao_tv_sala1(self):
        self.canvas.delete("tv_sala1_lore")
        largura = self.canvas.winfo_width()
        altura = self.canvas.winfo_height()
        esquerda, topo = largura * 0.1, altura * 0.08
        direita, base = largura * 0.9, altura * 0.92
        self.canvas.create_rectangle(
            esquerda,
            topo,
            direita,
            base,
            fill="#070C14",
            outline=DESTAQUE,
            width=3,
            tags=("tv_sala1_lore",),
        )
        self.canvas.create_text(
            largura / 2,
            topo + altura * 0.075,
            text="TRANSMISSÃO DE EMERGÊNCIA  |  ARQUIVO 07",
            fill="#FFE08A",
            font=("Consolas", 17, "bold"),
            tags=("tv_sala1_lore",),
        )
        self.canvas.create_text(
            esquerda + largura * 0.045,
            topo + altura * 0.15,
            text=TEXTO_TRANSMISSAO_SALA1,
            fill=TEXTO,
            font=("Consolas", 12, "bold"),
            justify="left",
            anchor="nw",
            width=direita - esquerda - largura * 0.09,
            tags=("tv_sala1_lore",),
        )
        fechar = "PRESSIONE ENTER OU ESC PARA FECHAR"
        self.canvas.create_text(
            largura / 2,
            base - altura * 0.055,
            text=fechar,
            fill=DESTAQUE,
            font=("Consolas", 11, "bold"),
            tags=("tv_sala1_lore", "tv_sala1_fechar"),
        )
        self.canvas.tag_bind(
            "tv_sala1_fechar",
            "<Button-1>",
            lambda _event: self._fechar_transmissao_tv_sala1(),
        )
        self.canvas.tag_raise("tv_sala1_lore")

    def _fechar_transmissao_tv_sala1(self):
        self.canvas.delete("tv_sala1_lore")
        self._tela_tv_sala1_aberta = False
        self._estado = "mundo"
        self.dialogo_var.set("A transmissão continua passando na TV.")
        self.canvas.focus_set()

    def _perto_do_quadro_sala1(self):
        return (
            self.sala_atual == "sala_1"
            and _ponto_dentro(
                ZONA_QUADRO_SALA1,
                self.player_x,
                self.player_y,
            )
        )

    def _nome_pista_cofre_sala1(self):
        return f"{PISTA_COFRE_SALA1}: {self.codigo_cofre_sala1}"

    def _desenhar_opcoes_cofre_sala1(self):
        if not self._perto_do_quadro_sala1():
            return

        self.canvas.delete("cofre_sala1_popup")
        escala_x = self.canvas.winfo_width() / LARGURA_MUNDO
        escala_y = self.canvas.winfo_height() / ALTURA_MUNDO
        centro_x = 720 * escala_x
        topo = 215 * escala_y
        meia_largura = 175 * escala_x
        altura = 128 * escala_y
        self.canvas.create_rectangle(
            centro_x - meia_largura,
            topo,
            centro_x + meia_largura,
            topo + altura,
            fill=FUNDO,
            outline=DESTAQUE,
            width=2,
            tags=("cofre_sala1_popup",),
        )
        titulo = (
            "COFRE ABERTO"
            if self.cofre_sala1_aberto
            else "COFRE ENCONTRADO"
            if self.quadro_sala1_investigado
            else "QUADRO NA PAREDE"
        )
        self.canvas.create_text(
            centro_x,
            topo + 16 * escala_y,
            text=titulo,
            fill=TEXTO,
            font=("Consolas", 12, "bold"),
            tags=("cofre_sala1_popup",),
        )
        opcoes = []
        if not self.quadro_sala1_investigado:
            opcoes.append(("investigar", "Investigar (D20 10+)", True))
        elif not self.cofre_sala1_aberto:
            opcoes.append(("senha", "Digitar senha", True))
        else:
            opcoes.append(("aberto", "O cofre está vazio", False))
        opcoes.append(("desistir", "Desistir", True))
        for indice, (acao, texto, habilitada) in enumerate(opcoes):
            tag = f"cofre_sala1_{acao}"
            self.canvas.create_text(
                centro_x,
                topo + (52 + indice * 32) * escala_y,
                text=texto,
                fill=DESTAQUE if habilitada else SUAVE,
                font=("Consolas", 11, "bold"),
                tags=("cofre_sala1_popup", tag),
            )
            if habilitada:
                self.canvas.tag_bind(
                    tag,
                    "<Button-1>",
                    lambda _event, escolha=acao: self._acao_cofre_sala1(escolha),
                )
                self.canvas.tag_bind(
                    tag,
                    "<Enter>",
                    lambda _event: self.canvas.configure(cursor="hand2"),
                )
                self.canvas.tag_bind(
                    tag,
                    "<Leave>",
                    lambda _event: self.canvas.configure(cursor=""),
                )
        self.canvas.tag_raise("cofre_sala1_popup")

    def _remover_opcoes_cofre_sala1(self):
        self.canvas.delete("cofre_sala1_popup")
        self.canvas.configure(cursor="")
        self._objeto_interativo_sala1 = None

    def _acao_cofre_sala1(self, acao):
        if self._estado != "mundo" or not self._perto_do_quadro_sala1():
            return
        if acao == "desistir":
            self._remover_opcoes_cofre_sala1()
            self.canvas.focus_set()
        elif acao == "investigar" and not self.quadro_sala1_investigado:
            self._remover_opcoes_cofre_sala1()
            self._iniciar_teste_interacao(
                10,
                "INVESTIGAR QUADRO",
                lambda sucesso, _resultado: self._resultado_investigacao_quadro_sala1(
                    sucesso
                ),
            )
        elif (
            acao == "senha"
            and self.quadro_sala1_investigado
            and not self.cofre_sala1_aberto
        ):
            self._abrir_entrada_senha_cofre_sala1()

    def _resultado_investigacao_quadro_sala1(self, sucesso):
        if sucesso:
            self.quadro_sala1_investigado = True
            self._ultimo_tamanho = None
            self._redimensionar_cena()
            self.dialogo_var.set("Atrás do quadro, você encontrou um cofre.")
        else:
            self.dialogo_var.set("Você não encontrou nada atrás do quadro.")
        if self._perto_do_quadro_sala1():
            self._objeto_interativo_sala1 = "cofre"
            self._desenhar_opcoes_cofre_sala1()

    def _abrir_entrada_senha_cofre_sala1(self):
        if not self.quadro_sala1_investigado or self.cofre_sala1_aberto:
            return
        self.canvas.delete("cofre_sala1_popup")
        self._estado = "senha_cofre"
        self._senha_cofre_digitada = ""
        self.teclas_pressionadas.clear()
        self.audio_passos.parar()
        self._desenhar_entrada_senha_cofre_sala1()
        self.canvas.focus_set()

    def _desenhar_entrada_senha_cofre_sala1(self):
        self.canvas.delete("cofre_senha_sala1_popup")
        largura = self.canvas.winfo_width()
        altura = self.canvas.winfo_height()
        esquerda, direita = largura * 0.27, largura * 0.73
        topo, base = altura * 0.31, altura * 0.69
        self.canvas.create_rectangle(
            esquerda,
            topo,
            direita,
            base,
            fill=FUNDO,
            outline=DESTAQUE,
            width=3,
            tags=("cofre_senha_sala1_popup",),
        )
        self.canvas.create_text(
            largura / 2,
            topo + altura * 0.07,
            text="COFRE — DIGITE A SENHA DE 4 DÍGITOS",
            fill=TEXTO,
            font=("Consolas", 14, "bold"),
            tags=("cofre_senha_sala1_popup",),
        )
        senha_visivel = self._senha_cofre_digitada.ljust(4, "_")
        self.canvas.create_text(
            largura / 2,
            altura / 2,
            text="  ".join(senha_visivel),
            fill="#FFE08A",
            font=("Consolas", 26, "bold"),
            tags=("cofre_senha_sala1_popup",),
        )
        self.canvas.create_text(
            largura / 2,
            base - altura * 0.065,
            text="ENTER: confirmar     BACKSPACE: apagar     ESC: cancelar",
            fill=DESTAQUE,
            font=("Consolas", 10, "bold"),
            tags=("cofre_senha_sala1_popup",),
        )
        self.canvas.tag_raise("cofre_senha_sala1_popup")

    def _confirmar_senha_cofre_sala1(self):
        if len(self._senha_cofre_digitada) != 4:
            self.dialogo_var.set("Digite os quatro números da senha.")
            return
        if self._senha_cofre_digitada != self.codigo_cofre_sala1:
            self._senha_cofre_digitada = ""
            self.dialogo_var.set("Senha incorreta. Tente novamente.")
            self._desenhar_entrada_senha_cofre_sala1()
            return

        self.cofre_sala1_aberto = True
        self.pecas.add(NOME_PECA_COFRE_SALA1)
        self._fechar_entrada_senha_cofre_sala1()
        self.dialogo_var.set(
            f"Senha correta! Você encontrou {NOME_PECA_COFRE_SALA1}."
        )

    def _fechar_entrada_senha_cofre_sala1(self):
        self.canvas.delete("cofre_senha_sala1_popup")
        self._estado = "mundo"
        self._senha_cofre_digitada = ""
        self.canvas.focus_set()
        if self._perto_do_quadro_sala1():
            self._objeto_interativo_sala1 = "cofre"
            self._desenhar_opcoes_cofre_sala1()
        else:
            self._objeto_interativo_sala1 = None

    def _perto_dos_armarios_sala1(self):
        return (
            self.sala_atual == "sala_1"
            and any(
                _ponto_dentro(zona, self.player_x, self.player_y)
                for zona in ZONAS_ARMARIOS_SALA1
            )
        )

    def _desenhar_opcoes_armarios_sala1(self):
        if not self._perto_dos_armarios_sala1():
            return

        self.canvas.delete("armarios_sala1_popup")
        escala_x = self.canvas.winfo_width() / LARGURA_MUNDO
        escala_y = self.canvas.winfo_height() / ALTURA_MUNDO
        centro_x = 260 * escala_x
        topo = 245 * escala_y
        meia_largura = 205 * escala_x
        altura = 114 * escala_y
        self.canvas.create_rectangle(
            centro_x - meia_largura,
            topo,
            centro_x + meia_largura,
            topo + altura,
            fill=FUNDO,
            outline=DESTAQUE,
            width=2,
            tags=("armarios_sala1_popup",),
        )
        self.canvas.create_text(
            centro_x,
            topo + 16 * escala_y,
            text="ARMÁRIOS",
            fill=TEXTO,
            font=("Consolas", 12, "bold"),
            tags=("armarios_sala1_popup",),
        )
        opcoes = (
            (
                "investigar",
                "Investigar parte aberta (D20 10+)"
                if not self.armarios_sala1_investigados
                else "Parte aberta — código encontrado",
                not self.armarios_sala1_investigados,
            ),
            (
                "arrombar",
                "Arrombar armários (D20 15+)"
                if not self.armarios_sala1_arrombados
                else "Armários arrombados",
                not self.armarios_sala1_arrombados,
            ),
            ("desistir", "Desistir", True),
        )
        for indice, (acao, texto, habilitada) in enumerate(opcoes):
            tag = f"armarios_sala1_{acao}"
            self.canvas.create_text(
                centro_x,
                topo + (42 + indice * 28) * escala_y,
                text=texto,
                fill=DESTAQUE if habilitada else SUAVE,
                font=("Consolas", 10, "bold"),
                tags=("armarios_sala1_popup", tag),
            )
            if habilitada:
                self.canvas.tag_bind(
                    tag,
                    "<Button-1>",
                    lambda _event, escolha=acao: self._acao_armarios_sala1(escolha),
                )
                self.canvas.tag_bind(
                    tag,
                    "<Enter>",
                    lambda _event: self.canvas.configure(cursor="hand2"),
                )
                self.canvas.tag_bind(
                    tag,
                    "<Leave>",
                    lambda _event: self.canvas.configure(cursor=""),
                )
        self.canvas.tag_raise("armarios_sala1_popup")

    def _remover_opcoes_armarios_sala1(self):
        self.canvas.delete("armarios_sala1_popup")
        self.canvas.configure(cursor="")
        self._objeto_interativo_sala1 = None

    def _acao_armarios_sala1(self, acao):
        if self._estado != "mundo" or not self._perto_dos_armarios_sala1():
            return
        if acao == "desistir":
            self._remover_opcoes_armarios_sala1()
            self.canvas.focus_set()
        elif acao == "investigar" and not self.armarios_sala1_investigados:
            self._remover_opcoes_armarios_sala1()
            self._iniciar_teste_interacao(
                10,
                "INVESTIGAR ARMÁRIO",
                lambda sucesso, _resultado: self._resultado_investigacao_armarios(
                    sucesso
                ),
            )
        elif acao == "arrombar" and not self.armarios_sala1_arrombados:
            self._remover_opcoes_armarios_sala1()
            self._iniciar_teste_interacao(
                15,
                "ARROMBAR ARMÁRIOS",
                lambda sucesso, _resultado: self._resultado_arrombamento_armarios(
                    sucesso
                ),
                dano_falha=2,
            )

    def _resultado_investigacao_armarios(self, sucesso):
        if sucesso:
            self.armarios_sala1_investigados = True
            self.inventario[self._nome_pista_cofre_sala1()] = 1
            self.dialogo_var.set(
                f"Você encontrou uma anotação: o código do cofre é "
                f"{self.codigo_cofre_sala1}. O código foi guardado no inventário."
            )
        else:
            self.dialogo_var.set("Você não conseguiu decifrar a anotação.")
        if self._perto_dos_armarios_sala1():
            self._objeto_interativo_sala1 = "armarios"
            self._desenhar_opcoes_armarios_sala1()

    def _resultado_arrombamento_armarios(self, sucesso):
        if sucesso:
            self.armarios_sala1_arrombados = True
            self.pecas.add(NOME_PECA_FOGUETE_SALA1)
            self.dialogo_var.set(
                f"Você arrombou os armários e encontrou {NOME_PECA_FOGUETE_SALA1}."
            )
        if self._perto_dos_armarios_sala1():
            self._objeto_interativo_sala1 = "armarios"
            self._desenhar_opcoes_armarios_sala1()

    def _verificar_porta_corredor(self):
        if self.sala_atual != "corredor":
            return
        if self._porta_ocupada is not None:
            x, y, largura, altura = self._porta_ocupada["retangulo"]
            if x <= self.player_x <= x + largura and y <= self.player_y <= y + altura:
                return
            if self._porta_ocupada["numero"] == 3:
                self._remover_opcoes_porta3()
            elif self._porta_ocupada["numero"] == 4:
                self._remover_opcoes_porta4()
            self._porta_ocupada = None

        for porta in PORTAS_CORREDOR:
            x, y, largura, altura = porta["retangulo"]
            if x <= self.player_x <= x + largura and y <= self.player_y <= y + altura:
                self._porta_ocupada = porta
                if porta["numero"] == 1:
                    self._carregar_sala("sala_1", (480, 430))
                elif porta["numero"] == 2:
                    self._carregar_sala("sala_2", (480, 480))
                elif porta["numero"] == 3:
                    if self.porta3_aberta:
                        self._abrir_porta(3)
                    else:
                        self._desenhar_opcoes_porta3()
                elif porta["numero"] == 4:
                    self._desenhar_opcoes_porta4()
                else:
                    self._abrir_porta(porta["numero"])
                return

    def _jogador_perto_da_porta3(self):
        x, y, largura, altura = PORTAS_CORREDOR[2]["retangulo"]
        return (
            self.sala_atual == "corredor"
            and x <= self.player_x <= x + largura
            and y <= self.player_y <= y + altura
        )

    def _jogador_perto_da_porta4(self):
        x, y, largura, altura = PORTAS_CORREDOR[3]["retangulo"]
        return (
            self.sala_atual == "corredor"
            and x <= self.player_x <= x + largura
            and y <= self.player_y <= y + altura
        )

    def _desenhar_opcoes_porta4(self):
        if not self._jogador_perto_da_porta4():
            return

        self.canvas.delete("porta4_popup")
        self._porta4_popup_visivel = True
        escala_x = self.canvas.winfo_width() / LARGURA_MUNDO
        escala_y = self.canvas.winfo_height() / ALTURA_MUNDO
        centro_x = 690 * escala_x
        topo = 290 * escala_y
        meia_largura = 205 * escala_x
        tem_chave = self.inventario.get(NOME_CHAVE_PRATA, 0) > 0
        self.canvas.create_rectangle(
            centro_x - meia_largura,
            topo,
            centro_x + meia_largura,
            topo + 88 * escala_y,
            fill=FUNDO,
            outline=DESTAQUE if tem_chave else "#FFE08A",
            width=2,
            tags=("porta4_popup",),
        )
        self.canvas.create_text(
            centro_x,
            topo + 20 * escala_y,
            text="PORTA 4 — SALA 4",
            fill=TEXTO,
            font=("Consolas", 12, "bold"),
            tags=("porta4_popup",),
        )
        tag_acao = "porta4_chave"
        self.canvas.create_text(
            centro_x,
            topo + 54 * escala_y,
            text=(
                "ABRIR COM A CHAVE DE PRATA"
                if tem_chave
                else "TRANCADA — PRECISA DA CHAVE DE PRATA"
            ),
            fill=DESTAQUE if tem_chave else SUAVE,
            font=("Consolas", 10, "bold"),
            tags=("porta4_popup", tag_acao),
        )
        if tem_chave:
            self.canvas.tag_bind(
                tag_acao,
                "<Button-1>",
                lambda _event: self._acao_porta4("chave"),
            )
            self.canvas.tag_bind(
                tag_acao,
                "<Enter>",
                lambda _event: self.canvas.configure(cursor="hand2"),
            )
            self.canvas.tag_bind(
                tag_acao,
                "<Leave>",
                lambda _event: self.canvas.configure(cursor=""),
            )
        self.canvas.tag_raise("porta4_popup")

    def _remover_opcoes_porta4(self):
        self.canvas.delete("porta4_popup")
        self.canvas.configure(cursor="")
        self._porta4_popup_visivel = False

    def _acao_porta4(self, acao):
        if (
            self._estado != "mundo"
            or not self._jogador_perto_da_porta4()
            or acao != "chave"
            or self.inventario.get(NOME_CHAVE_PRATA, 0) < 1
        ):
            return
        self._remover_opcoes_porta4()
        self._abrir_porta(4)

    def _desenhar_opcoes_porta3(self):
        if not self._jogador_perto_da_porta3():
            return

        self.canvas.delete("porta3_popup")
        self._porta3_popup_visivel = True
        escala_x = self.canvas.winfo_width() / LARGURA_MUNDO
        escala_y = self.canvas.winfo_height() / ALTURA_MUNDO
        centro_x = 590 * escala_x
        topo = max(12, (210 - 145) * escala_y)
        meia_largura = 185 * escala_x
        altura = 134 * escala_y
        self.canvas.create_rectangle(
            centro_x - meia_largura,
            topo,
            centro_x + meia_largura,
            topo + altura,
            fill=FUNDO,
            outline=DESTAQUE,
            width=2,
            tags=("porta3_popup",),
        )
        self.canvas.create_text(
            centro_x,
            topo + 18 * escala_y,
            text="PORTA 3 — REFORÇADA E TRANCADA",
            fill=TEXTO,
            font=("Consolas", 12, "bold"),
            tags=("porta3_popup",),
        )

        tem_chave = self.inventario.get("Chave Dourada", 0) > 0
        opcoes = (
            (
                "chave",
                "Usar chave dourada" if tem_chave else "Usar chave dourada — não possui",
                DESTAQUE if tem_chave else SUAVE,
                tem_chave,
            ),
            (
                "arrombar",
                "Teste D20 para arrombar (18+; 1 chance)"
                if not self.porta3_tentativa_usada
                else "Teste D20 — chance usada",
                "#FFE08A" if not self.porta3_tentativa_usada else SUAVE,
                not self.porta3_tentativa_usada,
            ),
            ("desistir", "Desistir", TEXTO, True),
        )
        for indice, (acao, texto, cor, habilitada) in enumerate(opcoes):
            tag = f"porta3_{acao}"
            self.canvas.create_text(
                centro_x,
                topo + (48 + indice * 27) * escala_y,
                text=texto,
                fill=cor,
                font=("Consolas", 11, "bold"),
                tags=("porta3_popup", tag),
            )
            if habilitada:
                self.canvas.tag_bind(
                    tag,
                    "<Button-1>",
                    lambda _event, escolha=acao: self._acao_porta3(escolha),
                )
                self.canvas.tag_bind(
                    tag,
                    "<Enter>",
                    lambda _event: self.canvas.configure(cursor="hand2"),
                )
                self.canvas.tag_bind(
                    tag,
                    "<Leave>",
                    lambda _event: self.canvas.configure(cursor=""),
                )
        self.canvas.tag_raise("porta3_popup")

    def _remover_opcoes_porta3(self):
        self.canvas.delete("porta3_popup")
        self.canvas.configure(cursor="")
        self._porta3_popup_visivel = False

    def _acao_porta3(self, acao):
        if (
            self._estado != "mundo"
            or not self._jogador_perto_da_porta3()
            or self.porta3_aberta
        ):
            return
        if acao == "desistir":
            self._remover_opcoes_porta3()
            self.canvas.focus_set()
        elif acao == "chave":
            if self.inventario.get("Chave Dourada", 0) > 0:
                self._consumir_item("Chave Dourada")
                self._remover_opcoes_porta3()
                self._abrir_porta(3)
        elif acao == "arrombar":
            self._iniciar_teste_porta3()

    @staticmethod
    def _dano_por_falha_teste(dificuldade):
        if dificuldade >= 18:
            return 3
        if dificuldade > 15:
            return 2
        if dificuldade >= 10:
            return 1
        return 0

    def _iniciar_teste_interacao(
        self,
        dificuldade,
        descricao,
        ao_resolver,
        dano_falha=None,
    ):
        if (
            self._estado != "mundo"
            or self.animador_d20.rolando
            or self.animador_d20_grande.rolando
        ):
            return

        self._estado = "teste_interacao"
        self.teclas_pressionadas.clear()
        self.audio_passos.parar()
        self._posicionar_dado_hud()
        self.canvas.itemconfigure(
            self.d20_rolagem_titulo,
            text=f"TESTE D20: {descricao} ({dificuldade}+)",
        )
        for item in (
            self.d20_rolagem_imagem,
            self.d20_rolagem_texto,
            self.d20_rolagem_titulo,
        ):
            self.canvas.itemconfigure(item, state="normal")
        self.canvas.tag_raise("hud_dado_rolagem")
        try:
            self.animador_d20_grande.rolar_teste(
                lambda resultado: self._resultado_teste_interacao(
                    resultado,
                    dificuldade,
                    descricao,
                    ao_resolver,
                    dano_falha,
                )
            )
        except (RuntimeError, ValueError, tk.TclError) as erro:
            self._ocultar_dado_rolagem()
            self._estado = "mundo"
            messagebox.showerror(
                "Erro no teste",
                f"Não foi possível concluir o teste de D20:\n{erro}",
                parent=self.container.winfo_toplevel(),
            )
            self.canvas.focus_set()

    def _resultado_teste_interacao(
        self,
        resultado,
        dificuldade,
        descricao,
        ao_resolver,
        dano_falha,
    ):
        if self._estado != "teste_interacao":
            return
        self.animador_d20.mostrar(resultado)
        self.dialogo_var.set(
            f"{descricao}: D20 {resultado}; precisa de {dificuldade}+."
        )
        self.container.after(
            3000,
            lambda: self._finalizar_teste_interacao(
                resultado,
                dificuldade,
                descricao,
                ao_resolver,
                dano_falha,
            ),
        )

    def _ocultar_dado_rolagem(self):
        for item in (
            self.d20_rolagem_imagem,
            self.d20_rolagem_texto,
            self.d20_rolagem_titulo,
        ):
            self.canvas.itemconfigure(item, state="hidden")

    def _finalizar_teste_interacao(
        self,
        resultado,
        dificuldade,
        descricao,
        ao_resolver,
        dano_falha,
    ):
        if self._estado != "teste_interacao":
            return
        self._ocultar_dado_rolagem()
        sucesso = resultado >= dificuldade
        if not sucesso:
            dano = (
                self._dano_por_falha_teste(dificuldade)
                if dano_falha is None
                else dano_falha
            )
            if dano:
                self.jogador.hp = max(0, self.jogador.hp - dano)
                self._atualizar_hud()
                self.dialogo_var.set(
                    f"Falha no teste de {descricao.lower()}: perdeu {dano} HP."
                )

        self._estado = "mundo"
        ao_resolver(sucesso, resultado)
        if self._estado == "mundo":
            self.canvas.focus_set()
        elif getattr(self, "tela_porta", None) is not None:
            self.tela_porta.focus_set()

    def _iniciar_teste_porta3(self):
        if (
            self.porta3_tentativa_usada
            or not self._jogador_perto_da_porta3()
        ):
            return

        self.porta3_tentativa_usada = True
        self._remover_opcoes_porta3()
        self._iniciar_teste_interacao(
            18,
            "ARROMBAR PORTA REFORÇADA",
            self._resultado_arrombamento_porta3,
        )

    def _resultado_arrombamento_porta3(self, sucesso, _resultado):
        if sucesso:
            self.porta3_aberta = True
            self._abrir_porta(3)
            return
        self.dialogo_var.set(
            "Falha: a porta resistiu. Você ainda pode usar a Chave Dourada."
        )
        if self._jogador_perto_da_porta3():
            self._desenhar_opcoes_porta3()

    def _abrir_porta(self, numero):
        if numero == 3:
            self.porta3_aberta = True
            texto = (
                "A porta reforçada dava para o exterior. Ao atravessá-la, "
                "uma horda de anomalias cercou você antes que pudesse voltar."
            )
            self._remover_opcoes_porta3()
            self._mostrar_tela_morte(texto, "VOCÊ MORREU")
            return
        else:
            if numero == 4 and self.inventario.get(NOME_CHAVE_PRATA, 0) < 1:
                self.dialogo_var.set(
                    "A porta 4 está trancada. Você precisa da Chave de Prata."
                )
                return
            texto = "Você entrou na Sala 4" if numero == 4 else f"Você entrou na porta {numero}"
            self._estado = "porta"
        self.teclas_pressionadas.clear()
        self.audio_passos.parar()
        self._remover_opcoes_porta3()
        self._remover_opcoes_porta4()

        self.tela_porta = tk.Frame(self.container, bg="black", takefocus=True)
        self.tela_porta.place(relx=0, rely=0, relwidth=1, relheight=1)
        tk.Label(
            self.tela_porta,
            text=f"{texto}\n\nPressione ESC para voltar ao corredor",
            fg="white",
            bg="black",
            font=("Consolas", 24, "bold"),
            justify="center",
        ).pack(expand=True)
        self.tela_porta.bind("<KeyPress-Escape>", self._fechar_porta)
        self.tela_porta.lift()
        self.tela_porta.focus_set()

    def _mostrar_tela_morte(self, texto, titulo):
        self._estado = "morte"
        self.teclas_pressionadas.clear()
        self.audio_passos.parar()
        self._parar_animacao_anomalia_sala2()
        if getattr(self, "_janela_combate", None) is not None:
            self._janela_combate.destroy()
            self._janela_combate = None

        self.tela_porta = tk.Frame(self.container, bg="black", takefocus=True)
        self.tela_porta.place(relx=0, rely=0, relwidth=1, relheight=1)
        tk.Label(
            self.tela_porta,
            text=titulo,
            fg="#FF5C69",
            bg="black",
            font=("Consolas", 34, "bold"),
        ).pack(pady=(150, 24))
        self._morte_texto = texto
        self._morte_indice = 0
        self._morte_texto_label = tk.Label(
            self.tela_porta,
            text="",
            fg="white",
            bg="black",
            font=("Consolas", 17),
            justify="center",
            wraplength=800,
        )
        self._morte_texto_label.pack(padx=40, pady=12)
        tk.Button(
            self.tela_porta,
            text="VOLTAR AO MENU",
            command=self._voltar_ao_menu_apos_morte,
            fg="#090D16",
            bg=DESTAQUE,
            font=("Consolas", 13, "bold"),
            padx=20,
            pady=8,
        ).pack(pady=32)
        self.tela_porta.bind(
            "<KeyPress-Escape>",
            self._voltar_ao_menu_apos_morte,
        )
        self.tela_porta.lift()
        self.tela_porta.focus_set()
        self._morte_after_id = self.tela_porta.after(
            28,
            self._animar_texto_morte,
        )

    def _animar_texto_morte(self):
        if self._estado != "morte" or self.tela_porta is None:
            self._morte_after_id = None
            return
        self._morte_indice += 1
        self._morte_texto_label.configure(
            text=self._morte_texto[: self._morte_indice]
        )
        if self._morte_indice < len(self._morte_texto):
            self._morte_after_id = self.tela_porta.after(
                28,
                self._animar_texto_morte,
            )
        else:
            self._morte_after_id = None

    def _cancelar_animacao_morte(self):
        identificador = getattr(self, "_morte_after_id", None)
        if identificador is not None and getattr(self, "tela_porta", None) is not None:
            self.tela_porta.after_cancel(identificador)
            self._morte_after_id = None

    def _voltar_ao_menu_apos_morte(self, event=None):
        self._cancelar_animacao_morte()
        self._parar_animacao_anomalia_sala2()
        self._estado = "menu"
        self.ao_menu()
        return "break"

    def _fechar_porta(self, event=None):
        self.tela_porta.destroy()
        self.tela_porta = None
        self._estado = "mundo"
        self.teclas_pressionadas.clear()
        self.canvas.focus_set()
        return "break"

    def _carregar_sala(self, sala, spawn):
        if self._objeto_interativo_sala1 == "armarios":
            self._remover_opcoes_armarios_sala1()
        if self._objeto_interativo_sala1 == "cofre":
            self._remover_opcoes_cofre_sala1()
        if getattr(self, "_estante_sala2_interativa", None) is not None:
            self._remover_opcoes_estantes_sala2()
        if getattr(self, "_glitch_popup_visivel", False):
            self._remover_opcoes_glitch_sala2()
        if getattr(self, "_capsula_popup_visivel", False):
            self._remover_opcoes_capsula_esquerda()
        if self.sala_atual == "sala_2" and sala != "sala_2":
            self._parar_animacao_anomalia_sala2()
        self._estado = "mundo"
        self.sala_atual = sala
        self.player_x, self.player_y = spawn
        self._porta_ocupada = None
        self.audio_passos.parar()
        self.direcao = "baixo"
        self._quadro_animacao = 0
        self._tempo_animacao = 0
        self.teclas_pressionadas.clear()
        self.dialogo_var.set("")
        self._atualizar_nome_sala()
        self._ultimo_tamanho = None
        self._redimensionar_cena()
        self._iniciar_animacao_anomalia_sala2()
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
