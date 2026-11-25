from __future__ import annotations

import secrets

from escola.compartilhado.erros import AcessoNegado, ErroDeDominio
from escola.compartilhado.seguranca import UsuarioAutenticado
from escola.modulos.autenticacao.contratos import CriarUsuario
from escola.modulos.autenticacao.dominio import Sessao, Usuario
from escola.modulos.autenticacao.repositorio import RepositorioDeUsuarios


class ServicoDeAutenticacao:
    def __init__(self, repositorio: RepositorioDeUsuarios) -> None:
        self._repo = repositorio

    def criar_usuario(self, cmd: CriarUsuario) -> None:
        if self._repo.por_login(cmd.login):
            raise ErroDeDominio("login já cadastrado")
        self._repo.salvar(Usuario.criar(cmd.login, cmd.senha, cmd.perfil))

    def entrar(self, login: str, senha: str) -> str:
        usuario = self._repo.por_login(login)
        if usuario is None or not usuario.confere_senha(senha):
            raise AcessoNegado("login ou senha incorretos")
        sessao = Sessao(token=secrets.token_urlsafe(24), login=login)
        self._repo.salvar_sessao(sessao)
        return sessao.token

    def validar_token(self, token: str) -> UsuarioAutenticado | None:
        sessao = self._repo.sessao(token)
        if sessao is None or sessao.expirada:
            return None
        usuario = self._repo.por_login(sessao.login)
        return UsuarioAutenticado(login=usuario.login, perfil=usuario.perfil) if usuario else None
