"""Raiz de composição (composition root).

É o único lugar que conhece as classes concretas de todos os módulos. Aqui as
dependências são criadas e injetadas, e os manipuladores de eventos são
assinados. Trocar um adaptador (ex.: repositório em memória por SQLite, ou o
barramento em memória por uma fila real) é uma mudança só neste arquivo.
"""
from __future__ import annotations

from dataclasses import dataclass

from escola.compartilhado.eventos import BarramentoEmMemoria
from escola.compartilhado.http import Roteador
from escola.compartilhado.seguranca import Perfil
from escola.modulos.academico import rotas as rotas_academico
from escola.modulos.academico.contratos import MatriculaCancelada, MatriculaConfirmada
from escola.modulos.academico.repositorio import RepositorioDeTurmasEmMemoria
from escola.modulos.academico.servico import ServicoAcademico
from escola.modulos.autenticacao import rotas as rotas_autenticacao
from escola.modulos.autenticacao.contratos import CriarUsuario
from escola.modulos.autenticacao.repositorio import RepositorioDeUsuariosEmMemoria
from escola.modulos.autenticacao.servico import ServicoDeAutenticacao
from escola.modulos.avaliacao import rotas as rotas_avaliacao
from escola.modulos.avaliacao.repositorio import RepositorioDeDiariosEmMemoria
from escola.modulos.avaliacao.servico import ServicoDeAvaliacao
from escola.modulos.cadastro import rotas as rotas_cadastro
from escola.modulos.cadastro.repositorio import RepositorioDeAlunosEmMemoria, RepositorioDeAlunosSQLite
from escola.modulos.cadastro.servico import ServicoDeCadastro
from escola.modulos.comunicacao import rotas as rotas_comunicacao
from escola.modulos.comunicacao.dominio import CanalConsole, CanalDeEnvio
from escola.modulos.comunicacao.servico import ServicoDeComunicacao
from escola.modulos.financeiro import rotas as rotas_financeiro
from escola.modulos.financeiro.contratos import CarneGerado
from escola.modulos.financeiro.repositorio import RepositorioDeMensalidadesEmMemoria
from escola.modulos.financeiro.servico import ServicoFinanceiro
from escola.modulos.relatorios import rotas as rotas_relatorios
from escola.modulos.relatorios.servico import GeradorDeBoletim


@dataclass
class Aplicacao:
    barramento: BarramentoEmMemoria
    autenticacao: ServicoDeAutenticacao
    cadastro: ServicoDeCadastro
    academico: ServicoAcademico
    avaliacao: ServicoDeAvaliacao
    financeiro: ServicoFinanceiro
    comunicacao: ServicoDeComunicacao
    relatorios: GeradorDeBoletim
    roteador: Roteador


def montar_aplicacao(
    *,
    assincrono: bool = False,
    banco_sqlite: str | None = None,
    canal: CanalDeEnvio | None = None,
) -> Aplicacao:
    barramento = BarramentoEmMemoria(assincrono=assincrono)

    autenticacao = ServicoDeAutenticacao(RepositorioDeUsuariosEmMemoria())
    repo_alunos = RepositorioDeAlunosSQLite(banco_sqlite) if banco_sqlite else RepositorioDeAlunosEmMemoria()
    cadastro = ServicoDeCadastro(repo_alunos, barramento)
    academico = ServicoAcademico(RepositorioDeTurmasEmMemoria(), cadastro, barramento)
    avaliacao = ServicoDeAvaliacao(RepositorioDeDiariosEmMemoria(), academico)
    financeiro = ServicoFinanceiro(RepositorioDeMensalidadesEmMemoria(), barramento)
    comunicacao = ServicoDeComunicacao(cadastro, canal or CanalConsole())
    relatorios = GeradorDeBoletim(cadastro, academico, avaliacao)

    # Integração assíncrona entre módulos
    barramento.assinar(MatriculaConfirmada, financeiro.ao_confirmar_matricula)
    barramento.assinar(MatriculaCancelada, financeiro.ao_cancelar_matricula)
    barramento.assinar(MatriculaConfirmada, comunicacao.ao_confirmar_matricula)
    barramento.assinar(CarneGerado, comunicacao.ao_gerar_carne)

    roteador = Roteador(validar_token=autenticacao.validar_token)
    rotas_autenticacao.registrar_rotas(roteador, autenticacao)
    rotas_cadastro.registrar_rotas(roteador, cadastro)
    rotas_academico.registrar_rotas(roteador, academico)
    rotas_avaliacao.registrar_rotas(roteador, avaliacao)
    rotas_financeiro.registrar_rotas(roteador, financeiro)
    rotas_comunicacao.registrar_rotas(roteador, comunicacao)
    rotas_relatorios.registrar_rotas(roteador, relatorios)

    autenticacao.criar_usuario(CriarUsuario(login="admin", senha="admin123", perfil=Perfil.ADMINISTRADOR))

    return Aplicacao(barramento, autenticacao, cadastro, academico, avaliacao,
                     financeiro, comunicacao, relatorios, roteador)
