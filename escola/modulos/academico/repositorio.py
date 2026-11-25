from __future__ import annotations

from typing import Protocol

from escola.modulos.academico.dominio import Turma


class RepositorioDeTurmas(Protocol):
    def salvar(self, turma: Turma) -> None: ...
    def por_id(self, turma_id: str) -> Turma | None: ...


class RepositorioDeTurmasEmMemoria:
    def __init__(self) -> None:
        self._dados: dict[str, Turma] = {}

    def salvar(self, turma: Turma) -> None:
        self._dados[turma.id] = turma

    def por_id(self, turma_id: str) -> Turma | None:
        return self._dados.get(turma_id)
