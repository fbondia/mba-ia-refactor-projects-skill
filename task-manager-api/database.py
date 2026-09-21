from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine

db = SQLAlchemy()


def enable_sqlite_foreign_keys():
    if getattr(enable_sqlite_foreign_keys, "registered", False):
        return

    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(connection, _record):
        if connection.__class__.__module__.startswith("sqlite3"):
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    enable_sqlite_foreign_keys.registered = True
