from __future__ import annotations

from typing import Protocol

from escola.modulos.financeiro.dominio import Mensalidade


class RepositorioDeMensalidades(Protocol):
    def salvar_todas(self, mensalidades: list[Mensalidade]) -> None: ...
    def por_id(self, mensalidade_id: str) -> Mensalidade | None: ...
    def do_aluno(self, aluno_id: str) -> list[Mensalidade]: ...


class RepositorioDeMensalidadesEmMemoria:
    def __init__(self) -> None:
        self._dados: dict[str, Mensalidade] = {}

    def salvar_todas(self, mensalidades: list[Mensalidade]) -> None:
        for m in mensalidades:
            self._dados[m.id] = m

    def por_id(self, mensalidade_id: str) -> Mensalidade | None:
        return self._dados.get(mensalidade_id)

    def do_aluno(self, aluno_id: str) -> list[Mensalidade]:
        return sorted((m for m in self._dados.values() if m.aluno_id == aluno_id), key=lambda m: m.vencimento)
