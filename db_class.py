import sqlite3


class DB():
    def __init__(self):
        self.db_conn = sqlite3.connect('db.db', check_same_thread=False)
    
    def fast_query(self, query, params=()):
        cursor = self.cursor()
        cursor.execute(query, params)
        self.commit()
    
    def cursor(self):
        return self.db_conn.cursor()
    
    def select(self, query, params=()):
        cursor = self.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()
    
    def commit(self):
        return self.db_conn.commit()
    
    def fetchall(self):
        return self.db_conn.fetchall()