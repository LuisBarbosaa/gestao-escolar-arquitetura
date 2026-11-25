from __future__ import annotations

from typing import Protocol

from escola.modulos.avaliacao.dominio import DiarioDoAluno


class RepositorioDeDiarios(Protocol):
    def obter_ou_criar(self, aluno_id: str, turma_id: str, disciplina_codigo: str) -> DiarioDoAluno: ...
    def salvar(self, diario: DiarioDoAluno) -> None: ...
    def do_aluno(self, aluno_id: str, turma_id: str) -> list[DiarioDoAluno]: ...


class RepositorioDeDiariosEmMemoria:
    def __init__(self) -> None:
        self._dados: dict[tuple[str, str, str], DiarioDoAluno] = {}

    def obter_ou_criar(self, aluno_id: str, turma_id: str, disciplina_codigo: str) -> DiarioDoAluno:
        chave = (aluno_id, turma_id, disciplina_codigo)
        return self._dados.get(chave) or DiarioDoAluno(aluno_id, turma_id, disciplina_codigo)

    def salvar(self, diario: DiarioDoAluno) -> None:
        self._dados[(diario.aluno_id, diario.turma_id, diario.disciplina_codigo)] = diario

    def do_aluno(self, aluno_id: str, turma_id: str) -> list[DiarioDoAluno]:
        return [d for (a, t, _), d in self._dados.items() if a == aluno_id and t == turma_id]
