import operator
from abc import ABC, abstractmethod
from typing import Callable, Dict, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from matching.match import Match


class AbstractRule(ABC):
    @abstractmethod
    def apply(self, match_object: "Match") -> int:
        raise NotImplementedError


class Rule(AbstractRule):
    def __init__(self, score_dict: Union[Dict[bool, int], None] = None):
        if score_dict is None:
            score_dict = {True: 0, False: 0}
        self.results = score_dict

    def apply(self, match_object: "Match") -> int:
        return self.results.get(self.evaluate(match_object), False)

    @abstractmethod
    def evaluate(self, match_object: "Match") -> bool:
        raise NotImplementedError


class UnmatchedBonus(Rule):
    def __init__(self, unmatched_bonus: int):
        super(UnmatchedBonus, self).__init__({True: unmatched_bonus, False: 0})

    def evaluate(self, match_object: "Match") -> bool:
        return any(
            map(
                lambda participant: len(participant.connections) == 0,
                (match_object.mentee, match_object.mentor),
            )
        )


class Grade(Rule):
    def __init__(
        self,
        target_diff: int,
        logical_operator: Callable[[int, int], bool],
        score_dict: Union[Dict[bool, int], None] = None,
    ):
        super(Grade, self).__init__(score_dict)
        self.target_diff = target_diff
        self.operator = logical_operator

    def evaluate(self, match_object: "Match") -> bool:
        return self.operator(
            (match_object.mentor.grade - match_object.mentee.grade), self.target_diff
        )


class Equivalent(Rule):
    def __init__(self, attribute: str, score_dict: Union[Dict[bool, int], None] = None):
        super(Equivalent, self).__init__(score_dict)
        self.attribute = attribute

    def evaluate(self, match_object: "Match") -> bool:
        participants = (match_object.mentor, match_object.mentee)
        attrs = map(
            lambda participant: participant.__getattribute__(self.attribute),
            participants,
        )
        return operator.eq(*attrs)


class Generic(Rule):
    def __init__(
        self,
        score_dict: Union[Dict[bool, int], None],
        evaluation_func: Callable[["Match"], bool],
    ):
        super(Generic, self).__init__(score_dict)
        self._evaluate = evaluation_func

    def evaluate(self, match_object: "Match") -> bool:
        return self._evaluate(match_object)


class Disqualify(Generic):
    """
    A disqualifying rule is a kind of anti-rule. Here, we pass a condition which, if it evaluates to `True`, should
    disqualify a `Match` rather than increase its score.
    """

    def __init__(self, disqualifying_condition: Callable[["Match"], bool]):
        super(Disqualify, self).__init__(None, disqualifying_condition)

    def apply(self, match_object: "Match") -> int:
        match_object.disallowed = self.evaluate(match_object)
        return 0
