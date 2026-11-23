from pathlib import Path
import warnings

import pygame


class AudioPassos:
    def __init__(self, arquivo, inicio=2.0):
        self.arquivo = Path(arquivo)
        self.inicio = inicio
        self._tocando = False
        self._indisponivel = False

    def atualizar(self, andando):
        if not andando:
            self.parar()
            return
        if self._tocando or self._indisponivel:
            return

        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init()
            pygame.mixer.music.load(str(self.arquivo))
            pygame.mixer.music.play(loops=-1, start=self.inicio)
        except pygame.error as erro:
            self._indisponivel = True
            warnings.warn(
                f"Não foi possível tocar o áudio de passos '{self.arquivo}': {erro}",
                RuntimeWarning,
                stacklevel=2,
            )
            return

        self._tocando = True

    def parar(self):
        if self._tocando:
            pygame.mixer.music.stop()
            self._tocando = False
