from escola.compartilhado.http import Requisicao, Roteador
from escola.modulos.autenticacao.servico import ServicoDeAutenticacao


def registrar_rotas(roteador: Roteador, servico: ServicoDeAutenticacao) -> None:
    def login(req: Requisicao):
        token = servico.entrar(req.corpo["login"], req.corpo["senha"])
        return 200, {"token": token}

    roteador.registrar("POST", "/auth/login", login)
