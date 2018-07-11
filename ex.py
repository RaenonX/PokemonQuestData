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
        return int(EnumWithName.str_get_enum(txt))

    @classmethod
    def int_get_str(cls, num):
        for item in cls:
            if int(item) == num:
                return str(item)

    @classmethod
    def str_get_enum(cls, txt):
        for item in cls:
            if str(item) == txt:
                return item

        raise ValueError('Not found. ({})'.format(txt))

    @classmethod
    def get_choices(cls):
        return [(int(s), str(s)) for s in cls]