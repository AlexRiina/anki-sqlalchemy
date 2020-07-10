import enum

from sqlalchemy import Column, ForeignKey, Index, Integer, Text
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
class ReviewwType(enum.IntEnum):
    learn = 0
    review = 1
    relearn = 2
    cram = 3


class Card(Base):
    __tablename__ = "cards"
    __table_args__ = (Index("ix_cards_sched", "did", "queue", "due"),)

    id = Column(Integer, primary_key=True)
    note_id = Column("nid", Integer, ForeignKey("notes.id"), nullable=False, index=True)
    deck_id = Column("did", Integer, nullable=False)
    ordinal = Column("ord", Integer, nullable=False)
    modification_time = Column("mod", sqlalchemy_fields.EpochTimeStamp, nullable=False)
    update_sequence_number = Column("usn", Integer, nullable=False, index=True)
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

    note = relationship("Note")

    @hybrid_property
    def burried(self):
        return self.queue == QueueType.burried


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
    conf = Column(sqlalchemy_fields.Json, nullable=False)
    models = Column(sqlalchemy_fields.Json, nullable=False)
    decks = Column(Text, nullable=False)
    dconf = Column(Text, nullable=False)
    tags = Column(Text, nullable=False)


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


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True)
    guid = Column(Text, nullable=False)
    # note that while this is an integer, it is often used as a string in code,
    # e.g. in Collect.models
    model_id = Column("mid", Integer, nullable=False)
    modification_time = Column("mod", sqlalchemy_fields.EpochTimeStamp, nullable=False)
    update_sequence_number = Column("usn", Integer, nullable=False, index=True)

    tags = Column(sqlalchemy_fields.SpaceList, nullable=False)
    fields = Column("flds", sqlalchemy_fields.FieldList, nullable=False)
    sort_field = Column("sfld", Integer, nullable=False)
    checksum = Column("csum", Integer, nullable=False, index=True)
    flags = Column(Integer, nullable=False)  # unused
    data = Column(Text, nullable=False)  # unused

    cards = relationship("Card", uselist=True)


class RevLog(Base):
    __tablename__ = "revlog"

    id = Column(Integer, primary_key=True)
    cid = Column("cid", Integer, nullable=False, index=True)
    usn = Column("usn", Integer, nullable=False, index=True)
    ease = Column(Integer, nullable=False)
    ivl = Column("ivl", Integer, nullable=False)
    lastIvl = Column("lastIvl", Integer, nullable=False)
    factor = Column(Integer, nullable=False)
    time = Column(Integer, nullable=False)  # milliseconds
    type = Column(Integer, nullable=False)
