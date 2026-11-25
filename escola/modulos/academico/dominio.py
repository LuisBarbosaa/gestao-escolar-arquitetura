from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum

from escola.compartilhado.erros import ErroDeDominio


class StatusMatricula(Enum):
    ATIVA = "ativa"
    TRANCADA = "trancada"
    CANCELADA = "cancelada"
    CONCLUIDA = "concluida"


@dataclass(frozen=True)
class Disciplina:
    codigo: str
    nome: str
    carga_horaria: int


@dataclass
class Matricula:
    id: str
    aluno_id: str
    status: StatusMatricula = StatusMatricula.ATIVA

    @property
    def ativa(self) -> bool:
        return self.status is StatusMatricula.ATIVA


@dataclass
class Turma:
    """Agregado: toda alteração de matrícula passa por aqui.

    A ordem "verificar duplicidade -> verificar vaga -> registrar" é uma
    conascência de execução. Ela foi mantida, mas confinada dentro de um único
    método do agregado, então ninguém de fora consegue executar na ordem errada.
    """

    id: str
    nome: str
    ano_letivo: int
    vagas: int
    disciplinas: tuple[Disciplina, ...]
    matriculas: list[Matricula] = field(default_factory=list)

    @classmethod
    def nova(cls, nome: str, ano_letivo: int, vagas: int, disciplinas: tuple[Disciplina, ...]) -> "Turma":
        if vagas <= 0:
            raise ErroDeDominio("a turma precisa ter ao menos uma vaga")
        if not disciplinas:
            raise ErroDeDominio("a turma precisa ter ao menos uma disciplina")
        return cls(str(uuid.uuid4()), nome, ano_letivo, vagas, disciplinas)

    @property
    def vagas_disponiveis(self) -> int:
        return self.vagas - sum(1 for m in self.matriculas if m.ativa)

    def matricular(self, aluno_id: str) -> Matricula:
        if self.matricula_ativa_de(aluno_id):
            raise ErroDeDominio("aluno já matriculado nesta turma")
        if self.vagas_disponiveis == 0:
            raise ErroDeDominio("turma sem vagas")
        matricula = Matricula(id=str(uuid.uuid4()), aluno_id=aluno_id)
        self.matriculas.append(matricula)
        return matricula

    def cancelar(self, aluno_id: str) -> Matricula:
        matricula = self.matricula_ativa_de(aluno_id)
        if matricula is None:
            raise ErroDeDominio("aluno não possui matrícula ativa nesta turma")
        matricula.status = StatusMatricula.CANCELADA
        return matricula

    def matricula_ativa_de(self, aluno_id: str) -> Matricula | None:
        return next((m for m in self.matriculas if m.aluno_id == aluno_id and m.ativa), None)
