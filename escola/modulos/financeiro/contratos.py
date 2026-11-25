from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Protocol

from escola.compartilhado.eventos import EventoDeDominio


@dataclass(frozen=True, kw_only=True)
class MensalidadeResumo:
    id: str
    competencia: str
    vencimento: date
    valor: Decimal
    status: str


@dataclass(frozen=True, kw_only=True)
class CarneGerado(EventoDeDominio):
    aluno_id: str
    quantidade_parcelas: int
    valor_parcela: Decimal
    primeiro_vencimento: date


class ConsultaFinanceira(Protocol):
    def mensalidades_do_aluno(self, aluno_id: str) -> list[MensalidadeResumo]: ...
