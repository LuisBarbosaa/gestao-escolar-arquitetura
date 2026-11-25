class ErroDeDominio(Exception):
    """Regra de negócio violada (vira HTTP 422)."""


class RecursoNaoEncontrado(ErroDeDominio):
    """Entidade inexistente (vira HTTP 404)."""


class AcessoNegado(Exception):
    """Usuário sem permissão (vira HTTP 401/403)."""
