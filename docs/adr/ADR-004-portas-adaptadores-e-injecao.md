# ADR-004: Portas e adaptadores com injeção de dependência

**Status:** aceita

## Decisão
Serviços dependem de interfaces (repositórios, canal de envio, barramento de eventos). As
implementações concretas são escolhidas e injetadas em um único lugar: `escola/aplicacao.py`
(raiz de composição).

## Consequências
- (+) Trocar memória por SQLite, ou console por SMTP, é mudança de uma linha na composição.
- (+) Testes usam dublês (ex.: `CanalFalso`) sem nenhum framework.
- (−) Um pouco mais de código (interfaces) do que instanciar tudo diretamente.
