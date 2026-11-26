import json
import os
from pathlib import Path
import tempfile


ARQUIVO_SAVE = Path(__file__).resolve().parents[1] / "dados" / "savegame.json"
VERSAO_SAVE = 1


def salvar_jogo(dados, caminho=ARQUIVO_SAVE):
    caminho = Path(caminho)
    conteudo = json.dumps(
        dados,
        ensure_ascii=False,
        indent=2,
        allow_nan=False,
    )
    caminho.parent.mkdir(parents=True, exist_ok=True)
    arquivo_temporario = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=caminho.parent,
            prefix=f".{caminho.name}.",
            suffix=".tmp",
            delete=False,
        ) as arquivo:
            arquivo_temporario = Path(arquivo.name)
            arquivo.write(conteudo)
        os.replace(arquivo_temporario, caminho)
        arquivo_temporario = None
    finally:
        if arquivo_temporario is not None:
            try:
                arquivo_temporario.unlink()
            except FileNotFoundError:
                pass


def carregar_jogo(caminho=ARQUIVO_SAVE):
    caminho = Path(caminho)
    try:
        with caminho.open("r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
    except json.JSONDecodeError as erro:
        raise ValueError(f"O arquivo de save está inválido: {erro}") from erro
    except UnicodeDecodeError as erro:
        raise ValueError("O arquivo de save não está codificado em UTF-8.") from erro

    if not isinstance(dados, dict):
        raise ValueError("O arquivo de save precisa conter um objeto JSON.")
    versao = dados.get("versao")
    if isinstance(versao, bool) or versao != VERSAO_SAVE:
        raise ValueError("A versão do arquivo de save não é compatível.")
    return dados
