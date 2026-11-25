# ADR-006: Regra de aprovação centralizada no módulo Avaliação

**Status:** aceita

## Contexto
Média e situação do aluno aparecem no boletim, no histórico, em alertas aos responsáveis e em
relatórios de rendimento. Se cada um calcular por conta própria, existe conascência de
algoritmo entre módulos: mudar a regra exige mudar todos em sincronia.

## Decisão
Só a classe `RegraDeAprovacao` (módulo Avaliação) calcula média e situação. Os demais módulos
recebem o resultado pronto em `DesempenhoNaDisciplina`, com a situação tipada por
`SituacaoFinal` (enum).

## Consequências
- (+) Trocar média aritmética por ponderada, ou 6,0 por 7,0, muda um arquivo.
- (−) Relatórios depende da disponibilidade do módulo Avaliação para montar o boletim.
