from __future__ import print_function

import copy
from collections import OrderedDict
from functools import partial
from operator import itemgetter as _itemgetter

import six

# TypedNamedTuple is largely structured the way the code generated by
# NamedTuple is structured.  However, by itself it is empty.  When a
# child class is created, the metaclass on TypedNamedTuple
# (TypedNamedTupleMeta) iterates over the new class looking for TProp
# class properties, which it will then use to build the field list,
# actual tuple, and the properties indexed into the tuple, just like
# on a named tuple.

# TypedNamedTupleMeta also saves the type information into a new field
# on the resulting class (_types).  TypedNamedTuple's __new__ method
# will use that type information for all incoming parameters for the
# new instance, and raise a TypeError (or whatever the type itself
# raises on an incompatible input.


class TypedNamedTupleMeta(type):
    def __new__(mcl, name, parents, dct):
        if name == "TypedNamedTuple":
            return super(TypedNamedTupleMeta,
                         mcl).__new__(mcl, name, parents, dct)
        fields = []
        for k, v in dct.items():
            if k.startswith("_"):
                continue
            if isinstance(v, TProp):
                fields.append((k,) + v)
        if fields:
            fields = sorted(fields, key=lambda f: f[1])
        field_names = tuple(f[0] for f in fields)
        new_dct = {k: v for k, v in dct.items() if k not in field_names}

        if fields:
            new_dct["_fields"] = field_names
            types = {}
            for field_name, idx in zip(field_names, range(len(field_names))):
                new_dct[field_name] = property(_itemgetter(idx),
                                               doc='Alias for field number %d' % idx)
                types[field_name] = fields[idx][2]
            new_dct["_types"] = types
            # Make vars() work on result
            new_dct["__dict__"] = property(parents[0]._asdict)
        ret = super(TypedNamedTupleMeta,
                    mcl).__new__(mcl, name, parents, new_dct)
        return ret


class TProp(tuple):
    cnt = 0
    def __new__(_cls, typ):
        if type(typ) is not type:
            raise TypeError('typ argument must be a type.')
        cnt = _cls.cnt
        _cls.cnt += 1
        return tuple.__new__(_cls, (cnt, typ))

    @classmethod
    def _reset(_cls):
        _cls.cnt = 0


IntProp = partial(TProp, int)
FloatProp = partial(TProp, float)
StrProp = partial(TProp, str)


@six.add_metaclass(TypedNamedTupleMeta)
class TypedNamedTuple(tuple):

    __slots__ = ()

    _fields = ()
    _types = {}
    def __new__(_cls, *args, **kw):
        """Create new instance of namedtype tuple."""
        typed_args = _cls._type_check(*args, **kw)
        return super(TypedNamedTuple, _cls).__new__(_cls, typed_args)

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new NT object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != len(cls._fields):
            raise TypeError('Expected %d arguments, got %d' % (
                len(cls._fields), len(result)))
        return result

    def __repr__(self):
        'Return a nicely formatted representation string'
        args = zip(self._fields, self)
        arg_strs = ["%s=%r" % pair for pair in args]
        return '%s(%s)' % (self.__class__.__name__,
                           ", ".join(arg_strs))

    def _asdict(self):
        'Return a new OrderedDict which maps field names to their values'
        return OrderedDict(zip(self._fields, self))

    def _replace(_self, **kwds):
        'Return a new object replacing specified fields with new values'
        result = _self._make(map(kwds.pop, _self._fields, _self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result

    def __getnewargs__(self):
        'Return self as a plain tuple.  Used by copy and pickle.'
        return tuple(self)

    def __getstate__(self):
        'Exclude the OrderedDict from pickling'
        pass

    @classmethod
    def _type_check(cls, *args, **kw):
        """Check types of args against cls expected types.

        If the type is the expected type, pass though.
        If the type isn't then pass the argument through the type as callable
        to see if coercion is possible.
        """

        ret = []
        if len(args) > len(cls._fields):
            msg = ("__new__() takes %d positional arguments but %d were given"
                   % (len(cls._fields), len(args)))
            raise TypeError(msg)

        faz = zip(cls._fields, args)
        for field, arg in faz:
            typ = cls._types[field]
            if isinstance(arg, typ):
                ret.append(arg)
            else:
                ret.append(typ(arg))

        missing = []
        # Only look for fields not in arg list.
        for field in cls._fields[len(ret):]:
            if field in kw:
                typ = cls._types[field]
                arg = kw[field]
                if isinstance(arg, typ):
                    ret.append(arg)
                else:
                    ret.append(typ(arg))
            else:
                missing.append(field)
        if missing:
            raise TypeError("%s missing %d required positional argument%s: %s"
                            % (cls.__name__, len(missing),
                               "s" if len(missing)>1 else "",
                               ", ".join([repr(m) for m in missing])))

        return ret

    def to_dict(self):
        return dict(zip(self._fields, tuple(self)))
