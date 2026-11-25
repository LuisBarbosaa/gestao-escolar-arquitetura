"""Testes do fluxo completo, passando pelo roteador (mesmo caminho da API)."""
import unittest

from escola.aplicacao import montar_aplicacao


class CanalFalso:
    def __init__(self):
        self.enviadas = []

    def enviar(self, notificacao):
        self.enviadas.append(notificacao)


class TestFluxoDeMatricula(unittest.TestCase):
    def setUp(self):
        self.canal = CanalFalso()
        self.app = montar_aplicacao(canal=self.canal)
        self.api = self.app.roteador.tratar
        _, r = self.api("POST", "/auth/login", {"login": "admin", "senha": "admin123"}, None)
        self.token = r["token"]
        _, self.aluno = self.api("POST", "/alunos", {
            "nome": "João Pedro Lima", "data_nascimento": "2013-07-01",
            "nome_responsavel": "Paula Lima", "email_responsavel": "paula@email.com",
        }, self.token)
        _, self.turma = self.api("POST", "/turmas", {
            "nome": "7º Ano B", "ano_letivo": 2027, "vagas": 2,
            "disciplinas": [{"codigo": "MAT", "nome": "Matemática", "carga_horaria": 160}],
        }, self.token)

    def matricular(self):
        return self.api("POST", f"/turmas/{self.turma['id']}/matriculas", {"aluno_id": self.aluno["id"]}, self.token)

    def test_rota_protegida_sem_token(self):
        status, _ = self.api("POST", "/alunos", {}, None)
        self.assertEqual(status, 401)

    def test_matricula_gera_carne_e_notificacoes(self):
        status, _ = self.matricular()
        self.assertEqual(status, 201)
        _, mensalidades = self.api("GET", f"/financeiro/alunos/{self.aluno['id']}/mensalidades", {}, self.token)
        self.assertEqual(len(mensalidades), 12)
        # A ordem entre assinantes não é garantida, e nenhum módulo depende dela.
        self.assertCountEqual([n.assunto for n in self.canal.enviadas], ["Matrícula confirmada", "Carnê disponível"])

    def test_cancelamento_cancela_mensalidades(self):
        self.matricular()
        self.api("POST", f"/turmas/{self.turma['id']}/cancelamentos", {"aluno_id": self.aluno["id"]}, self.token)
        _, mensalidades = self.api("GET", f"/financeiro/alunos/{self.aluno['id']}/mensalidades", {}, self.token)
        self.assertTrue(all(m["status"] == "cancelada" for m in mensalidades))

    def test_falha_na_comunicacao_nao_desfaz_matricula(self):
        class CanalQuebrado:
            def enviar(self, _):
                raise ConnectionError("servidor de e-mail fora do ar")

        app = montar_aplicacao(canal=CanalQuebrado())
        _, r = app.roteador.tratar("POST", "/auth/login", {"login": "admin", "senha": "admin123"}, None)
        t = r["token"]
        _, al = app.roteador.tratar("POST", "/alunos", {
            "nome": "Bruno Alves", "data_nascimento": "2012-01-01",
            "nome_responsavel": "Rita Alves", "email_responsavel": "rita@email.com"}, t)
        _, tu = app.roteador.tratar("POST", "/turmas", {
            "nome": "8A", "ano_letivo": 2027, "vagas": 10,
            "disciplinas": [{"codigo": "MAT", "nome": "Matemática", "carga_horaria": 160}]}, t)
        with self.assertLogs("escola.compartilhado.eventos", level="ERROR"):
            status, _ = app.roteador.tratar("POST", f"/turmas/{tu['id']}/matriculas", {"aluno_id": al["id"]}, t)
        self.assertEqual(status, 201)
        self.assertTrue(app.academico.matricula_ativa(al["id"], tu["id"]))

    def test_nota_exige_matricula_ativa(self):
        status, corpo = self.api("POST", "/avaliacoes/notas", {
            "aluno_id": self.aluno["id"], "turma_id": self.turma["id"],
            "disciplina_codigo": "MAT", "bimestre": 1, "valor": 8,
        }, self.token)
        self.assertEqual(status, 422)
        self.assertIn("matrícula", corpo["erro"])

    def test_boletim_usa_resultado_da_avaliacao(self):
        self.matricular()
        for b, v in enumerate([8, 7, 9, 6], start=1):
            self.api("POST", "/avaliacoes/notas", {
                "aluno_id": self.aluno["id"], "turma_id": self.turma["id"],
                "disciplina_codigo": "MAT", "bimestre": b, "valor": v,
            }, self.token)
        status, boletim = self.api("GET", f"/relatorios/boletim/{self.aluno['id']}?turma={self.turma['id']}", {}, self.token)
        self.assertEqual(status, 200)
        self.assertEqual(boletim["linhas"][0]["media"], 7.5)
        self.assertEqual(boletim["linhas"][0]["situacao"], "aprovado")


class TestTrocaDeAdaptador(unittest.TestCase):
    def test_mesmo_fluxo_com_sqlite(self):
        app = montar_aplicacao(banco_sqlite=":memory:")
        _, r = app.roteador.tratar("POST", "/auth/login", {"login": "admin", "senha": "admin123"}, None)
        status, aluno = app.roteador.tratar("POST", "/alunos", {
            "nome": "Carla Mendes", "data_nascimento": "2011-05-20",
            "nome_responsavel": "Jorge Mendes", "email_responsavel": "jorge@email.com",
        }, r["token"])
        self.assertEqual(status, 201)
        self.assertEqual(app.cadastro.obter_aluno(aluno["id"]).nome, "Carla Mendes")


if __name__ == "__main__":
    unittest.main()
