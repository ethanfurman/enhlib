from __future__ import division, print_function

from . import baseinteger, basestring, PY_VER

    # gets replaced later by their final values
Unknown = Null = object()

## Logical

class Logical(object):
    """
    Logical field return type.

    Accepts values of True, False, or None/Null.
    boolean value of Unknown is False (use Quantum if you want an exception instead.
    """

    def __new__(cls, value=None):
        if value in (None, Null, Unknown):
            return cls.unknown
        elif isinstance(value, basestring):
            if value.lower() in ('t', 'true', 'y', 'yes', 'on'):
                return cls.true
            elif value.lower() in ('f', 'false', 'n', 'no', 'off'):
                return cls.false
            elif value.lower() in ('?', 'unknown', 'null', 'none', ' ', ''):
                return cls.unknown
            else:
                raise ValueError('unknown value for Logical: %s' % value)
        else:
            return (cls.false, cls.true)[bool(value)]

    def __add__(x, y):
        if isinstance(y, type(None)) or y is Unknown or x is Unknown:
            return Unknown
        try:
            i = int(y)
        except Exception:
            return NotImplemented
        return int(x) + i

    __radd__ = __iadd__ = __add__

    def __sub__(x, y):
        if isinstance(y, type(None)) or y is Unknown or x is Unknown:
            return Unknown
        try:
            i = int(y)
        except Exception:
            return NotImplemented
        return int(x) - i

    __isub__ = __sub__

    def __rsub__(y, x):
        if isinstance(x, type(None)) or x is Unknown or y is Unknown:
            return Unknown
        try:
            i = int(x)
        except Exception:
            return NotImplemented
        return i - int(y)

    def __mul__(x, y):
        if x == 0 or y == 0:
            return 0
        elif isinstance(y, type(None)) or y is Unknown or x is Unknown:
            return Unknown
        try:
            i = int(y)
        except Exception:
            return NotImplemented
        return int(x) * i

    __rmul__ = __imul__ = __mul__

    def __div__(x, y):
        if isinstance(y, type(None)) or y == 0 or y is Unknown or x is Unknown:
            return Unknown
        try:
            i = int(y)
        except Exception:
            return NotImplemented
        return int(x).__div__(i)

    __idiv__ = __div__

    def __rdiv__(y, x):
        if isinstance(x, type(None)) or y == 0 or x is Unknown or y is Unknown:
            return Unknown
        try:
            i = int(x)
        except Exception:
            return NotImplemented
        return i.__div__(int(y))

    def __truediv__(x, y):
        if isinstance(y, type(None)) or y == 0 or y is Unknown or x is Unknown:
            return Unknown
        try:
            i = int(y)
        except Exception:
            return NotImplemented
        return int(x).__truediv__(i)

    __itruediv__ = __truediv__

    def __rtruediv__(y, x):
        if isinstance(x, type(None)) or y == 0 or y is Unknown or x is Unknown:
            return Unknown
        try:
            i = int(x)
        except Exception:
            return NotImplemented
        return i.__truediv__(int(y))

    def __floordiv__(x, y):
        if isinstance(y, type(None)) or y == 0 or y is Unknown or x is Unknown:
            return Unknown
        try:
            i = int(y)
        except Exception:
            return NotImplemented
        return int(x).__floordiv__(i)

    __ifloordiv__ = __floordiv__

    def __rfloordiv__(y, x):
        if isinstance(x, type(None)) or y == 0 or y is Unknown or x is Unknown:
            return Unknown
        try:
            i = int(x)
        except Exception:
            return NotImplemented
        return i.__floordiv__(int(y))

    def __divmod__(x, y):
        if isinstance(y, type(None)) or y == 0 or y is Unknown or x is Unknown:
            return (Unknown, Unknown)
        try:
            i = int(y)
        except Exception:
            return NotImplemented
        return divmod(int(x), i)

    def __rdivmod__(y, x):
        if isinstance(x, type(None)) or y == 0 or y is Unknown or x is Unknown:
            return (Unknown, Unknown)
        try:
            i = int(x)
        except Exception:
            return NotImplemented
        return divmod(i, int(y))

    def __mod__(x, y):
        if isinstance(y, type(None)) or y == 0 or y is Unknown or x is Unknown:
            return Unknown
        try:
            i = int(y)
        except Exception:
            return NotImplemented
        return int(x) % i

    __imod__ = __mod__

    def __rmod__(y, x):
        if isinstance(x, type(None)) or y == 0 or x is Unknown or y is Unknown:
            return Unknown
        try:
            i = int(x)
        except Exception:
            return NotImplemented
        return i % int(y)

    def __pow__(x, y):
        if not isinstance(y, (x.__class__, bool, type(None), baseinteger)):
            return NotImplemented
        if isinstance(y, type(None)) or y is Unknown:
            return Unknown
        i = int(y)
        if i == 0:
            return 1
        if x is Unknown:
            return Unknown
        return int(x) ** i

    __ipow__ = __pow__

    def __rpow__(y, x):
        if not isinstance(x, (y.__class__, bool, type(None), baseinteger)):
            return NotImplemented
        if y is Unknown:
            return Unknown
        i = int(y)
        if i == 0:
            return 1
        if x is Unknown or isinstance(x, type(None)):
            return Unknown
        return int(x) ** i

    def __lshift__(x, y):
        if isinstance(y, type(None)) or x is Unknown or y is Unknown:
            return Unknown
        return int(x.value) << int(y)

    __ilshift__ = __lshift__

    def __rlshift__(y, x):
        if isinstance(x, type(None)) or x is Unknown or y is Unknown:
            return Unknown
        return int(x) << int(y)

    def __rshift__(x, y):
        if isinstance(y, type(None)) or x is Unknown or y is Unknown:
            return Unknown
        return int(x.value) >> int(y)

    __irshift__ = __rshift__

    def __rrshift__(y, x):
        if isinstance(x, type(None)) or x is Unknown or y is Unknown:
            return Unknown
        return int(x) >> int(y)

    def __neg__(x):
        "NEG (negation)"
        if x in (Truth, Falsth):
            return -x.value
        return Unknown

    def __pos__(x):
        "POS (posation)"
        if x in (Truth, Falsth):
            return +x.value
        return Unknown

    def __abs__(x):
        if x in (Truth, Falsth):
            return abs(x.value)
        return Unknown

    def __invert__(x):
        if x in (Truth, Falsth):
            return (Truth, Falsth)[x.value]
        return Unknown

    def __complex__(x):
        if x.value is None:
            raise ValueError("unable to return complex() of %r" % x)
        return complex(x.value)

    def __int__(x):
        if x.value is None:
            raise ValueError("unable to return int() of %r" % x)
        return int(x.value)

    if PY_VER < (3, 0):
        def __long__(x):
            if x.value is None:
                raise ValueError("unable to return long() of %r" % x)
            return long(x.value)

    def __float__(x):
        if x.value is None:
            raise ValueError("unable to return float() of %r" % x)
        return float(x.value)

    if PY_VER < (3, 0):
        def __oct__(x):
            if x.value is None:
                raise ValueError("unable to return oct() of %r" % x)
            return oct(x.value)

        def __hex__(x):
            if x.value is None:
                raise ValueError("unable to return hex() of %r" % x)
            return hex(x.value)

    def __and__(x, y):
        """
        AND (conjunction) x & y:
        True iff both x, y are True
        False iff at least one of x, y is False
        Unknown otherwise
        """
        if (isinstance(x, baseinteger) and not isinstance(x, bool)) or (isinstance(y, baseinteger) and not isinstance(y, bool)):
            if x == 0 or y == 0:
                return 0
            elif x is Unknown or y is Unknown:
                return Unknown
            return int(x) & int(y)
        elif x in (False, Falsth) or y in (False, Falsth):
            return Falsth
        elif x in (True, Truth) and y in (True, Truth):
            return Truth
        elif isinstance(x, type(None)) or isinstance(y, type(None)) or y is Unknown or x is Unknown:
            return Unknown
        return NotImplemented

    __rand__ = __and__

    def __or__(x, y):
        "OR (disjunction): x | y => True iff at least one of x, y is True"
        if (isinstance(x, baseinteger) and not isinstance(x, bool)) or (isinstance(y, baseinteger) and not isinstance(y, bool)):
            if x is Unknown or y is Unknown:
                return Unknown
            return int(x) | int(y)
        elif x in (True, Truth) or y in (True, Truth):
            return Truth
        elif x in (False, Falsth) and y in (False, Falsth):
            return Falsth
        elif isinstance(x, type(None)) or isinstance(y, type(None)) or y is Unknown or x is Unknown:
            return Unknown
        return NotImplemented

    __ror__ = __or__

    def __xor__(x, y):
        "XOR (parity) x ^ y: True iff only one of x,y is True"
        if (isinstance(x, baseinteger) and not isinstance(x, bool)) or (isinstance(y, baseinteger) and not isinstance(y, bool)):
            if x is Unknown or y is Unknown:
                return Unknown
            return int(x) ^ int(y)
        elif x in (True, Truth, False, Falsth) and y in (True, Truth, False, Falsth):
            return {
                    (True, True)  : Falsth,
                    (True, False) : Truth,
                    (False, True) : Truth,
                    (False, False): Falsth,
                   }[(x, y)]
        elif isinstance(x, type(None)) or isinstance(y, type(None)) or y is Unknown or x is Unknown:
            return Unknown
        return NotImplemented

    __rxor__ = __xor__

    if PY_VER < (3, 0):
        def __nonzero__(x):
            "boolean value of Unknown is assumed False"
            return x.value is True
    else:
        def __bool__(x):
            "boolean value of Unknown is assumed False"
            return x.value is True

    def __eq__(x, y):
        if isinstance(y, x.__class__):
            return x.value == y.value
        elif isinstance(y, (bool, type(None), baseinteger)):
            return x.value == y
        return NotImplemented

    def __ge__(x, y):
        if isinstance(y, type(None)) or x is Unknown or y is Unknown:
            return x.value == None
        elif isinstance(y, x.__class__):
            return x.value >= y.value
        elif isinstance(y, (bool, baseinteger)):
            return x.value >= y
        return NotImplemented

    def __gt__(x, y):
        if isinstance(y, type(None)) or x is Unknown or y is Unknown:
            return False
        elif isinstance(y, x.__class__):
            return x.value > y.value
        elif isinstance(y, (bool, baseinteger)):
            return x.value > y
        return NotImplemented

    def __le__(x, y):
        if isinstance(y, type(None)) or x is Unknown or y is Unknown:
            return x.value == None
        elif isinstance(y, x.__class__):
            return x.value <= y.value
        elif isinstance(y, (bool, baseinteger)):
            return x.value <= y
        return NotImplemented

    def __lt__(x, y):
        if isinstance(y, type(None)) or x is Unknown or y is Unknown:
            return False
        elif isinstance(y, x.__class__):
            return x.value < y.value
        elif isinstance(y, (bool, baseinteger)):
            return x.value < y
        return NotImplemented

    def __ne__(x, y):
        if isinstance(y, x.__class__):
            return x.value != y.value
        elif isinstance(y, (bool, type(None), baseinteger)):
            return x.value != y
        return NotImplemented

    def __hash__(x):
        return hash(x.value)

    def __index__(x):
        if x.value is None:
            raise ValueError("unable to return int() of %r" % x)
        return int(x.value)

    def __repr__(x):
        return "Logical(%r)" % x.string

    def __str__(x):
        return x.string

Logical.true = object.__new__(Logical)
Logical.true.value = True
Logical.true.string = 'T'
Logical.false = object.__new__(Logical)
Logical.false.value = False
Logical.false.string = 'F'
Logical.unknown = object.__new__(Logical)
Logical.unknown.value = None
Logical.unknown.string = '?'
Truth = Logical(True)
Falsth = Logical(False)
Unknown = Logical()


## Null

class NullType(object):
    """
    Null object -- any interaction returns Null
    """

    def _null(self, *args, **kwargs):
        return self

    __eq__ = __ne__ = __ge__ = __gt__ = __le__ = __lt__ = _null
    __add__ = __iadd__ = __radd__ = _null
    __sub__ = __isub__ = __rsub__ = _null
    __mul__ = __imul__ = __rmul__ = _null
    __div__ = __idiv__ = __rdiv__ = _null
    __mod__ = __imod__ = __rmod__ = _null
    __pow__ = __ipow__ = __rpow__ = _null
    __and__ = __iand__ = __rand__ = _null
    __xor__ = __ixor__ = __rxor__ = _null
    __or__ = __ior__ = __ror__ = _null
    __truediv__ = __itruediv__ = __rtruediv__ = _null
    __floordiv__ = __ifloordiv__ = __rfloordiv__ = _null
    __lshift__ = __ilshift__ = __rlshift__ = _null
    __rshift__ = __irshift__ = __rrshift__ = _null
    __neg__ = __pos__ = __abs__ = __invert__ = _null
    __call__ = __getattr__ = _null

    def __divmod__(self, other):
        return self, self
    __rdivmod__ = __divmod__

    __hash__ = None

    def __new__(cls, *args):
        return cls.null

    if PY_VER < (3, 0):
        def __nonzero__(self):
            return False
    else:
        def __bool__(self):
            return False


    def __repr__(self):
        return '<null>'

    def __setattr__(self, name, value):
        return None

    def __setitem___(self, index, value):
        return None

    def __str__(self):
        return ''

NullType.null = object.__new__(NullType)
Null = NullType()

## Sentinel

class Sentinel(object):
    """
    When you have to be absolutely sure your object is unique.
    """
    def __init__(self, name, bool=None, doc='', repr=None):
        self.name = name
        self.__doc__ = doc
        self._bool = bool
        self._repr = repr or '<%s>' % name

    def __repr__(self):
        return self._repr

    def __bool__(self):
        if self._bool is None:
            raise NotImplementedError('Sentinel %r has no boolean value' % self.name)
        return self._bool
    __nonzero__ = __bool__


MISSING = Sentinel('MISSING', doc="argument not provided by caller")


# add xmlrpc support
if PY_VER < (3, 0):
    from xmlrpclib import Marshaller
else:
    from xmlrpc.client import Marshaller

# Logical unknown becomes False
Marshaller.dispatch[Logical] = Marshaller.dump_bool
del Marshaller


