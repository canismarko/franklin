class DOIError(RuntimeError):
    """Resolution of a digital object identifier has encountered an error."""
    pass


class DuplicateDOIError(RuntimeError):
    """Trying to add a new bibtex entry when the file already contains this DOI."""
    pass


class BibtexFileNotFoundError(FileNotFoundError):
    pass


class BibtexParseError(RuntimeError):
    """The bibtex string could not be parsed properly."""
    pass


class CassiError(RuntimeError):
    pass


class PDFNotFoundError(FileNotFoundError):
    pass


class FileExistsError(RuntimeError):
    pass


class ConfigError(RuntimeError):
    pass


class UnknownPublisherError(KeyError):
    pass

