"""Sobe a API HTTP: ``python -m escola [porta]``."""
import logging
import sys

from escola.aplicacao import montar_aplicacao
from escola.compartilhado.http import servir

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    porta = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    app = montar_aplicacao(assincrono=True, banco_sqlite="escola.db")
    servir(app.roteador, porta)
