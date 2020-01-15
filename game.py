import managers


class Game:
    def __init__(self):
        self._score = 0
        self._best_score = 0
        self._fruits_missed = 0
        self._critical_combo_num = 0
        self._freeze = False
        self._blitz = False
        self._double = False

    def reload(self, mode) -> None:
        self.score = 0
        self.best_score = managers.DatabaseManager.get_instance().get_best_score(mode)
        self.fruits_missed = 0
        self.critical_combo = 0
        self.freeze = False
        self.blitz = False
        self.double = False

    @property
    def freeze(self):
        return self._freeze

    @freeze.setter
    def freeze(self, value):
        self._freeze = value

    @property
    def blitz(self):
        return self._blitz

    @blitz.setter
    def blitz(self, value):
        self._blitz = value

    @property
    def double(self):
        return self._double

    @double.setter
    def double(self, value):
        self._double = value

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        n = value - self._score
        if self.double:
            n *= 2
        self._score += n

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
