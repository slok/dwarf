from dwarf.exceptions import DwarfException


class ClickManagerError(DwarfException):
    pass


class ClickError(ClickManagerError):
    pass
