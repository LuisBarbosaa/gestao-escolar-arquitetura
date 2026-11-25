from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class Notificacao:
    aluno_id: str
    destinatario: str
    assunto: str
    mensagem: str
    enviada_em: datetime = field(default_factory=datetime.now)


class CanalDeEnvio(Protocol):
    """Porta de saída. Hoje: console. Amanhã: SMTP, WhatsApp, push..."""

    def enviar(self, notificacao: Notificacao) -> None: ...


class CanalConsole:
    def enviar(self, notificacao: Notificacao) -> None:
        print(f"[e-mail para {notificacao.destinatario}] {notificacao.assunto}")
