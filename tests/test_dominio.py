import unittest
from datetime import date

from escola.compartilhado.erros import ErroDeDominio
from escola.modulos.academico.dominio import Disciplina, Turma
from escola.modulos.avaliacao.contratos import SituacaoFinal
from escola.modulos.avaliacao.dominio import DiarioDoAluno, RegraDeAprovacao
from escola.modulos.cadastro.dominio import Responsavel
from escola.modulos.financeiro.dominio import PoliticaDeCobranca, StatusPagamento


class TestRegraDeAprovacao(unittest.TestCase):
    notas_ok = {1: 7.0, 2: 6.0, 3: 6.5, 4: 8.0}

    def test_aprovado(self):
        self.assertEqual(RegraDeAprovacao.situacao(self.notas_ok, 90.0), SituacaoFinal.APROVADO)

    def test_reprovado_por_nota(self):
        notas = {1: 4.0, 2: 5.0, 3: 6.0, 4: 5.0}
        self.assertEqual(RegraDeAprovacao.situacao(notas, 90.0), SituacaoFinal.REPROVADO_POR_NOTA)

    def test_falta_tem_prioridade_sobre_nota(self):
        self.assertEqual(RegraDeAprovacao.situacao(self.notas_ok, 70.0), SituacaoFinal.REPROVADO_POR_FALTA)

    def test_em_andamento_sem_os_quatro_bimestres(self):
        self.assertEqual(RegraDeAprovacao.situacao({1: 9.0}, None), SituacaoFinal.EM_ANDAMENTO)

    def test_nota_fora_da_faixa(self):
        with self.assertRaises(ErroDeDominio):
            DiarioDoAluno("a", "t", "MAT").lancar_nota(1, 11)


class TestTurma(unittest.TestCase):
    def setUp(self):
        self.turma = Turma.nova("6A", 2027, 1, (Disciplina("MAT", "Matemática", 160),))

    def test_nao_matricula_sem_vaga(self):
        self.turma.matricular("aluno-1")
        with self.assertRaises(ErroDeDominio):
            self.turma.matricular("aluno-2")

    def test_cancelamento_libera_vaga(self):
        self.turma.matricular("aluno-1")
        self.turma.cancelar("aluno-1")
        self.assertEqual(self.turma.vagas_disponiveis, 1)

    def test_nao_matricula_duas_vezes(self):
        self.turma = Turma.nova("6A", 2027, 5, (Disciplina("MAT", "Matemática", 160),))
        self.turma.matricular("aluno-1")
        with self.assertRaises(ErroDeDominio):
            self.turma.matricular("aluno-1")


class TestOutrasRegras(unittest.TestCase):
    def test_email_do_responsavel_invalido(self):
        with self.assertRaises(ErroDeDominio):
            Responsavel("Maria", "maria-sem-arroba")

    def test_carne_tem_doze_parcelas_em_aberto(self):
        carne = PoliticaDeCobranca().gerar_carne("a", "t", 2027)
        self.assertEqual(len(carne), 12)
        self.assertEqual(carne[0].vencimento, date(2027, 1, 10))
        self.assertTrue(all(m.status is StatusPagamento.EM_ABERTO for m in carne))


if __name__ == "__main__":
    unittest.main()
