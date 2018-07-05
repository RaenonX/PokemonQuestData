from enum import IntEnum

class EnumWithName(IntEnum):
    def __new__(cls, value, name):
        member = int.__new__(cls, value)
        member._value_ = value
        member._name = name
        return member

    def __int__(self):
        return self._value_

    def __str__(self):
        return self._name

    @classmethod
    def str_get_int(cls, txt):
        for item in cls:
            if str(item) == txt:
                return int(item)

        raise ValueError('Not found. ({})'.format(txt))