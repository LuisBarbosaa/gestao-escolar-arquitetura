"""Extrai as dependências entre módulos a partir dos imports do código.

Usado pelos testes de arquitetura e pelo relatório de métricas, para que o
mapa de dependências do documento seja sempre o que o código realmente faz.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PACOTE_MODULOS = RAIZ / "escola" / "modulos"
PREFIXO = "escola.modulos."


@dataclass(frozen=True)
class Importacao:
    arquivo: Path
    modulo_origem: str
    alvo: str  # ex.: escola.modulos.cadastro.contratos


def modulos() -> list[str]:
    return sorted(p.name for p in PACOTE_MODULOS.iterdir() if p.is_dir() and not p.name.startswith("_"))


def importacoes(pasta: Path) -> list[tuple[Path, str]]:
    resultado = []
    for arquivo in sorted(pasta.rglob("*.py")):
        arvore = ast.parse(arquivo.read_text(encoding="utf-8"))
        for no in ast.walk(arvore):
            if isinstance(no, ast.ImportFrom) and no.module:
                resultado.append((arquivo, no.module))
            elif isinstance(no, ast.Import):
                resultado.extend((arquivo, a.name) for a in no.names)
    return resultado


def importacoes_entre_modulos() -> list[Importacao]:
    resultado = []
    for origem in modulos():
        for arquivo, alvo in importacoes(PACOTE_MODULOS / origem):
            if alvo.startswith(PREFIXO) and alvo.split(".")[2] != origem:
                resultado.append(Importacao(arquivo, origem, alvo))
    return resultado


def grafo() -> dict[str, set[str]]:
    g: dict[str, set[str]] = {m: set() for m in modulos()}
    for imp in importacoes_entre_modulos():
        g[imp.modulo_origem].add(imp.alvo.split(".")[2])
    return g
