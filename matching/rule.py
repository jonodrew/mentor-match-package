from abc import ABC, abstractmethod

from matching.match import Match


class AbstractRule(ABC):
    @abstractmethod
    def apply(self, match_object: Match) -> int:
        raise NotImplementedError


class Rule(AbstractRule):
    def apply(self, match_object: Match) -> int:
        return 0
