# Geppetto Exceptions


class InvalidThreadFormatError(KeyError):
    """Invalid thread format.

    Raise if the submitted thread format doesn't have the expected layout.
    Since the UIs and the underlying LLM engines must meet an interface,
    some validations have to be undertaken to assure key fields.
    """