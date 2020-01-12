import managers


class Game:
    def __init__(self):
        self._score = 0
        self._best_score = 0
        self._fruits_missed = 0
        self._critical_combo_num = 0

    def reload(self):
        self.score = 0
        self.best_score = managers.DatabaseManager.get_instance().get_best_score()
        self.fruits_missed = 0
        self.critical_combo = 0

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        self._score = value

    @property
    def best_score(self):
        return self._best_score

    @best_score.setter
    def best_score(self, value):
        self._best_score = value

    @property
    def fruits_missed(self):
        return self._fruits_missed

    @fruits_missed.setter
    def fruits_missed(self, value):
        self._fruits_missed = value

    @property
    def critical_combo(self):
        return self._critical_combo_num

    @critical_combo.setter
    def critical_combo(self, value):
        self._critical_combo_num = value
