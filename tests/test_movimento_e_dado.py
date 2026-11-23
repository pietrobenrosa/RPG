import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, call, patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dice_anim import AnimadorD20
from audio import AudioPassos
from jogo import (
    INVENTARIOS_INICIAIS,
    ITEM_CHAVE_DOURADA,
    ITENS_USAVEIS,
    Jogo,
    PORTAS_CORREDOR,
    SPAWN_INICIAL,
    TAMANHO_PERSONAGEM,
    VELOCIDADE_JOGADOR,
)


class CanvasFalso:
    def __init__(self):
        self.agendamentos = {}
        self.proximo_id = 0
        self.configuracoes = {}

    def itemconfigure(self, item, **kwargs):
        self.configuracoes.setdefault(item, {}).update(kwargs)

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
        jogo = Jogo.__new__(Jogo)
        jogo.sala_atual = ITEM_CHAVE_DOURADA["sala"]
        self.assertTrue(
            jogo._posicao_valida(
                ITEM_CHAVE_DOURADA["x"],
                ITEM_CHAVE_DOURADA["y"],
            )
        )

    def test_inventario_inicial_depende_da_classe(self):
        self.assertNotEqual(
            INVENTARIOS_INICIAIS["Engenheiro"],
            INVENTARIOS_INICIAIS["Segurança"],
        )
        self.assertIn("Kit Médico", ITENS_USAVEIS)
        self.assertNotIn("EMP", ITENS_USAVEIS)

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
        jogo._desenhar_opcoes_porta3 = Mock()
        jogo.porta3_aberta = False

        for porta in PORTAS_CORREDOR:
            jogo.player_x, jogo.player_y = posicoes[porta["numero"]]
            self.assertTrue(jogo._posicao_valida(jogo.player_x, jogo.player_y))
            jogo._verificar_porta_corredor()
            if porta["numero"] == 3:
                jogo._abrir_porta.assert_not_called()
                jogo._desenhar_opcoes_porta3.assert_called_once_with()
            else:
                jogo._abrir_porta.assert_called_with(porta["numero"])
            jogo._porta_ocupada = None
            jogo._abrir_porta.reset_mock()
            jogo._desenhar_opcoes_porta3.reset_mock()

    def test_sair_da_area_da_porta3_remove_as_opcoes(self):
        jogo = Jogo.__new__(Jogo)
        jogo.sala_atual = "corredor"
        jogo.player_x, jogo.player_y = (500, 250)
        jogo._porta_ocupada = PORTAS_CORREDOR[2]
        jogo._remover_opcoes_porta3 = Mock()

        jogo._verificar_porta_corredor()

        self.assertIsNone(jogo._porta_ocupada)
        jogo._remover_opcoes_porta3.assert_called_once_with()

    def test_chave_dourada_abre_a_porta_e_e_consumida(self):
        jogo = Jogo.__new__(Jogo)
        jogo._estado = "mundo"
        jogo.sala_atual = "corredor"
        jogo.player_x, jogo.player_y = (590, 250)
        jogo.porta3_aberta = False
        jogo.inventario = {"Chave Dourada": 1}
        jogo._remover_opcoes_porta3 = Mock()
        jogo._abrir_porta = Mock()

        jogo._acao_porta3("chave")

        self.assertNotIn("Chave Dourada", jogo.inventario)
        jogo._abrir_porta.assert_called_once_with(3)

    def test_teste_de_arrombamento_tem_uma_tentativa(self):
        jogo = Jogo.__new__(Jogo)
        jogo._estado = "mundo"
        jogo.sala_atual = "corredor"
        jogo.player_x, jogo.player_y = (590, 250)
        jogo.porta3_tentativa_usada = False
        jogo.teclas_pressionadas = set()
        jogo.animador_d20 = Mock(rolando=False)
        jogo.animador_d20_grande = Mock(rolando=False)
        jogo.audio_passos = Mock()
        jogo.canvas = Mock()
        jogo.d20_rolagem_imagem = 1
        jogo.d20_rolagem_texto = 2
        jogo.d20_rolagem_titulo = 3
        jogo._remover_opcoes_porta3 = Mock()
        jogo._posicionar_dado_hud = Mock()

        jogo._iniciar_teste_porta3()
        jogo._iniciar_teste_porta3()

        self.assertTrue(jogo.porta3_tentativa_usada)
        self.assertEqual(jogo._estado, "teste_porta")
        jogo.animador_d20_grande.rolar_teste.assert_called_once()

    def test_arrombamento_so_abre_com_resultado_18_ou_maior(self):
        jogo = Jogo.__new__(Jogo)
        jogo._estado = "teste_porta"
        jogo.porta3_aberta = False
        jogo.d20_rolagem_imagem = 1
        jogo.d20_rolagem_texto = 2
        jogo.d20_rolagem_titulo = 3
        jogo.canvas = Mock()
        jogo.dialogo_var = Mock()
        jogo._jogador_perto_da_porta3 = Mock(return_value=True)
        jogo._desenhar_opcoes_porta3 = Mock()
        jogo._abrir_porta = Mock()

        jogo._finalizar_teste_porta3(17)

        self.assertFalse(jogo.porta3_aberta)
        self.assertEqual(jogo._estado, "mundo")
        jogo._abrir_porta.assert_not_called()
        jogo._desenhar_opcoes_porta3.assert_called_once_with()

        jogo._estado = "teste_porta"
        jogo._finalizar_teste_porta3(18)

        self.assertTrue(jogo.porta3_aberta)
        jogo._abrir_porta.assert_called_once_with(3)

    def test_resultado_do_d20_fica_visivel_por_tres_segundos(self):
        jogo = Jogo.__new__(Jogo)
        jogo._estado = "teste_porta"
        jogo.animador_d20 = Mock()
        jogo.dialogo_var = Mock()
        jogo.container = Mock()
        jogo._finalizar_teste_porta3 = Mock()

        jogo._resultado_teste_porta3(18)

        jogo.animador_d20.mostrar.assert_called_once_with(18)
        jogo.dialogo_var.set.assert_called_once_with("D20: 18 — precisa de 18+.")
        atraso, callback = jogo.container.after.call_args.args
        self.assertEqual(atraso, 3000)
        callback()
        jogo._finalizar_teste_porta3.assert_called_once_with(18)


class TestAudioPassos(unittest.TestCase):
    @patch("audio.pygame.mixer")
    def test_audio_toca_em_loop_a_partir_do_segundo_dois_e_para_quando_para(self, mixer):
        mixer.get_init.return_value = (44100, -16, 2)
        audio = AudioPassos(Path("passos.mp3"))

        audio.atualizar(False)
        mixer.music.play.assert_not_called()

        audio.atualizar(True)
        mixer.music.get_busy.return_value = True
        audio.atualizar(True)
        mixer.music.load.assert_called_once_with("passos.mp3")
        mixer.music.play.assert_called_once_with(loops=0, start=2.0)

        mixer.music.get_busy.return_value = False
        audio.atualizar(True)
        self.assertEqual(mixer.music.play.call_count, 2)
        self.assertEqual(
            mixer.music.play.call_args_list,
            [
                call(loops=0, start=2.0),
                call(loops=0, start=2.0),
            ],
        )

        audio.atualizar(False)
        mixer.music.stop.assert_called_once_with()


class TestInventario(unittest.TestCase):
    def test_usar_kit_medico_cura_e_consume_um_item(self):
        jogo = Jogo.__new__(Jogo)
        jogo.inventario = {"Kit Médico": 2}
        jogo.classe_atual = "Engenheiro"
        jogo.jogador = Mock(hp=20)
        jogo.lista_inventario = Mock()
        jogo.lista_inventario.curselection.return_value = (0,)
        jogo._itens_inventario = [("Kit Médico", 2)]
        jogo.inventario_feedback = Mock()
        jogo._atualizar_hud = Mock()
        jogo._atualizar_lista_inventario = Mock()

        jogo._usar_item()

        self.assertEqual(jogo.jogador.hp, 32)
        self.assertEqual(jogo.inventario["Kit Médico"], 1)
        jogo._atualizar_hud.assert_called_once_with()

    def test_jogar_item_no_chao_remove_da_mochila_e_registra_na_sala(self):
        jogo = Jogo.__new__(Jogo)
        jogo.inventario = {"EMP": 1}
        jogo.sala_atual = "corredor"
        jogo.player_x = 500
        jogo.player_y = 430
        jogo.itens_no_chao = []
        jogo.lista_inventario = Mock()
        jogo.lista_inventario.curselection.return_value = (0,)
        jogo._itens_inventario = [("EMP", 1)]
        jogo._desenhar_itens_chao = Mock()
        jogo._atualizar_lista_inventario = Mock()
        jogo.inventario_feedback = Mock()

        jogo._jogar_item_no_chao()

        self.assertEqual(jogo.inventario, {})
        self.assertEqual(
            jogo.itens_no_chao,
            [{"nome": "EMP", "sala": "corredor", "x": 500, "y": 430}],
        )
        jogo._desenhar_itens_chao.assert_called_once_with()


class TestAnimacaoD20(unittest.TestCase):
    @patch("dice_anim.tk.PhotoImage", side_effect=lambda **_kwargs: Mock())
    def test_rolagem_anima_faces_e_termina_no_resultado(self, _photo_image):
        canvas = CanvasFalso()
        animador = AnimadorD20(canvas, "imagem", "texto")
        resultados = []

        self.assertEqual(canvas.configuracoes["texto"]["text"], "D20: 1")
        self.assertFalse(canvas.agendamentos)
        self.assertEqual(animador.rolar_teste(resultados.append, resultado=20), 20)
        atrasos = []
        while animador.rolando:
            atraso, callback = canvas.executar_proximo()
            atrasos.append(atraso)
            callback()

        self.assertEqual(resultados, [20])
        self.assertEqual(canvas.configuracoes["texto"]["text"], "D20: 20")
        self.assertEqual(
            canvas.configuracoes["imagem"]["image"],
            animador.imagens[20],
        )
        self.assertFalse(canvas.agendamentos)
        self.assertEqual(len(atrasos), 17)
        self.assertLess(atrasos[0], atrasos[-1])

    @patch("dice_anim.tk.PhotoImage", return_value=Mock())
    def test_dado_e_ampliado_em_dois_sem_interpolacao(self, photo_image):
        photo_image.return_value.zoom.return_value = "imagem ampliada"
        animador = AnimadorD20(CanvasFalso(), "imagem", "texto")

        self.assertEqual(animador.imagens[1], "imagem ampliada")
        self.assertEqual(photo_image.return_value.zoom.call_count, 20)
        photo_image.return_value.zoom.assert_called_with(2, 2)

    @patch("dice_anim.tk.PhotoImage", side_effect=lambda **_kwargs: Mock())
    def test_rolagem_rejeita_resultado_fora_do_d20(self, _photo_image):
        animador = AnimadorD20(CanvasFalso(), "imagem", "texto")

        with self.assertRaises(ValueError):
            animador.rolar_teste(lambda _valor: None, resultado=21)


if __name__ == "__main__":
    unittest.main()
