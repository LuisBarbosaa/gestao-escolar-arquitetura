# ADR-001: Monólito modular particionado por domínio

**Status:** aceita

## Contexto
O sistema de gestão escolar atende uma escola (ou uma pequena rede) com picos previsíveis
(período de matrícula, fechamento de bimestre). A característica arquitetural prioritária é a
**manutenibilidade**: as regras mudam com frequência (média mínima, forma de cobrança,
calendário) e a equipe é pequena.

## Decisão
Adotar um **monólito modular** com particionamento **por domínio** (Cadastro, Acadêmico,
Avaliação, Financeiro, Comunicação, Relatórios, Autenticação). Dentro de cada módulo, as
camadas são separadas (rotas, serviço, domínio, repositório).

## Consequências
- (+) Uma mudança de regra de negócio costuma ficar dentro de um módulo só.
- (+) Uma única implantação e um único processo: custo e complexidade operacional baixos.
- (+) As fronteiras já estão definidas; um módulo pode virar serviço separado no futuro.
- (−) Escala como um bloco só; não dá para escalar apenas o Financeiro, por exemplo.
- (−) A disciplina de fronteira depende de regras automatizadas (ver ADR-005).

## Alternativas descartadas
- **Camadas tradicionais (particionamento técnico):** uma regra de matrícula ficaria espalhada
  em controller, service e DAO globais; alterações atravessariam todas as camadas.
- **Microsserviços:** ganho de escalabilidade que o problema não exige, com custo alto de
  infraestrutura, observabilidade e consistência distribuída.
