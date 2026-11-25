# Sistema de Gestão Escolar — Protótipo Arquitetural

Trabalho da disciplina **Arquitetura de Software** (Uni-FACEF, 6º semestre, Prof. Carlos Alberto Lucas).
Tema: **Sistema de Gestão Escolar**, com foco na característica arquitetural **manutenibilidade**.

O protótipo materializa a arquitetura descrita no documento arquitetural: um **monólito modular**
particionado por domínio, com módulos de alta coesão, comunicação por **contratos** e **eventos**,
e **injeção de dependência** em uma raiz de composição única.

## Como executar

Requer apenas **Python 3.11+** (nenhuma dependência externa).

```bash
# roteiro de demonstração (fluxo completo no terminal)
python -m escola.demo

# testes (domínio, integração e regras de arquitetura)
python -m unittest discover -s tests -t . -v

# métricas de acoplamento extraídas do código (Ca, Ce, Instabilidade)
python -m ferramentas.metricas

# API HTTP na porta 8000 (usuário inicial: admin / admin123)
python -m escola
```

Exemplos de chamadas estão em [`docs/exemplos.http`](docs/exemplos.http).

## Estrutura

```
escola/
├── aplicacao.py          # raiz de composição: cria e injeta as dependências
├── compartilhado/        # núcleo genérico: eventos, erros, perfis, roteador HTTP
└── modulos/
    ├── autenticacao/     # usuários, senhas e tokens
    ├── cadastro/         # alunos e responsáveis
    ├── academico/        # turmas e matrículas
    ├── avaliacao/        # notas, frequência e regra de aprovação
    ├── financeiro/       # mensalidades e pagamentos
    ├── comunicacao/      # avisos aos responsáveis
    └── relatorios/       # boletim (somente leitura)
ferramentas/              # extração de dependências e métricas
tests/                    # testes de domínio, integração e arquitetura
docs/
├── adr/                  # registros de decisão arquitetural (ADRs)
└── diagramas/            # C4 (contexto, contêineres, componentes) e sequência
```

Todo módulo segue o mesmo formato:

| Arquivo | Papel | Visível para outros módulos? |
|---|---|---|
| `contratos.py` | DTOs, comandos, eventos e interfaces de consulta | **Sim (único)** |
| `servico.py` | casos de uso do módulo | Não |
| `dominio.py` | entidades e regras de negócio | Não |
| `repositorio.py` | porta e adaptadores de persistência | Não |
| `rotas.py` | adaptador HTTP | Não |

## Regras de arquitetura (verificadas por teste)

1. Um módulo só importa o `contratos.py` de outro módulo.
2. Não há ciclos de dependência entre módulos.
3. O núcleo `compartilhado` não conhece nenhum módulo.
4. O domínio não depende de infraestrutura (SQL, HTTP, JSON).
5. Nenhum módulo depende de Autenticação (as rotas só declaram perfis).
6. Relatórios não recalcula média nem situação (responsabilidade da Avaliação).

## Dependências entre módulos

| Módulo | Ca | Ce | I | Depende de |
|---|---|---|---|---|
| cadastro | 3 | 0 | 0,00 | — |
| academico | 4 | 1 | 0,20 | cadastro |
| avaliacao | 1 | 1 | 0,50 | academico |
| financeiro | 1 | 1 | 0,50 | academico (eventos) |
| comunicacao | 0 | 3 | 1,00 | academico (eventos), cadastro, financeiro (eventos) |
| relatorios | 0 | 3 | 1,00 | academico, avaliacao, cadastro |
| autenticacao | 0 | 0 | — | — |

As dependências apontam sempre na direção dos módulos mais estáveis (I menor).

## Decisões arquiteturais

- [ADR-001 — Monólito modular particionado por domínio](docs/adr/ADR-001-monolito-modular.md)
- [ADR-002 — Comunicação entre módulos por contratos e eventos](docs/adr/ADR-002-comunicacao-entre-modulos.md)
- [ADR-003 — Cada módulo é dono dos seus dados](docs/adr/ADR-003-dados-por-modulo.md)
- [ADR-004 — Portas e adaptadores com injeção de dependência](docs/adr/ADR-004-portas-adaptadores-e-injecao.md)
- [ADR-005 — Funções de aptidão para proteger a arquitetura](docs/adr/ADR-005-funcoes-de-aptidao.md)
- [ADR-006 — Regra de aprovação centralizada no módulo Avaliação](docs/adr/ADR-006-regra-de-aprovacao-centralizada.md)

## Referência

RICHARDS, Mark; FORD, Neal. *Fundamentos da arquitetura de software: uma abordagem moderna de engenharia*. 2. ed. São Paulo: Novatec, 2025.
