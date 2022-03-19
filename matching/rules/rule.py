import operator
from abc import ABC, abstractmethod
from typing import Callable, Dict

from matching.match import Match


class AbstractRule(ABC):
    @abstractmethod
    def apply(self, match_object: Match) -> int:
        raise NotImplementedError


class Rule(AbstractRule):
    def __init__(self, score_dict: Dict[bool, int]):
        self.results = score_dict

    def apply(self, match_object: Match) -> int:
        return self.results.get(self.evaluate(match_object), False)

    @abstractmethod
    def evaluate(self, match_object: Match) -> bool:
        raise NotImplementedError


class Grade(Rule):
    def __init__(
        self,
        score_dict: Dict[bool, int],
        target_diff: int,
        logical_operator: Callable[[int, int], bool],
    ):
        super(Grade, self).__init__(score_dict)
        self.target_diff = target_diff
        self.operator = logical_operator

    def evaluate(self, match_object: Match) -> bool:
        return self.operator(
            (match_object.mentor.grade - match_object.mentee.grade), self.target_diff
        )


class Equivalent(Rule):
    def __init__(self, score_dict: Dict[bool, int], attribute: str):
        super(Equivalent, self).__init__(score_dict)
        self.attribute = attribute

    def evaluate(self, match_object: Match) -> bool:
        participants = (match_object.mentor, match_object.mentee)
        attrs = map(
            lambda participant: participant.__getattribute__(self.attribute),
            participants,
        )
        return operator.eq(*attrs)


class Disqualify(AbstractRule):
    """
    A disqualifying rule is a kind of anti-rule. Here, we pass a condition which, if it evaluates to `True`, should
    disqualify a `Match` rather than increase its score.
    """

    def __init__(self, disqualifying_condition: Callable[[Match], bool]):
        self.condition = disqualifying_condition

    def apply(self, match_object: Match) -> int:
        if self.condition(match_object):
            match_object.disallowed = True
        return 0
