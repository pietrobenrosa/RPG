# 🌌 O Despertar do Éter (Cyber-Arcane RPG)

Um RPG de turnos desenvolvido em **Python** que transporta a experiência clássica dos jogos de mesa (sistema D20) para uma interface visual interativa, combinando elementos de **Cyberpunk/Sci-Fi** com **Magia Tecnomântica**.

Projeto desenvolvido como trabalho acadêmico para o curso.

---

## 📖 Sinopse

Após décadas em estado de criogenia, você desperta abruptamente dentro de um bunker subterrâneo em ruínas. O silêncio dos corredores é quebrado apenas por alarmes de contenção e criaturas anômalas que emergiram após uma catástrofe mágico-tecnológica.

Por meio de registros gravados nos terminais locais, você descobre o plano original de evacuação: alcançar uma estação espacial em órbita, onde a última arca estelar aguardaria para levar os sobreviventes a um novo planeta. No entanto, ao alcançar a órbita, o cenário é desolador — a Inteligência Artificial central da estação corrompeu-se, absorveu os sistemas arcanos e destruiu a nave principal de evacuação.

Agora, cabe a você sabotar o núcleo da estação, enfrentar a IA corrompida e roubar uma nave auxiliar antes que seja tarde demais.

---

## ✨ Funcionalidades Principais

* **Sistema de Combate D20 Animado:** Rolagem de dados em 2D na tela com animação de desaceleração, cálculo automático de modificadores de atributo, acertos críticos e falhas críticas.
* **Três Classes Jogáveis:** Estilos de jogo distintos com atributos, habilidades exclusivas e formas próprias de gerenciar energia/mana.
* **Gerenciamento de Recursos:** Sistema de turnos estratégico com menu de habilidades, uso de poções/estimulantes no inventário e controle de pontos de vida (HP) e energia arcana (MP).
* **Save e Continuação:** Salve o progresso durante a partida e continue do mesmo personagem, sala, posição e inventário pelo menu.
* **Narrativa Ramificada:** História dividida em três atos principais (*O Bunker*, *A Estação Orbital* e *O Núcleo*), permitindo desbloquear **múltiplos finais** dependendo das escolhas feitas durante a jornada.

---

## 🎭 Classes Disponíveis

| Classe | Estilo de Combate | Foco Principal |
| :--- | :--- | :--- |
| **Sombra da Rede** | Furtivo & Ágil | Esquiva elevada, ataques críticos com lâminas energéticas e ilusões holográficas para confundir inimigos. |
| **Hacker Elemental** | Conjurador Tech | Manipula códigos como feitiços para invocar descargas elétricas, sobrecargas térmicas e barreiras digitais. |
| **Ciber-Paladino** | Tanque & Corpo-a-Corpo | Armadura pesada reforçada por implantes arcanos, alta resistência física e ataques devastadores com lança energética. |

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.10+
* **Interface Gráfica & Animações:** `Tkinter`/`CustomTkinter`, com `Pillow` para exibir os cenários e sprites.
* **Lógica de Sistema:** Programação Orientada a Objetos (POO) para gerenciamento de entidades e testes de D20.

---

## 📂 Estrutura Sugerida do Projeto

```text
o-despertar-do-eter/
├── assets/
│   ├── cenarios/         # Sala de hibernação e corredor
│   ├── dados d20/        # Faces do dado (1 a 20)
│   └── personagem/      # Sprites parados e de caminhada
├── src/                  # Código-fonte do jogo
│   ├── combate.py        # Regras do sistema D20
│   ├── dice_anim.py      # Rolagem e animação visual do dado
│   ├── jogo.py           # Salas, movimento, colisões e HUD
│   ├── savegame.py       # Salvar e carregar progresso em JSON
│   └── main.py           # Ponto de entrada da aplicação
└── README.md             # Documentação do projeto
```

---

## 🕹️ Salas, movimento e D20

* Use **WASD** ou as **setas** para andar. O personagem anima na direção do movimento.
* Atravesse a porta da sala de hibernação para entrar no corredor. As portas 1, 2 e 4 mostram uma tela de identificação.
* No começo, o personagem aparece em frente à segunda câmara criogênica, da esquerda para a direita (a que tem a maca aberta).
* No corredor, avance para cima para explorar até a parede do fundo; volte para baixo até a entrada para retornar à sala de hibernação.
* O personagem se move 30% mais rápido que antes.
* A porta 3 é reforçada: pegue a **Chave Dourada** no chão da sala de hibernação para abri-la ou tente arrombá-la com um resultado **18+** no D20. O teste só pode ser feito uma vez; as opções aparecem perto da porta e somem ao se afastar. Use **ESC** na tela da sala 3 para voltar ao corredor.
* Pressione **E** (ou clique em **MOCHILA [E]**) para abrir o inventário. Use as setas para selecionar, **Enter** para usar, **Delete** para jogar no chão e **ESC** para fechar. Itens no chão podem ser clicados para recolher.
* A vida é mostrada no alto à esquerda; XP e nível ficam no alto à direita.
* Na barra superior, **SALVAR** grava o progresso em `dados/savegame.json`, **MENU** salva e volta ao menu e **SAIR** pergunta se deseja salvar antes de fechar. Se houver save, o menu mostra **CONTINUAR JOGO**.
* O som de passos começa no segundo 2 do arquivo `assets/audios/passos.mp3` e recomeça desse ponto a cada repetição; toca enquanto o personagem anda e para quando ele para.
* As faces do dado já têm transparência nos PNGs.
* Pressione **R** para testar a rolagem D20. O dado fica parado até a tecla ser pressionada, anima e para no resultado no canto inferior direito. O teste de arrombamento mostra o dado ampliado no centro da tela.
* Os sprites são ampliados sem interpolação: o personagem usa o dobro do tamanho no corredor e o dado fica 2× maior, preservando as bordas do pixel art.
* As salas usam coordenadas virtuais de **960 × 540**, com a origem `(0, 0)` no canto superior esquerdo.

### Ajustar colisões

No início de [`src/jogo.py`](src/jogo.py), edite `COLISOES`. Cada bloco é uma tupla `(x, y, largura, altura)`:

```python
"sala_hibernacao": [
    (38, 215, 100, 165),  # bloco de colisão de exemplo
],
```

Mude os quatro números para mover ou redimensionar o bloco; acrescente outra tupla para bloquear uma nova área. As coordenadas são relativas à imagem da sala, não ao tamanho atual da janela.

### Ajustar a passagem entre salas

No mesmo arquivo, edite `ZONAS_TELEPORTE`. Cada `retangulo` define a área que o personagem precisa atravessar; `destino` escolhe a próxima sala e `spawn` define onde ele aparece nela:

```python
{
    "retangulo": (620, 185, 155, 60),
    "destino": "corredor",
    "spawn": (480, 470),
},
```

Para mudar a porta, ajuste `(x, y, largura, altura)` em `retangulo`. Para criar uma nova saída, adicione outro bloco à lista da sala e informe a sala de destino e a posição de chegada.

---

## 🚀 Como Executar o Projeto

### Pré-requisitos
Certifique-se de ter o **Python 3** instalado em sua máquina.

### Passo a passo

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/seu-usuario/o-despertar-do-eter.git
   cd o-despertar-do-eter
   ```

2. **Crie e ative um ambiente virtual (opcional, mas recomendado):**
   ```bash
   python -m venv venv
   # No Windows:
   venv\Scripts\activate
   # No Linux/Mac:
   source venv/bin/activate
   ```

3. **Instale as dependências:**
   ```bash
   pip install customtkinter pillow pygame
   ```

4. **Inicie o jogo:**
   ```bash
   python src/main.py
   ```

---

## 👥 Autores

* **Você** — *Desenvolvimento, Arquitetura e Mecânicas de Combate*
* **Nicoly** — *Design Narrativo, Balanceamento de Classes e Interface*

---

## 📝 Licença

Este projeto foi desenvolvido exclusivamente para fins educacionais.