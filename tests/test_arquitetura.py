"""Funções de aptidão (fitness functions) da arquitetura.

Se alguém quebrar uma regra arquitetural, o teste falha antes do código chegar
na branch principal. É assim que a documentação continua valendo com o tempo.
"""
import unittest

from ferramentas.dependencias import RAIZ, grafo, importacoes, importacoes_entre_modulos


class TestRegrasDeArquitetura(unittest.TestCase):
    def test_modulo_so_acessa_o_contrato_publico_de_outro_modulo(self):
        violacoes = [
            f"{i.arquivo.relative_to(RAIZ)} importa {i.alvo}"
            for i in importacoes_entre_modulos()
            if not i.alvo.endswith(".contratos")
        ]
        self.assertEqual(violacoes, [], "acesso a detalhe interno de outro módulo")

    def test_nao_existem_ciclos_entre_modulos(self):
        g = grafo()
        visitando, concluidos = set(), set()

        def visitar(m, caminho):
            if m in visitando:
                self.fail("ciclo de dependência: " + " -> ".join(caminho + [m]))
            if m in concluidos:
                return
            visitando.add(m)
            for d in g[m]:
                visitar(d, caminho + [m])
            visitando.discard(m)
            concluidos.add(m)

        for modulo in g:
            visitar(modulo, [])

    def test_compartilhado_nao_conhece_modulos(self):
        ruins = [alvo for _, alvo in importacoes(RAIZ / "escola" / "compartilhado") if alvo.startswith("escola.modulos")]
        self.assertEqual(ruins, [])

    def test_dominio_nao_depende_de_infraestrutura(self):
        proibidos = ("sqlite3", "http", "escola.compartilhado.http", "json")
        ruins = [
            f"{arq.relative_to(RAIZ)} -> {alvo}"
            for arq, alvo in importacoes(RAIZ / "escola" / "modulos")
            if arq.name == "dominio.py" and alvo.startswith(proibidos)
        ]
        self.assertEqual(ruins, [])

    def test_nenhum_modulo_depende_de_autenticacao(self):
        dependentes = [m for m, deps in grafo().items() if "autenticacao" in deps]
        self.assertEqual(dependentes, [])

    def test_relatorios_nao_reimplementa_regra_de_aprovacao(self):
        fonte = "".join(p.read_text(encoding="utf-8") for p in (RAIZ / "escola/modulos/relatorios").rglob("*.py"))
        for termo in ("MEDIA_MINIMA", "sum(", "FREQUENCIA_MINIMA"):
            self.assertNotIn(termo, fonte)


if __name__ == "__main__":
    unittest.main()
