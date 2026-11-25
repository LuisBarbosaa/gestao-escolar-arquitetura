"""Porta de persistência do Cadastro e dois adaptadores.

O serviço depende só de ``RepositorioDeAlunos``. A troca entre memória e SQLite
é feita na composição da aplicação, sem tocar em regra de negócio.
"""
from __future__ import annotations

import sqlite3
from datetime import date
from typing import Protocol

from escola.modulos.cadastro.dominio import Aluno, Responsavel


class RepositorioDeAlunos(Protocol):
    def salvar(self, aluno: Aluno) -> None: ...
    def por_id(self, aluno_id: str) -> Aluno | None: ...
    def total(self) -> int: ...


class RepositorioDeAlunosEmMemoria:
    def __init__(self) -> None:
        self._dados: dict[str, Aluno] = {}

    def salvar(self, aluno: Aluno) -> None:
        self._dados[aluno.id] = aluno

    def por_id(self, aluno_id: str) -> Aluno | None:
        return self._dados.get(aluno_id)

    def total(self) -> int:
        return len(self._dados)


class RepositorioDeAlunosSQLite:
    """Cada módulo é dono das suas tabelas (prefixo ``cad_``)."""

    def __init__(self, caminho: str = ":memory:") -> None:
        self._con = sqlite3.connect(caminho, check_same_thread=False)
        self._con.execute(
            """CREATE TABLE IF NOT EXISTS cad_aluno (
                id TEXT PRIMARY KEY, ra TEXT UNIQUE, nome TEXT, data_nascimento TEXT,
                nome_responsavel TEXT, email_responsavel TEXT, ativo INTEGER)"""
        )

    def salvar(self, aluno: Aluno) -> None:
        with self._con:
            self._con.execute(
                "INSERT OR REPLACE INTO cad_aluno VALUES (:id, :ra, :nome, :nasc, :resp, :email, :ativo)",
                {
                    "id": aluno.id, "ra": aluno.ra, "nome": aluno.nome,
                    "nasc": aluno.data_nascimento.isoformat(),
                    "resp": aluno.responsavel.nome, "email": aluno.responsavel.email,
                    "ativo": int(aluno.ativo),
                },
            )

    def por_id(self, aluno_id: str) -> Aluno | None:
        linha = self._con.execute(
            "SELECT id, ra, nome, data_nascimento, nome_responsavel, email_responsavel, ativo "
            "FROM cad_aluno WHERE id = ?", (aluno_id,)
        ).fetchone()
        if linha is None:
            return None
        return Aluno(
            id=linha[0], ra=linha[1], nome=linha[2],
            data_nascimento=date.fromisoformat(linha[3]),
            responsavel=Responsavel(nome=linha[4], email=linha[5]),
            ativo=bool(linha[6]),
        )

    def total(self) -> int:
        return self._con.execute("SELECT COUNT(*) FROM cad_aluno").fetchone()[0]
