from __future__ import annotations

from escola.compartilhado.erros import RecursoNaoEncontrado
from escola.compartilhado.eventos import PublicadorDeEventos
from escola.modulos.cadastro.contratos import AlunoCadastrado, AlunoResumo, CadastrarAluno
from escola.modulos.cadastro.dominio import Aluno, Responsavel
from escola.modulos.cadastro.repositorio import RepositorioDeAlunos


class ServicoDeCadastro:
    """Implementa ``ConsultaDeAlunos`` e os casos de uso de cadastro."""

    def __init__(self, repositorio: RepositorioDeAlunos, publicador: PublicadorDeEventos) -> None:
        self._repo = repositorio
        self._publicador = publicador

    def cadastrar_aluno(self, cmd: CadastrarAluno) -> AlunoResumo:
        responsavel = Responsavel(nome=cmd.nome_responsavel, email=cmd.email_responsavel)
        aluno = Aluno.novo(cmd.nome, cmd.data_nascimento, responsavel, self._repo.total() + 1)
        self._repo.salvar(aluno)
        self._publicador.publicar(AlunoCadastrado(aluno_id=aluno.id, nome=aluno.nome))
        return _resumo(aluno)

    def inativar_aluno(self, aluno_id: str) -> None:
        aluno = self._repo.por_id(aluno_id)
        if aluno is None:
            raise RecursoNaoEncontrado("aluno não encontrado")
        aluno.inativar()
        self._repo.salvar(aluno)

    def obter_aluno(self, aluno_id: str) -> AlunoResumo | None:
        aluno = self._repo.por_id(aluno_id)
        return _resumo(aluno) if aluno else None


def _resumo(aluno: Aluno) -> AlunoResumo:
    return AlunoResumo(
        id=aluno.id, ra=aluno.ra, nome=aluno.nome,
        nome_responsavel=aluno.responsavel.nome,
        email_responsavel=aluno.responsavel.email,
        ativo=aluno.ativo,
    )
