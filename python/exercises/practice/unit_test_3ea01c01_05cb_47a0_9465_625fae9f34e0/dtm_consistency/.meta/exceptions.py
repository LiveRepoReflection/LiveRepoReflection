class DTMError(Exception):
    """Base class for DTM exceptions"""
    pass

class TransactionExistsError(DTMError):
    """Raised when attempting to create a transaction with an existing ID"""
    pass

class TransactionNotFoundError(DTMError):
    """Raised when attempting to access a non-existent transaction"""
    pass

class InvalidTransactionStateError(DTMError):
    """Raised when attempting an operation on a transaction in invalid state"""
    pass