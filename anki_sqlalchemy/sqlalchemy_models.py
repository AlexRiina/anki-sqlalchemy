import datetime
import enum

from sqlalchemy import func, Column, DateTime, ForeignKey, Index, Integer, Text, type_coerce
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from . import sqlalchemy_fields

Base = declarative_base()
metadata = Base.metadata


@enum.unique
class CardType(enum.IntEnum):
    new = 0
    learning = 1
    due = 2
    relearning = 3


class QueueType(enum.IntFlag):
    user_burried = -3
    schedule_burried = -2
    burried = -2
    suspended = -1
    new = 0
    learning = 1
    due = 2
    delayed_learning = 3


@enum.unique
class FlagColor(enum.IntFlag):
    none = 0
    red = 1
    orange = 2
    green = 3
    blue = 4


@enum.unique
class GraveType(enum.IntEnum):
    card = 0
    note = 1
    deck = 2


@enum.unique
class ReviewType(enum.IntEnum):
    learn = 0
    review = 1
    relearn = 2
    cram = 3
    manual = 4


class _UndoableMixin:
    update_sequence_number = Column("usn", Integer, nullable=False, index=True)
    modification_time = Column("mtime_secs", sqlalchemy_fields.EpochTimeStamp, nullable=False)


class _OldUndoableMixin:
    update_sequence_number = Column("usn", Integer, nullable=False, index=True)
    modification_time = Column("mod", sqlalchemy_fields.EpochTimeStamp, nullable=False)


class _TimestampIdMixin:
    @hybrid_property
    def creation_time(self):
        return datetime.datetime.fromtimestamp(self.id / 1000)

    @creation_time.expression  # noqa
    def creation_time(self):
        return type_coerce(func.datetime(self.id / 1000, 'unixepoch'), DateTime())


class Card(_OldUndoableMixin, _TimestampIdMixin, Base):
    __tablename__ = "cards"
    __table_args__ = (Index("ix_cards_sched", "did", "queue", "due"),)

    id = Column(Integer, primary_key=True)
    note_id = Column("nid", Integer, ForeignKey("notes.id"), nullable=False, index=True)
    deck_id = Column("did", Integer, ForeignKey("decks.id"), nullable=False)
    ordinal = Column("ord", Integer, nullable=False)
    type = Column(
        sqlalchemy_fields.IntEnum[CardType](CardType),
        nullable=False,
        default=CardType.new,
    )
    queue = Column(
        sqlalchemy_fields.IntEnum[QueueType](QueueType),
        nullable=False,
        default=QueueType.new,
    )

    # Due is used differently for different card types:
    #   new: note id or random int
    #   due: integer day, relative to the collection's creation time
    #   learning: integer timestamp
    due = Column(Integer, nullable=False)

    # interval (used in SRS algorithm). Negative = seconds, positive = days
    interval = Column("ivl", Integer, nullable=False, default=0)

    # The ease factor of the card in permille (parts per thousand). If the ease
    # factor is 2500, the card’s interval will be multiplied by 2.5 the next
    # time you press Good.
    factor = Column(Integer, nullable=False, default=0)
    review_count = Column("reps", Integer, nullable=False, default=0)
    lapse_count = Column("lapses", Integer, nullable=False, default=0)
    left = Column(Integer, nullable=False, default=0)
    original_due = Column("odue", Integer, nullable=False, default=0)
    original_deck_id = Column("odid", Integer, nullable=False, default=0)
    flags = Column(
        sqlalchemy_fields.IntEnum[FlagColor](FlagColor), nullable=False, default=0
    )
    data = Column(Text, nullable=False)  # unused

    deck = relationship("Deck")
    note = relationship("Note")
    reviews = relationship("RevLog", uselist=True, order_by="RevLog.update_sequence_number")

    @hybrid_property
    def is_burried(self):
        return self.queue == QueueType.burried

    @hybrid_property
    def is_review(self):
        return self.queue == QueueType.due

    @hybrid_property
    def is_mature(self):
        return self.is_review and self.interval >= 21

    @hybrid_property
    def is_young(self):
        return self.is_review and self.interval < 21


class Collection(Base):
    __tablename__ = "col"

    id = Column(Integer, primary_key=True)
    crt = Column(Integer, nullable=False)
    mod = Column(Integer, nullable=False)
    scm = Column(Integer, nullable=False)
    ver = Column(Integer, nullable=False)
    dty = Column(Integer, nullable=False)
    usn = Column(Integer, nullable=False)
    ls = Column(Integer, nullable=False)

    # deprecated and moved to their own tables
    # conf = Column(sqlalchemy_fields.Json, nullable=False)
    # models = Column(sqlalchemy_fields.Json, nullable=False)
    # decks = Column(sqlalchemy_fields.Json, nullable=False)
    # dconf = Column(Text, nullable=False)
    # tags = Column(Text, nullable=False)


class NoteType(_UndoableMixin, Base):
    __tablename__ = "notetypes"

    id = Column(Integer, primary_key=True)
    name = Column("name", Text, nullable=False)
    config = Column(Text, nullable=False)

    notes = relationship("Note", uselist=True)
    fields = relationship("Field", uselist=True)
    template = relationship("Template", uselist=True)

    def __repr__(self):
        return f"<{self.name}: {self.id}>"


class Grave(Base):
    __tablename__ = "graves"

    # unenforced primary key
    original_id = Column("oid", Integer, nullable=False, primary_key=True)
    type = Column(
        sqlalchemy_fields.IntEnum[GraveType](GraveType),
        nullable=False,
        primary_key=True,
    )

    update_sequence_number = Column("usn", Integer, nullable=False)


class Note(_OldUndoableMixin, _TimestampIdMixin, Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True)
    guid = Column(Text, nullable=False)
    # note that while this is an integer, it is often used as a string in code,
    # e.g. in Collect.models
    note_type_id = Column("mid", Integer, ForeignKey("notetypes.id"), nullable=False)

    tags = Column(sqlalchemy_fields.SpaceList, nullable=False)
    fields = Column("flds", sqlalchemy_fields.FieldList, nullable=False)
    sort_field = Column("sfld", Integer, nullable=False)
    checksum = Column("csum", Integer, nullable=False, index=True)
    flags = Column(Integer, nullable=False)  # unused
    data = Column(Text, nullable=False)  # unused

    cards = relationship("Card", uselist=True)
    note_type = relationship("NoteType")


class RevLog(_TimestampIdMixin, Base):
    __tablename__ = "revlog"

    id = Column(Integer, primary_key=True)
    card_id = Column("cid", Integer, ForeignKey("cards.id"), nullable=False, index=True)
    update_sequence_number = Column("usn", Integer, nullable=False, index=True)
    ease = Column(Integer, nullable=False)
    interval = Column("ivl", Integer, nullable=False)
    last_interval = Column("lastIvl", Integer, nullable=False)
    factor = Column(Integer, nullable=False)
    time = Column(Integer, nullable=False)  # milliseconds
    type = Column(
        sqlalchemy_fields.IntEnum[ReviewType](ReviewType),
        nullable=False,
    )

    card = relationship("Card")


class Field(Base):
    __tablename__ = "fields"

    # NOTE: these are not real primary keys, but there is a unique constraint
    # and sqlalchemy has trouble with tables that don't have primary keys
    note_type_id = Column("ntid", Integer, ForeignKey("notetypes.id"), nullable=False, index=True, primary_key=True)
    name = Column(Text, nullable=False, primary_key=True)
    config = Column(Text, nullable=False)
    ordinal = Column("ord", Integer, nullable=False)

    note_type = relationship("NoteType")

    def __repr__(self):
        return f"<{self.name}: {self.note_type_id}>"


class Template(_UndoableMixin, Base):
    __tablename__ = "templates"

    name = Column(Text, nullable=False)
    note_type_id = Column("ntid", Integer, ForeignKey("notetypes.id"), nullable=False, index=True, primary_key=True)
    ordinal = Column("ord", Integer, nullable=False, primary_key=True)
    config = Column(Text, nullable=False)

    note_type = relationship("NoteType")

    def __repr__(self):
        return f"<{self.name}>"


class Deck(_UndoableMixin, Base):
    __tablename__ = "decks"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    common = Column()
    kind = Column()

    cards = relationship("Card", uselist=True)

    def __repr__(self):
        return f"<{self.name}: {self.id}>"



class DeckConfig(_UndoableMixin, Base):
    __tablename__ = "deck_config"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    config = Column(Text, nullable=False)

    def __repr__(self):
        return f"<{self.name}: {self.id}>"


class Config(_UndoableMixin, Base):
    __tablename__ = "config"

    key = Column(Text, primary_key=True)
    value = Column('val', sqlalchemy_fields.Json, nullable=False)

    def __repr__(self):
        return f"<{self.key}>"


class Tag(Base):
    __tablename__ = "tags"

    tag = Column(Text, primary_key=True)
    update_sequence_number = Column("usn", Integer, nullable=False)

    def __repr__(self):
        return f"<{self.tag}>"
