"""Roteador HTTP mínimo sobre a biblioteca padrão.

Cada módulo registra suas próprias rotas em ``rotas.py``. O roteador não
conhece nenhum módulo; ele só recebe uma função que valida tokens, injetada
na composição da aplicação (``escola/aplicacao.py``).
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Callable
from urllib.parse import parse_qs, urlparse

from escola.compartilhado.erros import AcessoNegado, ErroDeDominio, RecursoNaoEncontrado
from escola.compartilhado.seguranca import Perfil, UsuarioAutenticado

Resposta = tuple[int, Any]


@dataclass
class Requisicao:
    parametros: dict[str, str] = field(default_factory=dict)
    corpo: dict[str, Any] = field(default_factory=dict)
    consulta: dict[str, str] = field(default_factory=dict)
    usuario: UsuarioAutenticado | None = None


@dataclass
class _Rota:
    metodo: str
    padrao: re.Pattern[str]
    manipulador: Callable[[Requisicao], Resposta]
    perfis: frozenset[Perfil] | None


class Roteador:
    def __init__(self, validar_token: Callable[[str], UsuarioAutenticado | None]) -> None:
        self._rotas: list[_Rota] = []
        self._validar_token = validar_token

    def registrar(
        self,
        metodo: str,
        caminho: str,
        manipulador: Callable[[Requisicao], Resposta],
        perfis: set[Perfil] | None = None,
    ) -> None:
        """``perfis=None`` indica rota pública. Ex.: ``/alunos/{aluno_id}``."""
        regex = "^" + re.sub(r"\{(\w+)\}", r"(?P<\1>[^/]+)", caminho) + "$"
        self._rotas.append(
            _Rota(metodo, re.compile(regex), manipulador, frozenset(perfis) if perfis else None)
        )

    def tratar(self, metodo: str, url: str, corpo: dict[str, Any], token: str | None) -> Resposta:
        partes = urlparse(url)
        for rota in self._rotas:
            achou = rota.padrao.match(partes.path)
            if rota.metodo != metodo or not achou:
                continue
            req = Requisicao(
                parametros=achou.groupdict(),
                corpo=corpo,
                consulta={k: v[0] for k, v in parse_qs(partes.query).items()},
            )
            try:
                if rota.perfis is not None:
                    req.usuario = self._validar_token(token or "")
                    if req.usuario is None:
                        return 401, {"erro": "token ausente ou inválido"}
                    if req.usuario.perfil not in rota.perfis:
                        return 403, {"erro": "perfil sem permissão"}
                return rota.manipulador(req)
            except RecursoNaoEncontrado as e:
                return 404, {"erro": str(e)}
            except ErroDeDominio as e:
                return 422, {"erro": str(e)}
            except AcessoNegado as e:
                return 401, {"erro": str(e)}
            except (KeyError, TypeError, ValueError) as e:
                return 400, {"erro": f"requisição inválida: {e}"}
        return 404, {"erro": "rota não encontrada"}


def servir(roteador: Roteador, porta: int = 8000) -> None:
    class _Handler(BaseHTTPRequestHandler):
        def _processar(self, metodo: str) -> None:
            tamanho = int(self.headers.get("Content-Length") or 0)
            bruto = self.rfile.read(tamanho) if tamanho else b""
            corpo = json.loads(bruto or b"{}")
            auth = self.headers.get("Authorization", "")
            token = auth.removeprefix("Bearer ").strip() or None
            status, dados = roteador.tratar(metodo, self.path, corpo, token)
            saida = json.dumps(dados, ensure_ascii=False, default=str).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(saida)))
            self.end_headers()
            self.wfile.write(saida)

        def do_GET(self) -> None:  # noqa: N802
            self._processar("GET")

        def do_POST(self) -> None:  # noqa: N802
            self._processar("POST")

    print(f"Servidor em http://localhost:{porta}")
    ThreadingHTTPServer(("0.0.0.0", porta), _Handler).serve_forever()
