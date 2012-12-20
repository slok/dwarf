from dwarf.exceptions import DwarfException


class LinkShortenerError(DwarfException):
    pass


class LinkShortenerLengthError(LinkShortenerError):
    pass


class ShortLinkError(LinkShortenerError):
    pass


class ShortLinkNotFoundError(LinkShortenerError):
    pass
