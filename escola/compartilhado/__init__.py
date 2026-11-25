"""Núcleo compartilhado (kernel).

Só entra aqui o que é genérico e estável: eventos, erros, tipos de segurança
e o roteador HTTP. Nenhuma regra de negócio de módulo deve morar neste pacote,
e ele nunca importa nada de ``escola.modulos``.
"""
