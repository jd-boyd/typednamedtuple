[![Build Status](https://travis-ci.org/jd-boyd/typednamedtuple.svg?branch=master)](https://travis-ci.org/jd-boyd/typednamedtuple)

# About

This library provides namedtuple's with typed fields and a nicer
syntax.  For those used to Django or SQLAlchemy's Declarative ORM,
created a typed named tuple should look familiar.

# Installation

  `pip install typednamedtuple`

# Usage

## Example

```python
class Employee(TypedNamedTuple):
    name = TProp(str)
    wage = TProp(int)
    startdate = datetime.date

    def time_with_employer(self):
        """Will return datetime.timedelta"""
        return datetime.datetime.now().date() - self.startdate


employee = Employee("Bob", 18, datetime.date(2011, 2, 3))
employee.time_with_employer()
```

## `TypedNamedTuple`

When a class inherits from `TypedNamedTuple`, all class members that
are instances of `TProp` will be included as a named tuple field.

Beyond that, the child class of `TypedNamedTuple` is allowed to have
non-tuple class members and methods.  Using non-tuple class members
for mutability is discouraged philosophically, but no steps are taken
to prevent it.

## `TProp(typ)`

This object is used to identify members of `TypedNamedTuple` that are
to be parts of the named tuple.  Values used for `typ` must be types,
either primitives or objects.

Type Checking is performed inside `TypedNamedTuple` by calling
typ(val).  This means that if `typ` is willing, val will be coerced to
`typ`.  This is the default behavior with most system types (`int`,
`str`, etc).  To enforce types strictly without coercion, consider
writing your own `StrictX` class.  See `StrictInt` in
`tests/test_base.py`.

## IntProp, StrProp, FloatProp

These three are factories to simplify repeated uses of `TProp(int)`,
`TProp(str)`, and `TProp(float)`.

# TODO/Bugs

See [github issues](https://github.com/jd-boyd/typednamedtuple/issues).

