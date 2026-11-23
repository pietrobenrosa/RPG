import random
from pathlib import Path

import tkinter as tk

from combate import rolar_d20


class AnimadorD20:
    def __init__(
        self,
        canvas,
        item_imagem,
        item_texto,
        pasta_dados=None,
        ampliacao=2,
    ):
        self.canvas = canvas
        self.item_imagem = item_imagem
        self.item_texto = item_texto
        self.pasta_dados = pasta_dados or (
            Path(__file__).resolve().parents[1] / "assets" / "dados d20"
        )
        self.imagens = {
            valor: tk.PhotoImage(
                file=str(self.pasta_dados / f"d20 - d{valor}.png")
            ).zoom(ampliacao, ampliacao)
            for valor in range(1, 21)
        }
        self.rolando = False
        self._valor_atual = 0
        self._agendamento = None
        self._mostrar(1)

    def _mostrar(self, valor):
        self._valor_atual = valor
        self.canvas.itemconfigure(self.item_imagem, image=self.imagens[valor])
        self.canvas.itemconfigure(self.item_texto, text=f"D20: {valor}")

    def mostrar(self, valor):
        if not 1 <= valor <= 20:
            raise ValueError("O resultado do D20 precisa estar entre 1 e 20.")
        self._mostrar(valor)

    def rolar_teste(self, ao_terminar, resultado=None):
        if self.rolando:
            raise RuntimeError("Já existe uma rolagem de D20 em andamento.")
        if resultado is None:
            resultado = rolar_d20()
        if not 1 <= resultado <= 20:
            raise ValueError("O resultado do D20 precisa estar entre 1 e 20.")

        self.rolando = True
        quadros = [random.randint(1, 20) for _ in range(17)]
        quadros.append(resultado)

        def animar_quadro(indice=0):
            self._mostrar(quadros[indice])
            if indice == len(quadros) - 1:
                self.rolando = False
                self._agendamento = None
                ao_terminar(resultado)
                return

            progresso = indice / (len(quadros) - 1)
            atraso = int(35 + 150 * progresso ** 2)
            self._agendamento = self.canvas.after(
                atraso,
                lambda: animar_quadro(indice + 1),
            )

        animar_quadro()
        return resultado
