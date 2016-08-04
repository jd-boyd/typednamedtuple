![TravisCI Status](https://travis-ci.org/jd-boyd/typednamedtuple.png)

# About

# Installation

  `pip install typednamedtuple`

# Usage


## Example

```python
class Employee(TypedNamedTuple):
	name = str
	wage = int
	startdate = datetime.date

	def time_with_employer(self):
		"""Will return datetime.timedelta"""
		return datetime.datetime.now().date() - self.startdate


employee = Employee("Bob", 18, datetime.date(2011, 2, 3)
employee.time_with_employer()
```

# TODO/Bugs

See [github issues](https://github.com/jd-boyd/typednamedtuple/issues).

# Copyright
  This is distributed as BSD.  Copyright 2016 Joshua D. Boyd
