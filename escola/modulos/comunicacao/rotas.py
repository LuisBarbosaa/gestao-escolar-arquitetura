from dataclasses import asdict

from escola.compartilhado.http import Requisicao, Roteador
from escola.compartilhado.seguranca import Perfil
from escola.modulos.comunicacao.servico import ServicoDeComunicacao


def registrar_rotas(roteador: Roteador, servico: ServicoDeComunicacao) -> None:
    def listar(req: Requisicao):
        return 200, [asdict(n) for n in servico.notificacoes_do_aluno(req.parametros["aluno_id"])]

    roteador.registrar(
        "GET", "/comunicacao/alunos/{aluno_id}/notificacoes", listar,
        {Perfil.ADMINISTRADOR, Perfil.SECRETARIA},
    )
