"""Tipos de segurança usados pelas rotas de todos os módulos.

Ficam no núcleo compartilhado para que nenhum módulo precise importar o módulo
de Autenticação: as rotas só declaram quais perfis podem acessá-las.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Perfil(Enum):
    ADMINISTRADOR = "administrador"
    SECRETARIA = "secretaria"
    PROFESSOR = "professor"
    RESPONSAVEL = "responsavel"


@dataclass(frozen=True, kw_only=True)
class UsuarioAutenticado:
    login: str
    perfil: Perfil
