class DocumentProcessingError(Exception):
    """Raised when a document cannot be parsed or is invalid."""
    pass


class UnsupportedFileFormatError(DocumentProcessingError):
    pass


class EmptyDocumentError(DocumentProcessingError):
    pass


class CorruptedDocumentError(DocumentProcessingError):
    pass

class NotFoundError(Exception):
    """Raised when a requested job or candidate doesn't exist."""
    pass


class InvalidInputError(Exception):
    """Raised when request input is missing or malformed."""
    pass