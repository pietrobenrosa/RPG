import json
from pathlib import Path


ARQUIVO_SAVE = Path(__file__).resolve().parents[1] / "dados" / "savegame.json"
VERSAO_SAVE = 1


def salvar_jogo(dados, caminho=ARQUIVO_SAVE):
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)


def carregar_jogo(caminho=ARQUIVO_SAVE):
    caminho = Path(caminho)
    try:
        with caminho.open("r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
    except json.JSONDecodeError as erro:
        raise ValueError(f"O arquivo de save está inválido: {erro}") from erro

    if not isinstance(dados, dict):
        raise ValueError("O arquivo de save precisa conter um objeto JSON.")
    if dados.get("versao") != VERSAO_SAVE:
        raise ValueError("A versão do arquivo de save não é compatível.")
    return dados
