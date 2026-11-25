from dataclasses import asdict
from datetime import date

from escola.compartilhado.erros import RecursoNaoEncontrado
from escola.compartilhado.http import Requisicao, Roteador
from escola.compartilhado.seguranca import Perfil
from escola.modulos.cadastro.contratos import CadastrarAluno
from escola.modulos.cadastro.servico import ServicoDeCadastro

_SECRETARIA = {Perfil.ADMINISTRADOR, Perfil.SECRETARIA}


def registrar_rotas(roteador: Roteador, servico: ServicoDeCadastro) -> None:
    def cadastrar(req: Requisicao):
        c = req.corpo
        aluno = servico.cadastrar_aluno(
            CadastrarAluno(
                nome=c["nome"],
                data_nascimento=date.fromisoformat(c["data_nascimento"]),
                nome_responsavel=c["nome_responsavel"],
                email_responsavel=c["email_responsavel"],
            )
        )
        return 201, asdict(aluno)

    def obter(req: Requisicao):
        aluno = servico.obter_aluno(req.parametros["aluno_id"])
        if aluno is None:
            raise RecursoNaoEncontrado("aluno não encontrado")
        return 200, asdict(aluno)

    roteador.registrar("POST", "/alunos", cadastrar, _SECRETARIA)
    roteador.registrar("GET", "/alunos/{aluno_id}", obter, _SECRETARIA | {Perfil.PROFESSOR})
