from sqlalchemy.engine import CreateEnginePlugin
from sqlalchemy import event
from unidecode import unidecode


class UnicasePlugin(CreateEnginePlugin):
    def engine_created(self, engine):
        @event.listens_for(engine, 'connect')
        def receive_connect(dbapi_connection, connection_record):
            def _compare(x, y):
                print('cmp')
                x_ = unidecode(x).lower()
                y_ = unidecode(y).lower()

                return 1 if x_ > y_ else -1 if x_ < y_ else 0

            dbapi_connection.create_collation("unicase", _compare)
