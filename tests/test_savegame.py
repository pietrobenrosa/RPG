import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from jogo import Jogo
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
            {"nome": "Chave Dourada", "sala": "sala_hibernacao", "x": 500, "y": 430},
            jogo.itens_no_chao,
        )
        self.assertEqual(jogo.xp, 20)
        self.assertEqual(jogo.pecas, {"Módulo de Energia"})
        jogo._iniciar_mapa.assert_called_once_with()

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
        jogo.xp = 0
        jogo.xp_proximo_nivel = 100
        jogo.pecas = set()
        jogo.ataque_extra = 0

        dados = jogo._dados_salvamento()

        self.assertTrue(dados["porta3_tentativa_usada"])
        self.assertFalse(dados["porta3_aberta"])


if __name__ == "__main__":
    unittest.main()
