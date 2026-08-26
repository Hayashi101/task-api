class ProductAlreadyExistsError(Exception):
    pass


class UserAlreadyExistsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class InvalidCurrentPasswordError(Exception):
    pass


class UserNotAdminError(Exception):
    pass
