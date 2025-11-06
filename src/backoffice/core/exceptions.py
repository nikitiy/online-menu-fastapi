class NotFoundError(Exception):
    """Raised when an entity is not found"""

    pass


class SubdomainAlreadyTaken(Exception):
    """Raised when trying to use a subdomain that is already taken"""

    pass


class ForbiddenError(Exception):
    """Raised when user doesn't have permission to perform an action"""

    pass
