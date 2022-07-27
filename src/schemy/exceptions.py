class InvalidFieldName(Exception):

    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self)->str:
        return repr(self.message)

class MissingField(Exception):

    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self)->str:
        return repr(self.message)

class InvalidType(Exception):
    """
    For wrong field type exceptions.
    """
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self)->str:
        return repr(self.message)

class InvalidName(Exception):
    """
    For field name exceptions.
    """
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self)->str:
        return repr(self.message)