import customtkinter as ctk

from combate import atacar, rolar_d20, testar_fuga
from models import Entidade


FUNDO = "#090D16"
PAINEL = "#111A27"
DESTAQUE = "#42E8C4"
TEXTO = "#E8F0F5"
SUAVE = "#91A4B5"

CLASSES = {
    "Engenheiro": {"hp": 34, "ataque": 6, "defesa": 8, "nivel": 1,
                   "descricao": "Resistente; bônus nos testes de conserto e overclock."},
    "Segurança": {"hp": 42, "ataque": 9, "defesa": 5, "nivel": 1,
                  "descricao": "Mais vida e força para enfrentar as Anomalias."},
    "Cientista": {"hp": 27, "ataque": 7, "defesa": 4, "nivel": 2,
                  "descricao": "Começa no nível 2 com suprimentos extras."},
}

PASSOS = [
    ("Ala médica", "As cápsulas foram abertas à força. Um terminal ainda pisca perto dos leitos.", None),
    ("Corredor de manutenção", "Cabos expostos iluminam um rastro escuro. Algo se move dentro das paredes.", "Parasita Sombrio"),
    ("Depósito de combustível", "Entre caixas tombadas, você encontra uma Célula de Combustível intacta.", None),
    ("Laboratório", "O Mutante Rastejante protege o módulo de ignição. O alarme dispara quando você entra.", "Mutante Rastejante"),
    ("Centro de navegação", "Você recupera a Placa de Navegação e baixa a gravação final da equipe.", None),
    ("Hangar subterrâneo", "A Aberração do Hangar bloqueia o mini-foguete. As três peças estão prontas para instalação.", "Aberração do Hangar"),
    ("Órbita terrestre", "O foguete acopla à estação. A nave de evacuação está destruída; a I.A. anuncia contenção biológica.", "Drone de Patrulha"),
    ("Setor de segurança", "Torretas acordam no corredor. Atrás delas fica o acesso ao Núcleo Central.", "Torreta Laser"),
    ("Núcleo Central", "A I.A. fecha as portas. Não existe negociação: o Núcleo precisa ser desligado.", "Núcleo da I.A."),
]

INIMIGOS = {
    "Parasita Sombrio": (20, 6, 2, 1),
    "Mutante Rastejante": (25, 7, 3, 1),
    "Aberração do Hangar": (38, 9, 5, 2),
    "Drone de Patrulha": (25, 7, 3, 2),
    "Torreta Laser": (31, 8, 4, 2),
    "Núcleo da I.A.": (55, 10, 6, 3),
}


class Jogo:
    def __init__(self, container, ao_menu):
        self.container = container
        self.ao_menu = ao_menu
        self.indice = 0
        self.inimigo = None
        self.em_animacao = False
        self.pecas = set()
        self.inventario = {"Kit Médico": 1, "Injeção de Adrenalina": 1, "Pulso Eletromagnético": 1}
        self.ataque_extra = 0
        self.log = "Escolha sua especialização para iniciar a miss��o."
        self._classe()

    def _limpar(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        self.container.configure(fg_color=FUNDO)

    def _painel(self, titulo, texto):
        self._limpar()
        card = ctk.CTkFrame(self.container, fg_color=PAINEL, corner_radius=18)
        card.pack(fill="both", expand=True, padx=36, pady=30)
        ctk.CTkLabel(card, text=titulo, font=("Consolas", 30, "bold"), text_color=DESTAQUE).pack(anchor="w", padx=28, pady=(24, 8))
        ctk.CTkLabel(card, text=texto, font=("Consolas", 15), text_color=TEXTO, justify="left", wraplength=950).pack(anchor="w", padx=28, pady=(0, 16))
        self.corpo = ctk.CTkFrame(card, fg_color="transparent")
        self.corpo.pack(fill="both", expand=True, padx=24, pady=12)
        self.card = card

    def _botao(self, texto, comando, parent=None, **kwargs):
        ctk.CTkButton(parent or self.corpo, text=texto, command=comando, fg_color="#203447", hover_color="#2A5360", text_color=TEXTO, height=42, **kwargs).pack(fill="x", pady=5)

    def _classe(self):
        self._painel("EXILE | ESCOLHA SUA CLASSE", "O bunker está em ruínas. A estação orbital parte em 24 horas. Quem você era antes de acordar?")
        for nome, dados in CLASSES.items():
            self._botao(f"{nome}  —  HP {dados['hp']} | ATQ {dados['ataque']} | DEF {dados['defesa']} | Nível {dados['nivel']}\n{dados['descricao']}", lambda n=nome: self._iniciar(n), height=64)

    def _iniciar(self, nome):
        dados = CLASSES[nome]
        if nome == "Cientista":
            self.inventario["Kit Médico"] += 1
            self.inventario["Pulso Eletromagnético"] += 1
        self.heroi = Entidade(nome, dados["hp"], dados["ataque"], dados["defesa"], dados["nivel"])
        self._historia("PRÓLOGO — O DESPERTAR", "A cápsula de hibernação abre com um estalo. Luzes vermelhas piscam no bunker vazio. No terminal, uma gravação explica: as Anomalias tomaram a superfície e a nave de evacuação partirá da estação orbital em 24 horas. Você precisa alcançar o hangar e consertar o mini-foguete.", "Começar exploração", self._explorar)

    def _historia(self, titulo, texto, rotulo, comando):
        self._painel(titulo, texto)
        self._botao(rotulo, comando)

    def _explorar(self):
        if self.indice >= len(PASSOS):
            self._final()
            return
        titulo, texto, inimigo = PASSOS[self.indice]
        self._painel(f"ATO {'1' if self.indice < 6 else '2'} — {titulo.upper()}", texto)
        self._status(self.corpo)
        if inimigo:
            hp, ataque, defesa, nivel = INIMIGOS[inimigo]
            self.inimigo = Entidade(inimigo, hp, ataque, defesa, nivel)
            self._botao("Enfrentar ameaça", self._combate)
        else:
            if self.indice == 0:
                self._botao("Hackear terminal (D20; Engenheiro ganha +2)", self._hackear)
            elif self.indice == 2:
                self.pecas.add("Célula de Combustível")
                self._botao("Guardar Célula de Combustível", self._avancar)
            elif self.indice == 4:
                self.pecas.add("Módulo de Ignição")
                self.pecas.add("Placa de Navegação")
                self._botao("Guardar módulo e placa de navegação", self._avancar)
            else:
                self._botao("Continuar", self._avancar)
            self._botao("Procurar suprimentos", self._buscar)

    def _status(self, parent):
        pecas = ", ".join(sorted(self.pecas)) or "nenhuma"
        itens = " | ".join(f"{k}: {v}" for k, v in self.inventario.items() if v)
        ctk.CTkLabel(parent, text=f"{self.heroi.nome}  HP {self.heroi.hp}/{CLASSES[self.heroi.nome]['hp']}  |  Nível {self.heroi.nivel}  |  Peças: {pecas}\nInventário: {itens or 'vazio'}", text_color=SUAVE, justify="left", wraplength=900).pack(anchor="w", pady=8)

    def _avancar(self):
        if self.indice == 5:
            faltam = {"Célula de Combustível", "Módulo de Ignição", "Placa de Navegação"} - self.pecas
            if faltam:
                self.log = "Ainda faltam componentes: " + ", ".join(sorted(faltam))
                self._explorar()
                return
        self.indice += 1
        if self.indice == 6:
            self._historia("LANÇAMENTO", "Com as peças instaladas, o mini-foguete rompe a atmosfera. A Terra desaparece sob nuvens de poeira.", "Acoplar à estação", self._explorar)
        else:
            self._explorar()

    def _buscar(self):
        self.inventario["Kit Médico"] = self.inventario.get("Kit Médico", 0) + 1
        self.log = "Você encontrou um Kit Médico."
        self._explorar()

    def _hackear(self):
        valor = rolar_d20()
        bonus = 2 if self.heroi.nome == "Engenheiro" else 0
        texto = f"Terminal: D20 {valor}" + (f" + bônus de classe {bonus}" if bonus else "")
        if valor + bonus >= 11:
            self.inventario["Pulso Eletromagnético"] += 1
            texto += ". Acesso concedido; você recupera um Pulso Eletromagnético."
        else:
            texto += ". A tentativa falha, mas o sistema não dispara o alarme."
        self._historia("TESTE DE HACK", texto, "Seguir", self._avancar)

    def _combate(self):
        self._painel(f"COMBATE — {self.inimigo.nome.upper()}", "Você age primeiro. Itens podem ser usados sem consumir sua ação; escolha atacar ou tentar fugir.")
        self._status(self.corpo)
        ctk.CTkLabel(self.corpo, text=f"{self.inimigo.nome}: HP {self.inimigo.hp}/{INIMIGOS[self.inimigo.nome][0]}", text_color="#F29E8E").pack(anchor="w", pady=6)
        self.dado_label = ctk.CTkLabel(self.corpo, text="D20: —", font=("Consolas", 24, "bold"), text_color=DESTAQUE)
        self.dado_label.pack(pady=8)
        if self.log:
            ctk.CTkLabel(self.corpo, text=self.log, text_color=SUAVE, wraplength=900).pack(anchor="w", pady=4)
        self._botao("Atacar", self._atacar)
        self._botao("Usar item", self._menu_itens)
        if self.inimigo.nome != "Núcleo da I.A.":
            self._botao("Fugir (sucesso com 11+)", self._fugir)

    def _animar_dado(self, ao_terminar):
        self.em_animacao = True
        valores = [rolar_d20() for _ in range(10)]
        def passo(i=0):
            if i < len(valores):
                self.dado_label.configure(text=f"D20: {valores[i]}")
                self.container.after(65, lambda: passo(i + 1))
            else:
                self.em_animacao = False
                ao_terminar(valores[-1])
        passo()

    def _atacar(self):
        if self.em_animacao:
            return
        def resolver(dado):
            self.heroi.ataque += self.ataque_extra
            resultado = atacar(self.heroi, self.inimigo, dado)
            self.heroi.ataque -= self.ataque_extra
            self.log = self._texto_ataque(resultado, "Você", self.inimigo.nome)
            if not self.inimigo.viva:
                self.log += f"\n{self.inimigo.nome} foi derrotado!"
                if self.inimigo.nome == "Núcleo da I.A.":
                    self._final()
                    return
                self._combate_vitoria()
                return
            self._turno_inimigo()
        self._animar_dado(resolver)

    def _texto_ataque(self, resultado, atacante, defensor):
        if resultado.falha_critica:
            return f"{atacante} tirou 1: falha crítica! O ataque erra."
        detalhe = " Acerto crítico! Dano dobrado." if resultado.critico else ""
        return f"{atacante} tirou {resultado.dado} e causou {resultado.dano} de dano a {defensor}.{detalhe}"

    def _turno_inimigo(self):
        resultado = atacar(self.inimigo, self.heroi)
        self.log += "\n" + self._texto_ataque(resultado, self.inimigo.nome, "você")
        if not self.heroi.viva:
            self._fim("FIM DE JOGO", "Seus sinais vitais cessam no silêncio. A estação continua à deriva.")
        else:
            self._combate()

    def _combate_vitoria(self):
        nome = self.inimigo.nome
        if nome == "Aberração do Hangar":
            self._historia("HANGAR CONQUISTADO", "A criatura cai. Você instala as três peças no mini-foguete e inicia a sequência de lançamento.", "Lançar", self._avancar)
        elif nome == "Núcleo da I.A.":
            self._final()
        else:
            self.indice += 1
            self._historia("AMEAÇA ELIMINADA", self.log + "\nO caminho está livre.", "Continuar", self._explorar)

    def _fugir(self):
        if self.em_animacao:
            return
        def resolver(dado):
            self.dado_label.configure(text=f"Fuga — D20: {dado}")
            if dado >= 11:
                self.log = f"Você tirou {dado} e escapou. A ameaça fica para trás."
                if self.inimigo.nome == "Aberração do Hangar":
                    self._historia("FUGA DO HANGAR", self.log + " Você não conseguiu lançar o foguete sem derrotar o guardião; tente novamente.", "Voltar ao combate", self._combate)
                else:
                    self.indice += 1
                    self._historia("FUGA", self.log, "Seguir", self._explorar)
            else:
                self.log = f"Você tirou {dado}; a fuga falha!"
                self._turno_inimigo()
        self._animar_dado(resolver)

    def _menu_itens(self):
        self._painel("INVENTÁRIO", "Itens são usados sem gastar a ação do turno. Escolha um item disponível.")
        for nome, quantidade in self.inventario.items():
            if quantidade:
                self._botao(f"{nome} × {quantidade}", lambda n=nome: self._usar_item(n))
        self._botao("Voltar ao combate", self._combate)

    def _usar_item(self, nome):
        if nome == "Kit Médico":
            self.inventario[nome] -= 1
            cura = min(18, CLASSES[self.heroi.nome]["hp"] - self.heroi.hp)
            self.heroi.hp += cura
            self.log = f"Kit Médico usado: +{cura} HP."
        elif nome == "Injeção de Adrenalina":
            self.inventario[nome] -= 1
            self.ataque_extra = 3
            self.log = "Adrenalina ativa: +3 de ataque até o fim do próximo combate."
        else:
            self.inventario[nome] -= 1
            dano = 18 if "Drone" in self.inimigo.nome or "Torreta" in self.inimigo.nome or "I.A." in self.inimigo.nome else 9
            self.inimigo.hp = max(0, self.inimigo.hp - dano)
            self.log = f"Pulso EMP causa {dano} de dano."
            if not self.inimigo.viva:
                self._combate_vitoria()
                return
        self._combate()

    def _final(self):
        self._painel("EPÍLOGO — UMA ÚLTIMA ESCOLHA", "O Núcleo da I.A. foi derrotado. Uma nave reserva aguarda no hangar. Escolha como garantir que a inteligência corrompida não volte.")
        self._botao("Final 1 — Overclock do Sistema", lambda: self._fim("FINAL: OVERCLOCK", "Você sobrecarrega os circuitos sem danificar a estação. Com os sistemas de navegação sob seu controle, parte em segurança rumo a um novo planeta."))
        self._botao("Final 2 — Detonação do Reator", lambda: self._fim("FINAL: DETONAÇÃO", "O reator entra em reação em cadeia. Você escapa na cápsula no último segundo, enquanto a estação desaparece numa explosão silenciosa."))

    def _fim(self, titulo, texto):
        self._painel(titulo, texto)
        self._botao("Jogar novamente", self._classe)
        self._botao("Voltar ao menu", self.ao_menu)
