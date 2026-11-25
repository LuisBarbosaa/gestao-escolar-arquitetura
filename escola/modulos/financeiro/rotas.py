from dataclasses import asdict

from escola.compartilhado.http import Requisicao, Roteador
from escola.compartilhado.seguranca import Perfil
from escola.modulos.financeiro.servico import ServicoFinanceiro

_FINANCEIRO = {Perfil.ADMINISTRADOR, Perfil.SECRETARIA}


def registrar_rotas(roteador: Roteador, servico: ServicoFinanceiro) -> None:
    def listar(req: Requisicao):
        return 200, [asdict(m) for m in servico.mensalidades_do_aluno(req.parametros["aluno_id"])]

    def pagar(req: Requisicao):
        servico.registrar_pagamento(req.parametros["mensalidade_id"])
        return 200, {"status": "paga"}

    roteador.registrar("GET", "/financeiro/alunos/{aluno_id}/mensalidades", listar, _FINANCEIRO)
    roteador.registrar("POST", "/financeiro/mensalidades/{mensalidade_id}/pagamento", pagar, _FINANCEIRO)
