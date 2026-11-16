from dataclasses import dataclass


@dataclass
class Entidade:
    """Base comum para heróis, anomalias, robôs e chefes (5 atributos)."""

    nome: str
    hp: int
    ataque: int
    defesa: int
    nivel: int

    @property
    def viva(self):
        return self.hp > 0
