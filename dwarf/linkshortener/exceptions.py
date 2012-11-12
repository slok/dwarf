from dwarf.exceptions import DwarfException


class LinkShortenerError(DwarfException):
    pass


class LinkShortenerLengthError(LinkShortenerError):
    pass
