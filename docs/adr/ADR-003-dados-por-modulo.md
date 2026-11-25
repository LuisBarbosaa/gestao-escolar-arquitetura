# ADR-003: Cada módulo é dono dos seus dados

**Status:** aceita

## Decisão
Cada módulo tem seu próprio repositório e suas próprias tabelas (prefixo por módulo, ex.:
`cad_aluno`). Nenhum módulo lê tabela de outro; dados de outro módulo são obtidos pela
interface de consulta dele.

## Consequências
- (+) Mudar o esquema de um módulo não quebra os outros.
- (+) Facilita uma eventual extração do módulo para um serviço separado.
- (−) Relatórios precisam compor dados por interfaces em vez de um `JOIN` direto.
