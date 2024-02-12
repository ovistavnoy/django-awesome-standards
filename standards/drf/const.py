from enum import Enum

__all__ = ('VIEW_SCOPES', )


class VIEW_SCOPES(Enum):
    generic = 1
    create = 2
    list = 3
    receive = 4
    remove = 5
    update = 6
