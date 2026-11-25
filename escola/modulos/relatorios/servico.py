from __future__ import annotations

from escola.compartilhado.erros import RecursoNaoEncontrado
from escola.modulos.academico.contratos import ConsultaAcademica
from escola.modulos.avaliacao.contratos import ConsultaDeDesempenho
from escola.modulos.cadastro.contratos import ConsultaDeAlunos
from escola.modulos.relatorios.contratos import Boletim, LinhaDoBoletim


class GeradorDeBoletim:
    def __init__(
        self,
        alunos: ConsultaDeAlunos,
        academico: ConsultaAcademica,
        desempenho: ConsultaDeDesempenho,
    ) -> None:
        self._alunos = alunos
        self._academico = academico
        self._desempenho = desempenho

    def gerar(self, aluno_id: str, turma_id: str) -> Boletim:
        aluno = self._alunos.obter_aluno(aluno_id)
        turma = self._academico.obter_turma(turma_id)
        if aluno is None or turma is None:
            raise RecursoNaoEncontrado("aluno ou turma não encontrados")

        nomes = {d.codigo: d.nome for d in turma.disciplinas}
        resultados = {r.disciplina_codigo: r for r in self._desempenho.desempenho_do_aluno(aluno_id, turma_id)}
        linhas = []
        for codigo, nome in nomes.items():
            r = resultados.get(codigo)
            linhas.append(
                LinhaDoBoletim(
                    disciplina=nome,
                    notas=r.notas_por_bimestre if r else {},
                    media=r.media if r else None,
                    frequencia=r.frequencia_percentual if r else None,
                    situacao=r.situacao.value if r else "sem lançamentos",
                )
            )
        return Boletim(aluno=aluno.nome, ra=aluno.ra, turma=turma.nome,
                       ano_letivo=turma.ano_letivo, linhas=tuple(linhas))


def boletim_em_texto(boletim: Boletim) -> str:
    def fmt(v: float | None) -> str:
        return "-" if v is None else f"{v:.1f}"

    cab = f"{'Disciplina':<22}{'1ºB':>6}{'2ºB':>6}{'3ºB':>6}{'4ºB':>6}{'Média':>8}{'Freq%':>8}  Situação"
    linhas = [
        f"BOLETIM - {boletim.aluno} (RA {boletim.ra}) - {boletim.turma}/{boletim.ano_letivo}",
        cab,
        "-" * len(cab),
    ]
    for l in boletim.linhas:
        notas = "".join(f"{fmt(l.notas.get(b)):>6}" for b in (1, 2, 3, 4))
        linhas.append(f"{l.disciplina:<22}{notas}{fmt(l.media):>8}{fmt(l.frequencia):>8}  {l.situacao}")
    return "\n".join(linhas)
