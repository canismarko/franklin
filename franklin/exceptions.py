class DOIError(RuntimeError):
    """Resolution of a digital object identifier has encountered an error."""
    pass


class DuplicateDOIError(RuntimeError):
    """Trying to add a new bibtex entry when the file already contains this DOI."""
    pass


class BibtexFileNotFoundError(FileNotFoundError):
    pass


class PDFNotFoundError(FileNotFoundError):
    pass
