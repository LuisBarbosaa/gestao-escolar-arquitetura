from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol


class SituacaoFinal(Enum):
    EM_ANDAMENTO = "em andamento"
    APROVADO = "aprovado"
    REPROVADO_POR_NOTA = "reprovado por nota"
    REPROVADO_POR_FALTA = "reprovado por falta"


@dataclass(frozen=True, kw_only=True)
class LancarNota:
    """Comando com campos nomeados (kw_only).

    Antes era ``lancar_nota(aluno_id, turma_id, disciplina, bimestre, valor)``:
    trocar a ordem de dois argumentos do mesmo tipo passava sem erro.
    """

    aluno_id: str
    turma_id: str
    disciplina_codigo: str
    bimestre: int
    valor: float


@dataclass(frozen=True, kw_only=True)
class RegistrarFrequencia:
    aluno_id: str
    turma_id: str
    disciplina_codigo: str
    aulas_dadas: int
    faltas: int


@dataclass(frozen=True, kw_only=True)
class DesempenhoNaDisciplina:
    disciplina_codigo: str
    notas_por_bimestre: dict[int, float]
    media: float | None
    frequencia_percentual: float | None
    situacao: SituacaoFinal


class ConsultaDeDesempenho(Protocol):
    def desempenho_do_aluno(self, aluno_id: str, turma_id: str) -> list[DesempenhoNaDisciplina]: ...
