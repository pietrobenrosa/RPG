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
        if self._indisponivel:
            return
        if self._tocando:
            try:
                ocupado = pygame.mixer.music.get_busy()
            except pygame.error as erro:
                self._desativar("consultar o estado", erro)
                return
            if not ocupado:
                self._tocar()
            return

        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init()
            pygame.mixer.music.load(str(self.arquivo))
        except pygame.error as erro:
            self._desativar("carregar", erro)
            return

        self._tocando = True
        self._tocar()

    def _tocar(self):
        try:
            pygame.mixer.music.play(loops=0, start=self.inicio)
        except pygame.error as erro:
            self._desativar("iniciar", erro)

    def parar(self):
        if self._tocando:
            try:
                pygame.mixer.music.stop()
            except pygame.error as erro:
                self._desativar("parar", erro)
            finally:
                self._tocando = False

    def _desativar(self, operacao, erro):
        self._tocando = False
        self._indisponivel = True
        warnings.warn(
            f"Não foi possível {operacao} o áudio de passos "
            f"'{self.arquivo}': {erro}",
            RuntimeWarning,
            stacklevel=2,
        )
