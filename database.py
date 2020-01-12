import sqlite3
import config


class Database:
    def __init__(self):
        self.connection: sqlite3.Connection = sqlite3.connect(config.database)
        self.cursor: sqlite3.Cursor = self.connection.cursor()

    def get_best_score(self) -> int:
        return self.cursor.execute('SELECT MAX(score) FROM scores').fetchone()[0]

    def add_score(self, score) -> None:
        self.cursor.execute('INSERT INTO scores (score) VALUES (?)', (score, ))

    def close(self) -> None:
        self.connection.close()
