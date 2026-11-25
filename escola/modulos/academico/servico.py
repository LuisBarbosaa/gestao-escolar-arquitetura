from __future__ import annotations

from escola.compartilhado.erros import ErroDeDominio, RecursoNaoEncontrado
from escola.compartilhado.eventos import PublicadorDeEventos
from escola.modulos.academico.contratos import (
    CriarTurma,
    DisciplinaDaTurma,
    MatriculaCancelada,
    MatriculaConfirmada,
    MatricularAluno,
    TurmaResumo,
)
from escola.modulos.academico.dominio import Disciplina, Turma
from escola.modulos.academico.repositorio import RepositorioDeTurmas
from escola.modulos.cadastro.contratos import ConsultaDeAlunos


class ServicoAcademico:
    """Implementa ``ConsultaAcademica``.

    Depende de Cadastro apenas pela interface ``ConsultaDeAlunos``, recebida por
    injeção de dependência no construtor.
    """

    def __init__(
        self,
        repositorio: RepositorioDeTurmas,
        alunos: ConsultaDeAlunos,
        publicador: PublicadorDeEventos,
    ) -> None:
        self._repo = repositorio
        self._alunos = alunos
        self._publicador = publicador

    def criar_turma(self, cmd: CriarTurma) -> TurmaResumo:
        disciplinas = tuple(Disciplina(d.codigo, d.nome, d.carga_horaria) for d in cmd.disciplinas)
        turma = Turma.nova(cmd.nome, cmd.ano_letivo, cmd.vagas, disciplinas)
        self._repo.salvar(turma)
        return _resumo(turma)

    def matricular(self, cmd: MatricularAluno) -> str:
        aluno = self._alunos.obter_aluno(cmd.aluno_id)
        if aluno is None:
            raise RecursoNaoEncontrado("aluno não encontrado")
        if not aluno.ativo:
            raise ErroDeDominio("aluno inativo não pode ser matriculado")
        turma = self._turma(cmd.turma_id)
        matricula = turma.matricular(cmd.aluno_id)
        self._repo.salvar(turma)
        # Financeiro e Comunicação reagem a este evento; o Acadêmico não os conhece.
        self._publicador.publicar(
            MatriculaConfirmada(
                matricula_id=matricula.id, aluno_id=cmd.aluno_id,
                turma_id=turma.id, ano_letivo=turma.ano_letivo,
            )
        )
        return matricula.id

    def cancelar_matricula(self, cmd: MatricularAluno) -> None:
        turma = self._turma(cmd.turma_id)
        matricula = turma.cancelar(cmd.aluno_id)
        self._repo.salvar(turma)
        self._publicador.publicar(
            MatriculaCancelada(matricula_id=matricula.id, aluno_id=cmd.aluno_id, turma_id=turma.id)
        )

    # --- ConsultaAcademica ---
    def obter_turma(self, turma_id: str) -> TurmaResumo | None:
        turma = self._repo.por_id(turma_id)
        return _resumo(turma) if turma else None

    def matricula_ativa(self, aluno_id: str, turma_id: str) -> bool:
        turma = self._repo.por_id(turma_id)
        return bool(turma and turma.matricula_ativa_de(aluno_id))

    def _turma(self, turma_id: str) -> Turma:
        turma = self._repo.por_id(turma_id)
        if turma is None:
            raise RecursoNaoEncontrado("turma não encontrada")
        return turma


def _resumo(turma: Turma) -> TurmaResumo:
    return TurmaResumo(
        id=turma.id, nome=turma.nome, ano_letivo=turma.ano_letivo,
        vagas_disponiveis=turma.vagas_disponiveis,
        disciplinas=tuple(
            DisciplinaDaTurma(codigo=d.codigo, nome=d.nome, carga_horaria=d.carga_horaria)
            for d in turma.disciplinas
        ),
    )
