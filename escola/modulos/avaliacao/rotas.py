from escola.compartilhado.http import Requisicao, Roteador
from escola.compartilhado.seguranca import Perfil
from escola.modulos.avaliacao.contratos import LancarNota, RegistrarFrequencia
from escola.modulos.avaliacao.servico import ServicoDeAvaliacao

_DOCENTES = {Perfil.ADMINISTRADOR, Perfil.PROFESSOR}


def registrar_rotas(roteador: Roteador, servico: ServicoDeAvaliacao) -> None:
    def lancar_nota(req: Requisicao):
        servico.lancar_nota(LancarNota(**req.corpo))
        return 201, {"status": "nota lançada"}

    def registrar_frequencia(req: Requisicao):
        servico.registrar_frequencia(RegistrarFrequencia(**req.corpo))
        return 201, {"status": "frequência registrada"}

    roteador.registrar("POST", "/avaliacoes/notas", lancar_nota, _DOCENTES)
    roteador.registrar("POST", "/avaliacoes/frequencias", registrar_frequencia, _DOCENTES)
