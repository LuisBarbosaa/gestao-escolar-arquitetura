from __future__ import annotations

from dataclasses import dataclass, field

from escola.compartilhado.erros import ErroDeDominio
from escola.modulos.avaliacao.contratos import SituacaoFinal


class RegraDeAprovacao:
    """Ponto único da regra de aprovação.

    Se a escola mudar a média mínima ou a forma de cálculo (ex.: média
    ponderada), a alteração acontece só aqui. Relatórios e demais módulos
    recebem o resultado já calculado.
    """

    MEDIA_MINIMA = 6.0
    FREQUENCIA_MINIMA = 75.0
    BIMESTRES = (1, 2, 3, 4)

    @classmethod
    def media(cls, notas: dict[int, float]) -> float | None:
        if not notas:
            return None
        return round(sum(notas.values()) / len(notas), 2)

    @classmethod
    def situacao(cls, notas: dict[int, float], frequencia: float | None) -> SituacaoFinal:
        if frequencia is not None and frequencia < cls.FREQUENCIA_MINIMA:
            return SituacaoFinal.REPROVADO_POR_FALTA
        if set(notas) != set(cls.BIMESTRES):
            return SituacaoFinal.EM_ANDAMENTO
        if cls.media(notas) >= cls.MEDIA_MINIMA:
            return SituacaoFinal.APROVADO
        return SituacaoFinal.REPROVADO_POR_NOTA


@dataclass
class DiarioDoAluno:
    """Notas e frequência de um aluno em uma disciplina de uma turma."""

    aluno_id: str
    turma_id: str
    disciplina_codigo: str
    notas: dict[int, float] = field(default_factory=dict)
    aulas_dadas: int = 0
    faltas: int = 0

    def lancar_nota(self, bimestre: int, valor: float) -> None:
        if bimestre not in RegraDeAprovacao.BIMESTRES:
            raise ErroDeDominio("bimestre deve ser entre 1 e 4")
        if not 0 <= valor <= 10:
            raise ErroDeDominio("nota deve estar entre 0 e 10")
        self.notas[bimestre] = round(float(valor), 2)

    def registrar_frequencia(self, aulas_dadas: int, faltas: int) -> None:
        if aulas_dadas < 0 or faltas < 0 or faltas > aulas_dadas:
            raise ErroDeDominio("frequência inválida")
        self.aulas_dadas, self.faltas = aulas_dadas, faltas

    @property
    def frequencia_percentual(self) -> float | None:
        if self.aulas_dadas == 0:
            return None
        return round(100 * (self.aulas_dadas - self.faltas) / self.aulas_dadas, 1)
