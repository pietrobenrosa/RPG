import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dice_anim import AnimadorD20
from audio import AudioPassos
from jogo import (
    Jogo,
    PORTAS_CORREDOR,
    SPAWN_INICIAL,
    TAMANHO_PERSONAGEM,
    VELOCIDADE_JOGADOR,
)


class RotuloFalso:
    def __init__(self):
        self.agendamentos = {}
        self.proximo_id = 0
        self.configuracao = {}

    def configure(self, **kwargs):
        self.configuracao.update(kwargs)

    def after(self, atraso, callback):
        self.proximo_id += 1
        self.agendamentos[self.proximo_id] = (atraso, callback)
        return self.proximo_id

    def after_cancel(self, identificador):
        self.agendamentos.pop(identificador, None)

    def executar_proximo(self):
        identificador = next(iter(self.agendamentos))
        return self.agendamentos.pop(identificador)


class TestMovimentoESalas(unittest.TestCase):
    def test_colisao_bloqueia_capsula_sem_bloquear_corredor_da_sala(self):
        jogo = Jogo.__new__(Jogo)
        jogo.sala_atual = "sala_hibernacao"

        self.assertFalse(jogo._posicao_valida(100, 300))
        self.assertTrue(jogo._posicao_valida(700, 300))

    def test_colisao_do_corredor_segue_as_bordas_do_piso(self):
        jogo = Jogo.__new__(Jogo)
        jogo.sala_atual = "corredor"

        self.assertFalse(jogo._posicao_valida(480, 150))
        self.assertTrue(jogo._posicao_valida(100, 150))
        self.assertFalse(jogo._posicao_valida(100, 300))
        self.assertTrue(jogo._posicao_valida(480, 410))
        self.assertTrue(jogo._posicao_valida(480, 246))
        self.assertFalse(jogo._posicao_valida(480, 245))

    def test_personagem_fica_duas_vezes_maior_no_corredor(self):
        self.assertEqual(TAMANHO_PERSONAGEM["corredor"], 2 * TAMANHO_PERSONAGEM["sala_hibernacao"])

    def test_spawn_inicial_e_velocidade(self):
        self.assertEqual(SPAWN_INICIAL, (235, 410))
        self.assertAlmostEqual(VELOCIDADE_JOGADOR, 3 * 1.3)

    def test_entrada_na_porta_transfere_para_o_corredor(self):
        jogo = Jogo.__new__(Jogo)
        jogo.sala_atual = "sala_hibernacao"
        jogo.player_x = 700
        jogo.player_y = 210
        jogo._carregar_sala = Mock()

        jogo._verificar_teleporte()

        jogo._carregar_sala.assert_called_once_with("corredor", (480, 430))

    def test_porta_de_entrada_no_corredor_volta_para_hibernacao(self):
        jogo = Jogo.__new__(Jogo)
        jogo.sala_atual = "corredor"
        jogo.player_x = 480
        jogo.player_y = 300
        jogo._porta_ocupada = None
        jogo._carregar_sala = Mock()

        jogo._verificar_teleporte()
        jogo._carregar_sala.assert_not_called()

        jogo.player_y = 470
        jogo._verificar_teleporte()

        jogo._carregar_sala.assert_called_once_with("sala_hibernacao", (700, 260))

    def test_quatro_portas_do_corredor_abrem_a_tela_correspondente(self):
        posicoes = {
            1: (305, 450),
            2: (385, 332),
            3: (590, 250),
            4: (690, 450),
        }
        jogo = Jogo.__new__(Jogo)
        jogo.sala_atual = "corredor"
        jogo._porta_ocupada = None
        jogo._abrir_porta = Mock()

        for porta in PORTAS_CORREDOR:
            jogo.player_x, jogo.player_y = posicoes[porta["numero"]]
            self.assertTrue(jogo._posicao_valida(jogo.player_x, jogo.player_y))
            jogo._verificar_porta_corredor()
            jogo._abrir_porta.assert_called_with(porta["numero"])
            jogo._porta_ocupada = None
            jogo._abrir_porta.reset_mock()


class TestAudioPassos(unittest.TestCase):
    @patch("audio.pygame.mixer")
    def test_audio_toca_em_loop_a_partir_do_segundo_dois_e_para_quando_para(self, mixer):
        mixer.get_init.return_value = (44100, -16, 2)
        audio = AudioPassos(Path("passos.mp3"))

        audio.atualizar(False)
        mixer.music.play.assert_not_called()

        audio.atualizar(True)
        audio.atualizar(True)
        mixer.music.load.assert_called_once_with("passos.mp3")
        mixer.music.play.assert_called_once_with(loops=-1, start=2.0)

        audio.atualizar(False)
        mixer.music.stop.assert_called_once_with()


class TestAnimacaoD20(unittest.TestCase):
    @patch("dice_anim.tk.PhotoImage", side_effect=lambda **_kwargs: Mock())
    def test_rolagem_anima_faces_e_termina_no_resultado(self, _photo_image):
        rotulo = RotuloFalso()
        animador = AnimadorD20(rotulo)
        resultados = []

        self.assertEqual(rotulo.configuracao["text"], "D20: 1")
        self.assertFalse(rotulo.agendamentos)
        self.assertEqual(animador.rolar_teste(resultados.append, resultado=20), 20)
        atrasos = []
        while animador.rolando:
            atraso, callback = rotulo.executar_proximo()
            atrasos.append(atraso)
            callback()

        self.assertEqual(resultados, [20])
        self.assertEqual(rotulo.configuracao["text"], "D20: 20")
        self.assertFalse(rotulo.agendamentos)
        self.assertEqual(len(atrasos), 17)
        self.assertLess(atrasos[0], atrasos[-1])

    @patch("dice_anim.tk.PhotoImage", return_value=Mock())
    def test_dado_e_ampliado_em_dois_sem_interpolacao(self, photo_image):
        photo_image.return_value.zoom.return_value = "imagem ampliada"
        animador = AnimadorD20(RotuloFalso())

        self.assertEqual(animador.imagens[1], "imagem ampliada")
        self.assertEqual(photo_image.return_value.zoom.call_count, 20)
        photo_image.return_value.zoom.assert_called_with(2, 2)

    @patch("dice_anim.tk.PhotoImage", side_effect=lambda **_kwargs: Mock())
    def test_rolagem_rejeita_resultado_fora_do_d20(self, _photo_image):
        animador = AnimadorD20(RotuloFalso())

        with self.assertRaises(ValueError):
            animador.rolar_teste(lambda _valor: None, resultado=21)


if __name__ == "__main__":
    unittest.main()
