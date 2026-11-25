from dataclasses import asdict

from escola.compartilhado.http import Requisicao, Roteador
from escola.compartilhado.seguranca import Perfil
from escola.modulos.relatorios.servico import GeradorDeBoletim


def registrar_rotas(roteador: Roteador, gerador: GeradorDeBoletim) -> None:
    def boletim(req: Requisicao):
        return 200, asdict(gerador.gerar(req.parametros["aluno_id"], req.consulta["turma"]))

    roteador.registrar(
        "GET", "/relatorios/boletim/{aluno_id}", boletim,
        {Perfil.ADMINISTRADOR, Perfil.SECRETARIA, Perfil.PROFESSOR, Perfil.RESPONSAVEL},
    )
