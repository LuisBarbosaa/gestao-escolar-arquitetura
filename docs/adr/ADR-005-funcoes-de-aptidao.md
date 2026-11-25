# ADR-005: Funções de aptidão para proteger a arquitetura

**Status:** aceita

## Decisão
As regras arquiteturais viram testes automatizados (`tests/test_arquitetura.py`):
- um módulo só importa o `contratos.py` de outro módulo;
- não há ciclos de dependência entre módulos;
- o núcleo `compartilhado` não conhece módulos;
- o domínio não depende de infraestrutura (SQL, HTTP, JSON);
- Relatórios não reimplementa a regra de aprovação.

## Consequências
- (+) A documentação não "envelhece": se o código violar a arquitetura, o build falha.
- (+) As métricas de acoplamento (`python -m ferramentas.metricas`) saem do código real.
