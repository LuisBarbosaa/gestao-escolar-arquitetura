# ADR-002: Comunicação entre módulos por contratos e eventos

**Status:** aceita

## Decisão
1. Cada módulo publica um arquivo `contratos.py` com DTOs imutáveis, interfaces de consulta
   (`Protocol`) e eventos. É a **única** parte importável por outros módulos.
2. **Consultas** que precisam de resposta imediata são síncronas, via interface injetada
   (ex.: Acadêmico pergunta ao Cadastro se o aluno existe).
3. **Reações** a algo que aconteceu são assíncronas, via eventos de domínio
   (ex.: `MatriculaConfirmada` gera carnê no Financeiro e aviso na Comunicação).

## Consequências
- (+) O Acadêmico não conhece Financeiro nem Comunicação. Novos interessados na matrícula
  (biblioteca, transporte) entram assinando o evento, sem alterar o Acadêmico.
- (+) Falha no envio de e-mail não desfaz a matrícula.
- (−) Consistência eventual entre matrícula e carnê; aceitável para o negócio.
- (−) Fluxos por eventos são mais difíceis de rastrear; mitigado com testes de integração.
