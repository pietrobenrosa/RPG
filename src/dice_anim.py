import random
from pathlib import Path

import tkinter as tk

from combate import rolar_d20


class AnimadorD20:
    def __init__(self, label, pasta_dados=None):
        self.label = label
        self.pasta_dados = pasta_dados or (
            Path(__file__).resolve().parents[1] / "assets" / "dados d20"
        )
        self.imagens = {
            valor: tk.PhotoImage(
                file=str(self.pasta_dados / f"d20 - d{valor}.png")
            ).zoom(2, 2)
            for valor in range(1, 21)
        }
        self.rolando = False
        self._valor_atual = 0
        self._agendamento = None
        self._mostrar(1)

    def _mostrar(self, valor):
        self._valor_atual = valor
        self.label.configure(image=self.imagens[valor], text=f"D20: {valor}")

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
            self._agendamento = self.label.after(
                atraso,
                lambda: animar_quadro(indice + 1),
            )

        animar_quadro()
        return resultado
