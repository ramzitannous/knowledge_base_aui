class ResourceConflict(Exception):
    """Raised when a unique constraint or duplicate resource conflict occurs."""
    pass

class ResourceNotFound(Exception):
    """Raised when a requested resource is not found."""
    pass