import sqlite3


class DB():
    
    def __init__(self, db="pyflickr.db"):
        self.db = db

    def create_table(self):
        with sqlite3.connect(self.db) as connection:
            with open("db/DDL.sql", "r") as ddl:
                connection.execute(ddl.read())
        return
    
    def save_to_db(self, data):
        with sqlite3.connect(self.db) as connection:
            cursor = connection.cursor()
            query = "REPLACE INTO pyflickr (%s) values (%s)" % (', '.join(data.keys()), ', '.join('?' * len(data)))
            cursor.execute(query, data.values())
        return None
