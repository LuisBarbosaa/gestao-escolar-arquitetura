from __future__ import annotations

from typing import Protocol

from escola.modulos.autenticacao.dominio import Sessao, Usuario


class RepositorioDeUsuarios(Protocol):
    def salvar(self, usuario: Usuario) -> None: ...
    def por_login(self, login: str) -> Usuario | None: ...
    def salvar_sessao(self, sessao: Sessao) -> None: ...
    def sessao(self, token: str) -> Sessao | None: ...


class RepositorioDeUsuariosEmMemoria:
    def __init__(self) -> None:
        self._usuarios: dict[str, Usuario] = {}
        self._sessoes: dict[str, Sessao] = {}

    def salvar(self, usuario: Usuario) -> None:
        self._usuarios[usuario.login] = usuario

    def por_login(self, login: str) -> Usuario | None:
        return self._usuarios.get(login)

    def salvar_sessao(self, sessao: Sessao) -> None:
        self._sessoes[sessao.token] = sessao

    def sessao(self, token: str) -> Sessao | None:
        return self._sessoes.get(token)
