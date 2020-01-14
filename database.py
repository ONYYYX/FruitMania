import sqlite3
import config


class Database:
    def __init__(self):
        self.connection: sqlite3.Connection = sqlite3.connect(config.database)
        self.cursor: sqlite3.Cursor = self.connection.cursor()

    def get_best_score(self, mode) -> int:
        score = self.cursor.execute('SELECT MAX(score) FROM scores WHERE mode=?', (mode, )).fetchone()[0]
        if score is None:
            score = 0
        return score

    def add_score(self, score, mode) -> None:
        self.cursor.execute('INSERT INTO scores (score, mode) VALUES (?, ?)', (score, mode))
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()
