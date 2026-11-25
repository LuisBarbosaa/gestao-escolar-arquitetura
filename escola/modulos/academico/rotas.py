from dataclasses import asdict

from escola.compartilhado.erros import RecursoNaoEncontrado
from escola.compartilhado.http import Requisicao, Roteador
from escola.compartilhado.seguranca import Perfil
from escola.modulos.academico.contratos import CriarTurma, DisciplinaDaTurma, MatricularAluno
from escola.modulos.academico.servico import ServicoAcademico

_SECRETARIA = {Perfil.ADMINISTRADOR, Perfil.SECRETARIA}


def registrar_rotas(roteador: Roteador, servico: ServicoAcademico) -> None:
    def criar_turma(req: Requisicao):
        c = req.corpo
        turma = servico.criar_turma(
            CriarTurma(
                nome=c["nome"], ano_letivo=int(c["ano_letivo"]), vagas=int(c["vagas"]),
                disciplinas=tuple(DisciplinaDaTurma(**d) for d in c["disciplinas"]),
            )
        )
        return 201, asdict(turma)

    def obter_turma(req: Requisicao):
        turma = servico.obter_turma(req.parametros["turma_id"])
        if turma is None:
            raise RecursoNaoEncontrado("turma não encontrada")
        return 200, asdict(turma)

    def matricular(req: Requisicao):
        cmd = MatricularAluno(aluno_id=req.corpo["aluno_id"], turma_id=req.parametros["turma_id"])
        return 201, {"matricula_id": servico.matricular(cmd)}

    def cancelar(req: Requisicao):
        cmd = MatricularAluno(aluno_id=req.corpo["aluno_id"], turma_id=req.parametros["turma_id"])
        servico.cancelar_matricula(cmd)
        return 200, {"status": "cancelada"}

    roteador.registrar("POST", "/turmas", criar_turma, _SECRETARIA)
    roteador.registrar("GET", "/turmas/{turma_id}", obter_turma, _SECRETARIA | {Perfil.PROFESSOR})
    roteador.registrar("POST", "/turmas/{turma_id}/matriculas", matricular, _SECRETARIA)
    roteador.registrar("POST", "/turmas/{turma_id}/cancelamentos", cancelar, _SECRETARIA)
