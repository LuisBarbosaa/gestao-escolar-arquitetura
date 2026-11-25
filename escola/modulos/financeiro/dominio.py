from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum

from escola.compartilhado.erros import ErroDeDominio


class StatusPagamento(Enum):
    EM_ABERTO = "em aberto"
    PAGA = "paga"
    CANCELADA = "cancelada"


@dataclass
class Mensalidade:
    id: str
    aluno_id: str
    turma_id: str
    competencia: str
    vencimento: date
    valor: Decimal
    status: StatusPagamento = StatusPagamento.EM_ABERTO

    def pagar(self) -> None:
        if self.status is not StatusPagamento.EM_ABERTO:
            raise ErroDeDominio(f"mensalidade {self.status.value} não pode ser paga")
        self.status = StatusPagamento.PAGA

    def cancelar(self) -> None:
        if self.status is StatusPagamento.EM_ABERTO:
            self.status = StatusPagamento.CANCELADA


@dataclass(frozen=True)
class PoliticaDeCobranca:
    """Parâmetros de cobrança da escola, configuráveis na composição."""

    valor_mensal: Decimal = Decimal("850.00")
    dia_vencimento: int = 10
    parcelas: int = 12

    def gerar_carne(self, aluno_id: str, turma_id: str, ano_letivo: int) -> list[Mensalidade]:
        return [
            Mensalidade(
                id=str(uuid.uuid4()), aluno_id=aluno_id, turma_id=turma_id,
                competencia=f"{mes:02d}/{ano_letivo}",
                vencimento=date(ano_letivo, mes, self.dia_vencimento),
                valor=self.valor_mensal,
            )
            for mes in range(1, self.parcelas + 1)
        ]
