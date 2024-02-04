
class ArityMismatchError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class UnexpectedPositionError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class UnexpectedIndexError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class InversionError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class IndexNotFoundError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message
