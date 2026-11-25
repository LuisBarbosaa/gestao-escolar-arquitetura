"""Contrato público do módulo Acadêmico.

Repare que ``StatusMatricula`` NÃO aparece aqui: quem está fora do módulo
pergunta ``matricula_ativa(...)`` em vez de interpretar o status. Assim a regra
do que significa "ativa" fica num lugar só.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from escola.compartilhado.eventos import EventoDeDominio


@dataclass(frozen=True, kw_only=True)
class DisciplinaDaTurma:
    codigo: str
    nome: str
    carga_horaria: int


@dataclass(frozen=True, kw_only=True)
class CriarTurma:
    nome: str
    ano_letivo: int
    vagas: int
    disciplinas: tuple[DisciplinaDaTurma, ...]


@dataclass(frozen=True, kw_only=True)
class MatricularAluno:
    aluno_id: str
    turma_id: str


@dataclass(frozen=True, kw_only=True)
class TurmaResumo:
    id: str
    nome: str
    ano_letivo: int
    vagas_disponiveis: int
    disciplinas: tuple[DisciplinaDaTurma, ...]


@dataclass(frozen=True, kw_only=True)
class MatriculaConfirmada(EventoDeDominio):
    matricula_id: str
    aluno_id: str
    turma_id: str
    ano_letivo: int


@dataclass(frozen=True, kw_only=True)
class MatriculaCancelada(EventoDeDominio):
    matricula_id: str
    aluno_id: str
    turma_id: str


class ConsultaAcademica(Protocol):
    def obter_turma(self, turma_id: str) -> TurmaResumo | None: ...
    def matricula_ativa(self, aluno_id: str, turma_id: str) -> bool: ...
