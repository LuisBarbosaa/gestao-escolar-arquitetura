from __future__ import annotations

from escola.modulos.academico.contratos import MatriculaConfirmada
from escola.modulos.cadastro.contratos import ConsultaDeAlunos
from escola.modulos.comunicacao.contratos import NotificacaoResumo
from escola.modulos.comunicacao.dominio import CanalDeEnvio, Notificacao
from escola.modulos.financeiro.contratos import CarneGerado


class ServicoDeComunicacao:
    """Implementa ``ConsultaDeNotificacoes``.

    Antes da refatoração, o envio de e-mail era chamado dentro da matrícula e a
    matrícula só terminava depois do envio (conascência temporal). Agora o envio
    reage a eventos e roda depois, de forma independente.
    """

    def __init__(self, alunos: ConsultaDeAlunos, canal: CanalDeEnvio) -> None:
        self._alunos = alunos
        self._canal = canal
        self._enviadas: list[Notificacao] = []

    def ao_confirmar_matricula(self, evento: MatriculaConfirmada) -> None:
        self._notificar(
            evento.aluno_id,
            "Matrícula confirmada",
            "A matrícula de {nome} para o ano letivo de %d foi confirmada." % evento.ano_letivo,
        )

    def ao_gerar_carne(self, evento: CarneGerado) -> None:
        self._notificar(
            evento.aluno_id,
            "Carnê disponível",
            "O carnê de {nome} tem %d parcelas de R$ %s; a primeira vence em %s."
            % (evento.quantidade_parcelas, evento.valor_parcela, evento.primeiro_vencimento.strftime("%d/%m/%Y")),
        )

    def notificacoes_do_aluno(self, aluno_id: str) -> list[NotificacaoResumo]:
        return [
            NotificacaoResumo(
                destinatario=n.destinatario, assunto=n.assunto,
                mensagem=n.mensagem, enviada_em=n.enviada_em,
            )
            for n in self._enviadas if n.aluno_id == aluno_id
        ]

    def _notificar(self, aluno_id: str, assunto: str, modelo: str) -> None:
        aluno = self._alunos.obter_aluno(aluno_id)
        if aluno is None:
            return
        notificacao = Notificacao(
            aluno_id=aluno_id, destinatario=aluno.email_responsavel,
            assunto=assunto, mensagem=modelo.format(nome=aluno.nome),
        )
        self._canal.enviar(notificacao)
        self._enviadas.append(notificacao)
