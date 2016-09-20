import sqlite3


class DB():
    
    def __init__(self, db="pyflickr.db"):
        self.db = db
        self.connection = sqlite3.connect(db)
        self.cursor = self.connection.cursor()
    
    def create_table(self):
        with open("db/DDL.sql", "r") as ddl:
            self.connection.execute(ddl.read())
        return
    
    def save_to_db(self, data):
        self.create_table()
        for metadata in data:
            query = "REPLACE INTO pyflickr (%s) values (%s)" % (', '.join(metadata.keys()), ', '.join('?' * len(metadata)))
            self.cursor.execute(query, metadata.values())
        self.connection.commit()
        self.connection.close()
