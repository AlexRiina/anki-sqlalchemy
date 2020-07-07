Anki SQLAlchemy is an interface for interacting with the
[Anki](https://apps.ankiweb.net/) sqlite database from python without having to
either hack an Anki install or figure out the database structure and field
serialization from scratch.

Here is a small code snippet written first without `anki_sqlalchemy` to show
how unintuivite the data format and columns names are without an wrapper.

```python
import sqlite3

conn = sqlite3.connect('backup.db')
cursor = conn.execute("SELECT id, tags FROM notes WHERE mod >= ?", [1445394366])
note = cursor.fetchone()
note[0]  # 1428143940996
note[1]  # ' edit math probability wikipedia '

cursor = conn.execute("SELECT mod, type FROM cards WHERE nid = ?", [nid])
card = cursor.fetchone()
card[0]  # 1445394366
card[1]  # 2
```

```python
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from anki_sqlalchemy.sqlalchemy_models import Card

engine = create_engine("sqlite:///backup.db", echo=True)
Session = sessionmaker(bind=engine)
session = Session()

note = session.query(Note).filter(Note.modification_time >= datetime.datetime(2017, 2, 5, 21, 29, 49)).first()
note.id  # 1428143940996
note.modification_time  # datetime.datetime(2017, 2, 5, 21, 29, 49)

card = note.cards[0]
card.modification_time  # datetime.datetime(2019, 11, 5, 22, 23, 3)
card.type  # <CardType.due: 2>
```
