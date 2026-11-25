from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class LinhaDoBoletim:
    disciplina: str
    notas: dict[int, float]
    media: float | None
    frequencia: float | None
    situacao: str


@dataclass(frozen=True, kw_only=True)
class Boletim:
    aluno: str
    ra: str
    turma: str
    ano_letivo: int
    linhas: tuple[LinhaDoBoletim, ...]
