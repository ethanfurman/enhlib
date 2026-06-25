version = 0, 0, 14, 1

import re as _re
import sys as _sys

PY_VER = _sys.version_info[:2]

__all__ = (
        'bytes', 'str', 'unicode', 'basestring', 'int', 'long', 'baseinteger',
        'builtins', 'dir', 'ord', 'range', 'xrange', 'zip',
        'NoneType', 'PY_VER',
        )

if PY_VER < (3, 0):
    bytes = str
    str = unicode
    unicode = unicode
    basestring = bytes, unicode
    int = int
    long = long
    baseinteger = int, long
    range = xrange
    import __builtin__ as builtins
else:
    bytes = bytes
    str = str
    unicode = str
    basestring = unicode,
    int = int
    long = int
    baseinteger = int,
    range = range
    import builtins

def dir(obj, pat=None):
    res = builtins.dir(obj)
    if pat is not None:
        res = [s for s in res if _re.search(pat, s)]
    return res


def ord(int_or_char):
    if isinstance(int_or_char, baseinteger):
        return int_or_char
    else:
        return builtins.ord(int_or_char)

try:
    from types import NoneType
except ImportError:
    NoneType = type(None)

from .itertools import xrange, zip
