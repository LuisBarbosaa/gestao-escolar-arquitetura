from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from escola.compartilhado.seguranca import Perfil, UsuarioAutenticado


@dataclass(frozen=True, kw_only=True)
class CriarUsuario:
    login: str
    senha: str
    perfil: Perfil


class ValidadorDeToken(Protocol):
    def validar_token(self, token: str) -> UsuarioAutenticado | None: ...
