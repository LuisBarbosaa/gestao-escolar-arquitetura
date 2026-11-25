"""Roteiro de demonstração para a apresentação: ``python -m escola.demo``.

Percorre o fluxo principal pela API (mesmo caminho de uma requisição real):
login -> cadastro do aluno -> turma -> matrícula -> eventos (financeiro e
comunicação) -> notas e frequência -> boletim.
"""
from escola.aplicacao import montar_aplicacao
from escola.modulos.relatorios.servico import boletim_em_texto


def main() -> None:
    app = montar_aplicacao(assincrono=True)
    api = app.roteador.tratar

    _, r = api("POST", "/auth/login", {"login": "admin", "senha": "admin123"}, None)
    token = r["token"]
    print("1) Login realizado como admin\n")

    _, aluno = api("POST", "/alunos", {
        "nome": "Ana Beatriz Souza", "data_nascimento": "2012-03-15",
        "nome_responsavel": "Carla Souza", "email_responsavel": "carla.souza@email.com",
    }, token)
    print(f"2) Aluno cadastrado: {aluno['nome']} (RA {aluno['ra']})\n")

    _, turma = api("POST", "/turmas", {
        "nome": "8º Ano A", "ano_letivo": 2027, "vagas": 30,
        "disciplinas": [
            {"codigo": "MAT", "nome": "Matemática", "carga_horaria": 160},
            {"codigo": "POR", "nome": "Língua Portuguesa", "carga_horaria": 160},
            {"codigo": "CIE", "nome": "Ciências", "carga_horaria": 120},
        ],
    }, token)
    print(f"3) Turma criada: {turma['nome']}/{turma['ano_letivo']}\n")

    print("4) Matrícula (Financeiro e Comunicação reagem ao evento MatriculaConfirmada):")
    api("POST", f"/turmas/{turma['id']}/matriculas", {"aluno_id": aluno["id"]}, token)
    app.barramento.aguardar()
    _, mensalidades = api("GET", f"/financeiro/alunos/{aluno['id']}/mensalidades", {}, token)
    print(f"   Carnê gerado com {len(mensalidades)} parcelas de R$ {mensalidades[0]['valor']}\n")

    notas = {"MAT": [7.5, 6.0, 8.0, 7.0], "POR": [5.0, 5.5, 6.0, 4.5], "CIE": [9.0, 8.5]}
    for disciplina, valores in notas.items():
        for bimestre, valor in enumerate(valores, start=1):
            api("POST", "/avaliacoes/notas", {
                "aluno_id": aluno["id"], "turma_id": turma["id"],
                "disciplina_codigo": disciplina, "bimestre": bimestre, "valor": valor,
            }, token)
    for disciplina, faltas in {"MAT": 8, "POR": 12, "CIE": 40}.items():
        api("POST", "/avaliacoes/frequencias", {
            "aluno_id": aluno["id"], "turma_id": turma["id"], "disciplina_codigo": disciplina,
            "aulas_dadas": 120, "faltas": faltas,
        }, token)
    print("5) Notas e frequência lançadas\n")

    print(boletim_em_texto(app.relatorios.gerar(aluno["id"], turma["id"])))

    status, erro = api("POST", "/avaliacoes/notas", {
        "aluno_id": aluno["id"], "turma_id": turma["id"],
        "disciplina_codigo": "MAT", "bimestre": 5, "valor": 8,
    }, token)
    print(f"\n6) Regra de domínio protegida: HTTP {status} - {erro['erro']}")


if __name__ == "__main__":
    main()
