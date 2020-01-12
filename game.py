class Game:
    def __init__(self):
        self._score = 0
        self._bombs_exploded = 0
        self._critical_combo_num = 0

    def reload(self):
        self.score = 0
        self.bombs_exploded = 0
        self.critical_combo = 0

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        self._score = value

    @property
    def bombs_exploded(self):
        return self._bombs_exploded

    @bombs_exploded.setter
    def bombs_exploded(self, value):
        self._bombs_exploded = value

    @property
    def critical_combo(self):
        return self._critical_combo_num

    @critical_combo.setter
    def critical_combo(self, value):
        self._critical_combo_num = value
