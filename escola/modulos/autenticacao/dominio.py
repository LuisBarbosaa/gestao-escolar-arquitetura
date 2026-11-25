from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from escola.compartilhado.erros import ErroDeDominio
from escola.compartilhado.seguranca import Perfil

ITERACOES_HASH = 120_000
VALIDADE_TOKEN = timedelta(hours=8)
TAMANHO_MINIMO_SENHA = 6


@dataclass
class Usuario:
    login: str
    perfil: Perfil
    sal: bytes
    hash_senha: bytes

    @classmethod
    def criar(cls, login: str, senha: str, perfil: Perfil) -> "Usuario":
        if len(senha) < TAMANHO_MINIMO_SENHA:
            raise ErroDeDominio(f"a senha deve ter ao menos {TAMANHO_MINIMO_SENHA} caracteres")
        sal = secrets.token_bytes(16)
        return cls(login=login, perfil=perfil, sal=sal, hash_senha=_hash(senha, sal))

    def confere_senha(self, senha: str) -> bool:
        return hmac.compare_digest(self.hash_senha, _hash(senha, self.sal))


@dataclass
class Sessao:
    token: str
    login: str
    expira_em: datetime = field(default_factory=lambda: datetime.now() + VALIDADE_TOKEN)

    @property
    def expirada(self) -> bool:
        return datetime.now() >= self.expira_em


def _hash(senha: str, sal: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", senha.encode(), sal, ITERACOES_HASH)
