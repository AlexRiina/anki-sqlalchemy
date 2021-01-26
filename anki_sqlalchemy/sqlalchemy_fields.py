import json
import datetime
from typing import List, Generic, Dict, TypeVar, TYPE_CHECKING

from sqlalchemy import Integer, Text
from sqlalchemy.types import TypeDecorator as _TypeDecorator


T = TypeVar("T")


if TYPE_CHECKING:
    TypeDecorator = _TypeDecorator
else:

    class TypeDecorator(_TypeDecorator, Generic[T]):
        pass


class SpaceList(TypeDecorator[List[str]]):
    impl = Text

    def process_bind_param(self, value, dialect):
        return " " + " ".join(value) + " "

    def process_result_value(self, value, dialect):
        # mutable types sometimes trick sqlalchemy into not saving
        if value.strip():
            return tuple(value.strip().split(" "))
        else:
            return tuple()


class FieldList(TypeDecorator[List[str]]):
    impl = Text

    def process_bind_param(self, value, dialect):
        # anki.utils.joinField
        return "\x1f".join(value)

    def process_result_value(self, value, dialect):
        # anki.utils.splitField
        # mutable types sometimes trick sqlalchemy into not saving
        if value:
            return tuple(value.split("\x1f"))
        else:
            return tuple()


class EpochTimeStamp(TypeDecorator[datetime.datetime]):
    impl = Integer

    def process_bind_param(self, value, dialect):
        return int(value.timestamp())

    def process_result_value(self, value, dialect):
        return datetime.datetime.fromtimestamp(value)


class MilisecondEpochTimeStamp(TypeDecorator[datetime.datetime]):
    impl = Integer

    def process_bind_param(self, value, dialect):
        return int(value.timestamp()) * 1000

    def process_result_value(self, value, dialect):
        return datetime.datetime.fromtimestamp(value / 1000)


class Json(TypeDecorator[Dict]):
    impl = Text

    def process_bind_param(self, value, dialect):
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        return json.loads(value)


class IntEnum(TypeDecorator[T], Generic[T]):
    """
    Enables passing in a Python enum and storing the enum's *value* in the db.
    The default would have stored the enum's *name* (ie the string).

    stolen from https://www.michaelcho.me/article/using-python-enums-in-sqlalchemy-models
    """

    impl = Integer

    def __init__(self, enumtype, *args, **kwargs):
        super(IntEnum, self).__init__(*args, **kwargs)
        self._enumtype = enumtype

    def process_bind_param(self, value, dialect):
        if isinstance(value, int):
            return value

        return value.value

    def process_result_value(self, value, dialect):
        return self._enumtype(value)
