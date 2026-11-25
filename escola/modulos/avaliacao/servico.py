from __future__ import annotations

from escola.compartilhado.erros import ErroDeDominio, RecursoNaoEncontrado
from escola.modulos.academico.contratos import ConsultaAcademica
from escola.modulos.avaliacao.contratos import (
    DesempenhoNaDisciplina,
    LancarNota,
    RegistrarFrequencia,
)
from escola.modulos.avaliacao.dominio import DiarioDoAluno, RegraDeAprovacao
from escola.modulos.avaliacao.repositorio import RepositorioDeDiarios


class ServicoDeAvaliacao:
    """Implementa ``ConsultaDeDesempenho``."""

    def __init__(self, repositorio: RepositorioDeDiarios, academico: ConsultaAcademica) -> None:
        self._repo = repositorio
        self._academico = academico

    def lancar_nota(self, cmd: LancarNota) -> None:
        diario = self._diario_valido(cmd.aluno_id, cmd.turma_id, cmd.disciplina_codigo)
        diario.lancar_nota(cmd.bimestre, cmd.valor)
        self._repo.salvar(diario)

    def registrar_frequencia(self, cmd: RegistrarFrequencia) -> None:
        diario = self._diario_valido(cmd.aluno_id, cmd.turma_id, cmd.disciplina_codigo)
        diario.registrar_frequencia(cmd.aulas_dadas, cmd.faltas)
        self._repo.salvar(diario)

    def desempenho_do_aluno(self, aluno_id: str, turma_id: str) -> list[DesempenhoNaDisciplina]:
        return [
            DesempenhoNaDisciplina(
                disciplina_codigo=d.disciplina_codigo,
                notas_por_bimestre=dict(sorted(d.notas.items())),
                media=RegraDeAprovacao.media(d.notas),
                frequencia_percentual=d.frequencia_percentual,
                situacao=RegraDeAprovacao.situacao(d.notas, d.frequencia_percentual),
            )
            for d in sorted(self._repo.do_aluno(aluno_id, turma_id), key=lambda x: x.disciplina_codigo)
        ]

    def _diario_valido(self, aluno_id: str, turma_id: str, disciplina: str) -> DiarioDoAluno:
        turma = self._academico.obter_turma(turma_id)
        if turma is None:
            raise RecursoNaoEncontrado("turma não encontrada")
        if disciplina not in {d.codigo for d in turma.disciplinas}:
            raise ErroDeDominio("disciplina não pertence à turma")
        if not self._academico.matricula_ativa(aluno_id, turma_id):
            raise ErroDeDominio("aluno sem matrícula ativa na turma")
        return self._repo.obter_ou_criar(aluno_id, turma_id, disciplina)
