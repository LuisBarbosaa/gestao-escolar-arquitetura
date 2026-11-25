"""Eventos de domínio e barramento de eventos.

Os módulos dependem apenas das interfaces ``PublicadorDeEventos`` e
``AssinanteDeEventos``. A implementação em memória pode ser trocada por uma
fila real (RabbitMQ, Redis Streams, SQS...) sem alterar nenhum módulo.
"""
from __future__ import annotations

import logging
import queue
import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Protocol, TypeVar

log = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class EventoDeDominio:
    ocorrido_em: datetime = field(default_factory=datetime.now)


E = TypeVar("E", bound=EventoDeDominio)


class PublicadorDeEventos(Protocol):
    def publicar(self, evento: EventoDeDominio) -> None: ...


class AssinanteDeEventos(Protocol):
    def assinar(self, tipo: type[E], manipulador: Callable[[E], None]) -> None: ...


class BarramentoEmMemoria:
    """Barramento in-process.

    Com ``assincrono=True`` os eventos vão para uma fila e são tratados por uma
    thread separada, então quem publica não espera os assinantes terminarem
    (reduz a conascência temporal). Nos testes usamos o modo síncrono para
    deixar o resultado determinístico.
    """

    def __init__(self, assincrono: bool = False) -> None:
        self._manipuladores: dict[type, list[Callable]] = {}
        self._assincrono = assincrono
        self._fila: queue.Queue[EventoDeDominio] = queue.Queue()
        if assincrono:
            threading.Thread(target=self._consumir, daemon=True).start()

    def assinar(self, tipo: type[E], manipulador: Callable[[E], None]) -> None:
        self._manipuladores.setdefault(tipo, []).append(manipulador)

    def publicar(self, evento: EventoDeDominio) -> None:
        if self._assincrono:
            self._fila.put(evento)
        else:
            self._despachar(evento)

    def aguardar(self) -> None:
        """Bloqueia até a fila esvaziar (útil na demonstração)."""
        if self._assincrono:
            self._fila.join()

    def _consumir(self) -> None:
        while True:
            evento = self._fila.get()
            try:
                self._despachar(evento)
            finally:
                self._fila.task_done()

    def _despachar(self, evento: EventoDeDominio) -> None:
        for manipulador in self._manipuladores.get(type(evento), []):
            try:
                manipulador(evento)
            except Exception:  # falha de um assinante não derruba quem publicou
                log.exception("Falha ao tratar %s em %s", type(evento).__name__, manipulador)
