import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from jogo import (
    Jogo,
    NOME_MODULO_CAPSULA,
    NOME_PECA_COFRE_SALA1,
    NOME_PECA_FOGUETE_SALA1,
)
from savegame import VERSAO_SAVE, carregar_jogo, salvar_jogo


class TestSaveGame(unittest.TestCase):
    def test_salvar_e_carregar_preserva_os_dados(self):
        dados = {
            "versao": VERSAO_SAVE,
            "jogador": {"nome": "Vance", "hp": 22},
            "inventario": {"Kit Médico": 1},
        }
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "savegame.json"

            salvar_jogo(dados, caminho)

            self.assertEqual(carregar_jogo(caminho), dados)

    def test_save_com_versao_incompativel_e_rejeitado(self):
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "savegame.json"
            caminho.write_text('{"versao": 999}', encoding="utf-8")

            with self.assertRaises(ValueError):
                carregar_jogo(caminho)

    def test_dado_invalido_nao_corrompe_o_save_existente(self):
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "savegame.json"
            original = {"versao": VERSAO_SAVE, "xp": 10}
            salvar_jogo(original, caminho)

            with self.assertRaises(ValueError):
                salvar_jogo({"versao": VERSAO_SAVE, "xp": float("nan")}, caminho)

            self.assertEqual(carregar_jogo(caminho), original)

    def test_save_com_codificacao_invalida_retorna_erro_compreensivel(self):
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "savegame.json"
            caminho.write_bytes(b"\xff\xfe")

            with self.assertRaisesRegex(ValueError, "UTF-8"):
                carregar_jogo(caminho)

    def test_restaurar_progresso_reconstroi_personagem_e_mundo(self):
        dados = {
            "versao": VERSAO_SAVE,
            "jogador": {
                "nome": "Vance",
                "classe": "Engenheiro",
                "hp": 22,
                "ataque": 6,
                "defesa": 8,
                "nivel": 1,
            },
            "sala_atual": "corredor",
            "posicao": [480, 430],
            "direcao": "baixo",
            "inventario": {"Kit Médico": 1},
            "itens_no_chao": [
                {"nome": "EMP", "sala": "corredor", "x": 500, "y": 430}
            ],
            "xp": 20,
            "xp_proximo_nivel": 100,
            "pecas": ["Módulo de Energia"],
            "ataque_extra": 2,
        }
        jogo = Jogo.__new__(Jogo)
        jogo._iniciar_mapa = Mock()

        jogo._restaurar_progresso(dados)

        self.assertEqual(jogo.jogador.nome, "Vance")
        self.assertEqual(jogo.jogador.hp, 22)
        self.assertEqual(jogo.sala_atual, "corredor")
        self.assertEqual((jogo.player_x, jogo.player_y), (480, 430))
        self.assertEqual(jogo.inventario, {"Kit Médico": 1})
        self.assertFalse(jogo.porta3_tentativa_usada)
        self.assertFalse(jogo.porta3_aberta)
        self.assertIn(
            {"nome": "Chave Dourada", "sala": "sala_1", "x": 850, "y": 470},
            jogo.itens_no_chao,
        )
        self.assertFalse(jogo.tv_sala1_ligada)
        self.assertFalse(jogo.armarios_sala1_investigados)
        self.assertFalse(jogo.armarios_sala1_arrombados)
        self.assertEqual(jogo.xp, 20)
        self.assertEqual(jogo.pecas, {"Módulo de Energia"})
        jogo._iniciar_mapa.assert_called_once_with()

    def test_restaurar_progresso_preserva_tv_e_recompensas_da_sala1(self):
        dados = {
            "versao": VERSAO_SAVE,
            "jogador": {
                "nome": "Vance",
                "classe": "Engenheiro",
                "hp": 22,
                "ataque": 6,
                "defesa": 8,
                "nivel": 1,
            },
            "sala_atual": "sala_1",
            "posicao": [480, 430],
            "direcao": "baixo",
            "inventario": {},
            "itens_no_chao": [],
            "porta3_tentativa_usada": False,
            "porta3_aberta": False,
            "tv_sala1_ligada": True,
            "armarios_sala1_investigados": True,
            "armarios_sala1_arrombados": True,
            "codigo_cofre_sala1": "0042",
            "quadro_sala1_investigado": True,
            "cofre_sala1_aberto": True,
            "xp": 0,
            "xp_proximo_nivel": 100,
            "pecas": [],
            "ataque_extra": 0,
        }
        jogo = Jogo.__new__(Jogo)
        jogo._iniciar_mapa = Mock()

        jogo._restaurar_progresso(dados)

        self.assertTrue(jogo.tv_sala1_ligada)
        self.assertTrue(jogo.armarios_sala1_investigados)
        self.assertTrue(jogo.armarios_sala1_arrombados)
        self.assertEqual(jogo.codigo_cofre_sala1, "0042")
        self.assertTrue(jogo.quadro_sala1_investigado)
        self.assertTrue(jogo.cofre_sala1_aberto)
        self.assertEqual(jogo.inventario["Código do Cofre: 0042"], 1)
        self.assertIn(NOME_PECA_FOGUETE_SALA1, jogo.pecas)
        self.assertIn(NOME_PECA_COFRE_SALA1, jogo.pecas)
        jogo._iniciar_mapa.assert_called_once_with()

    def test_save_antigo_migra_a_pista_para_a_senha_aleatoria(self):
        dados = {
            "versao": VERSAO_SAVE,
            "jogador": {
                "nome": "Vance",
                "classe": "Engenheiro",
                "hp": 22,
                "ataque": 6,
                "defesa": 8,
                "nivel": 1,
            },
            "sala_atual": "sala_1",
            "posicao": [480, 430],
            "direcao": "baixo",
            "inventario": {"Código do Cofre: 4826": 1},
            "itens_no_chao": [],
            "armarios_sala1_investigados": True,
            "xp": 0,
            "xp_proximo_nivel": 100,
            "pecas": [],
            "ataque_extra": 0,
        }
        jogo = Jogo.__new__(Jogo)
        jogo._iniciar_mapa = Mock()

        jogo._restaurar_progresso(dados)

        self.assertRegex(jogo.codigo_cofre_sala1, r"^\d{4}$")
        self.assertEqual(
            jogo.inventario,
            {f"Código do Cofre: {jogo.codigo_cofre_sala1}": 1},
        )

    def test_restaurar_progresso_preserva_sala2_e_modulo_da_capsula(self):
        dados = {
            "versao": VERSAO_SAVE,
            "jogador": {
                "nome": "Vance",
                "classe": "Engenheiro",
                "hp": 22,
                "ataque": 6,
                "defesa": 8,
                "nivel": 1,
            },
            "sala_atual": "sala_2",
            "posicao": [480, 480],
            "direcao": "baixo",
            "inventario": {"Chave de Prata": 1, "Chave de Fenda": 1},
            "itens_no_chao": [],
            "xp": 0,
            "xp_proximo_nivel": 100,
            "pecas": [],
            "ataque_extra": 0,
            "anomalia_sala2_derrotada": True,
            "estantes_sala2_investigadas": [0, 2],
            "modulo_capsula_retirado": True,
        }
        jogo = Jogo.__new__(Jogo)
        jogo._iniciar_mapa = Mock()

        jogo._restaurar_progresso(dados)

        self.assertEqual(jogo.sala_atual, "sala_2")
        self.assertTrue(jogo.anomalia_sala2_derrotada)
        self.assertEqual(jogo.estantes_sala2_investigadas, [0, 2])
        self.assertTrue(jogo.modulo_capsula_retirado)
        self.assertIn(NOME_MODULO_CAPSULA, jogo.pecas)

    def test_save_rejeita_indice_de_estante_repetido(self):
        dados = {
            "versao": VERSAO_SAVE,
            "jogador": {
                "nome": "Vance",
                "classe": "Engenheiro",
                "hp": 22,
                "ataque": 6,
                "defesa": 8,
                "nivel": 1,
            },
            "sala_atual": "sala_2",
            "posicao": [480, 480],
            "direcao": "baixo",
            "inventario": {},
            "itens_no_chao": [],
            "xp": 0,
            "xp_proximo_nivel": 100,
            "pecas": [],
            "ataque_extra": 0,
            "estantes_sala2_investigadas": [1, 1],
        }
        jogo = Jogo.__new__(Jogo)

        with self.assertRaisesRegex(ValueError, "estantes"):
            jogo._restaurar_progresso(dados)

    def test_dados_salvos_incluem_progresso_da_porta_reforcada(self):
        jogo = Jogo.__new__(Jogo)
        jogo.jogador = Mock(
            nome="Vance",
            hp=22,
            ataque=6,
            defesa=8,
            nivel=1,
        )
        jogo.classe_atual = "Engenheiro"
        jogo.sala_atual = "corredor"
        jogo.player_x = 590
        jogo.player_y = 250
        jogo.direcao = "baixo"
        jogo.inventario = {}
        jogo.itens_no_chao = []
        jogo.porta3_tentativa_usada = True
        jogo.porta3_aberta = False
        jogo.anomalia_sala2_derrotada = True
        jogo.estantes_sala2_investigadas = [0, 2]
        jogo.modulo_capsula_retirado = True
        jogo.tv_sala1_ligada = True
        jogo.armarios_sala1_investigados = True
        jogo.armarios_sala1_arrombados = False
        jogo.codigo_cofre_sala1 = "0073"
        jogo.quadro_sala1_investigado = True
        jogo.cofre_sala1_aberto = False
        jogo.xp = 0
        jogo.xp_proximo_nivel = 100
        jogo.pecas = set()
        jogo.ataque_extra = 0

        dados = jogo._dados_salvamento()

        self.assertTrue(dados["porta3_tentativa_usada"])
        self.assertFalse(dados["porta3_aberta"])
        self.assertTrue(dados["anomalia_sala2_derrotada"])
        self.assertEqual(dados["estantes_sala2_investigadas"], [0, 2])
        self.assertTrue(dados["modulo_capsula_retirado"])
        self.assertTrue(dados["tv_sala1_ligada"])
        self.assertTrue(dados["armarios_sala1_investigados"])
        self.assertFalse(dados["armarios_sala1_arrombados"])
        self.assertEqual(dados["codigo_cofre_sala1"], "0073")
        self.assertTrue(dados["quadro_sala1_investigado"])
        self.assertFalse(dados["cofre_sala1_aberto"])


if __name__ == "__main__":
    unittest.main()
