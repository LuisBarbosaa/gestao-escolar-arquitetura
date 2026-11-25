from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from datetime import date

from escola.compartilhado.erros import ErroDeDominio

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True)
class Responsavel:
    nome: str
    email: str

    def __post_init__(self) -> None:
        if not self.nome.strip():
            raise ErroDeDominio("nome do responsável é obrigatório")
        if not _EMAIL.match(self.email):
            raise ErroDeDominio("e-mail do responsável inválido")


@dataclass
class Aluno:
    id: str
    ra: str
    nome: str
    data_nascimento: date
    responsavel: Responsavel
    ativo: bool = True

    @classmethod
    def novo(cls, nome: str, data_nascimento: date, responsavel: Responsavel, sequencial: int) -> "Aluno":
        if len(nome.strip()) < 3:
            raise ErroDeDominio("nome do aluno muito curto")
        if data_nascimento >= date.today():
            raise ErroDeDominio("data de nascimento inválida")
        ra = f"{date.today().year}{sequencial:05d}"
        return cls(str(uuid.uuid4()), ra, nome.strip(), data_nascimento, responsavel)

    def inativar(self) -> None:
        self.ativo = False
