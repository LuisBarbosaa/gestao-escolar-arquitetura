from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True, kw_only=True)
class NotificacaoResumo:
    destinatario: str
    assunto: str
    mensagem: str
    enviada_em: datetime


class ConsultaDeNotificacoes(Protocol):
    def notificacoes_do_aluno(self, aluno_id: str) -> list[NotificacaoResumo]: ...
