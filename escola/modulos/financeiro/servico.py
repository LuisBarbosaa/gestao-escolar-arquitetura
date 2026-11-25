from __future__ import annotations

from escola.compartilhado.erros import RecursoNaoEncontrado
from escola.compartilhado.eventos import PublicadorDeEventos
from escola.modulos.academico.contratos import MatriculaCancelada, MatriculaConfirmada
from escola.modulos.financeiro.contratos import CarneGerado, MensalidadeResumo
from escola.modulos.financeiro.dominio import PoliticaDeCobranca
from escola.modulos.financeiro.repositorio import RepositorioDeMensalidades


class ServicoFinanceiro:
    """Implementa ``ConsultaFinanceira``.

    O acoplamento com o Acadêmico é só pelos eventos (nome e campos). O
    Acadêmico continua funcionando mesmo se o Financeiro estiver fora do ar.
    """

    def __init__(
        self,
        repositorio: RepositorioDeMensalidades,
        publicador: PublicadorDeEventos,
        politica: PoliticaDeCobranca | None = None,
    ) -> None:
        self._repo = repositorio
        self._publicador = publicador
        self._politica = politica or PoliticaDeCobranca()

    # --- manipuladores de eventos ---
    def ao_confirmar_matricula(self, evento: MatriculaConfirmada) -> None:
        carne = self._politica.gerar_carne(evento.aluno_id, evento.turma_id, evento.ano_letivo)
        self._repo.salvar_todas(carne)
        self._publicador.publicar(
            CarneGerado(
                aluno_id=evento.aluno_id, quantidade_parcelas=len(carne),
                valor_parcela=self._politica.valor_mensal,
                primeiro_vencimento=carne[0].vencimento,
            )
        )

    def ao_cancelar_matricula(self, evento: MatriculaCancelada) -> None:
        mensalidades = [m for m in self._repo.do_aluno(evento.aluno_id) if m.turma_id == evento.turma_id]
        for m in mensalidades:
            m.cancelar()
        self._repo.salvar_todas(mensalidades)

    # --- casos de uso ---
    def registrar_pagamento(self, mensalidade_id: str) -> None:
        mensalidade = self._repo.por_id(mensalidade_id)
        if mensalidade is None:
            raise RecursoNaoEncontrado("mensalidade não encontrada")
        mensalidade.pagar()
        self._repo.salvar_todas([mensalidade])

    def mensalidades_do_aluno(self, aluno_id: str) -> list[MensalidadeResumo]:
        return [
            MensalidadeResumo(
                id=m.id, competencia=m.competencia, vencimento=m.vencimento,
                valor=m.valor, status=m.status.value,
            )
            for m in self._repo.do_aluno(aluno_id)
        ]
