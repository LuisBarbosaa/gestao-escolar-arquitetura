"""Contrato público do módulo de Cadastro.

Outros módulos só podem importar deste arquivo. Ele expõe DTOs imutáveis,
a interface de consulta e os eventos publicados pelo módulo.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Protocol

from escola.compartilhado.eventos import EventoDeDominio


@dataclass(frozen=True, kw_only=True)
class CadastrarAluno:
    nome: str
    data_nascimento: date
    nome_responsavel: str
    email_responsavel: str


@dataclass(frozen=True, kw_only=True)
class AlunoResumo:
    id: str
    ra: str
    nome: str
    nome_responsavel: str
    email_responsavel: str
    ativo: bool


@dataclass(frozen=True, kw_only=True)
class AlunoCadastrado(EventoDeDominio):
    aluno_id: str
    nome: str


class ConsultaDeAlunos(Protocol):
    def obter_aluno(self, aluno_id: str) -> AlunoResumo | None: ...
