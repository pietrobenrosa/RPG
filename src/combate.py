from dataclasses import dataclass
import random

from models import Entidade


@dataclass
class ResultadoAtaque:
    dado: int
    dano: int
    critico: bool = False
    falha_critica: bool = False


def rolar_d20():
    return random.randint(1, 20)


def calcular_dano(ataque, defesa, dado):
    """Aplica a regra do D20; defesa reduz metade do ataque, mínimo 1."""
    if dado == 1:
        return ResultadoAtaque(dado=dado, dano=0, falha_critica=True)
    dano_base = max(1, ataque - defesa // 2)
    critico = dado == 20
    return ResultadoAtaque(
        dado=dado,
        dano=dano_base * (2 if critico else 1),
        critico=critico,
    )


def atacar(atacante: Entidade, defensor: Entidade, dado=None):
    resultado = calcular_dano(atacante.ataque, defensor.defesa, dado or rolar_d20())
    defensor.hp = max(0, defensor.hp - resultado.dano)
    return resultado


def testar_fuga(dado=None):
    dado = dado or rolar_d20()
    return dado, dado >= 11
