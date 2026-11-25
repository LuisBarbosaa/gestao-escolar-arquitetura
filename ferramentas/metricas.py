"""Métricas de acoplamento por módulo: ``python -m ferramentas.metricas``.

Ca  = acoplamento aferente (quantos módulos dependem deste)
Ce  = acoplamento eferente (de quantos módulos este depende)
I   = instabilidade = Ce / (Ca + Ce)
"""
from ferramentas.dependencias import grafo


def calcular() -> list[tuple[str, int, int, float | None]]:
    g = grafo()
    linhas = []
    for modulo, saidas in g.items():
        ca = sum(1 for outro, deps in g.items() if modulo in deps)
        ce = len(saidas)
        inst = round(ce / (ca + ce), 2) if (ca + ce) else None
        linhas.append((modulo, ca, ce, inst))
    return linhas


if __name__ == "__main__":
    g = grafo()
    print(f"{'Módulo':<14}{'Ca':>4}{'Ce':>4}{'I':>7}   depende de")
    for modulo, ca, ce, inst in calcular():
        i = "-" if inst is None else f"{inst:.2f}"
        print(f"{modulo:<14}{ca:>4}{ce:>4}{i:>7}   {', '.join(sorted(g[modulo])) or '-'}")
