import logging
from typing import TYPE_CHECKING, List, Dict, Optional
from matching.rules import rule as rl

if TYPE_CHECKING:
    from matching.mentor import Mentor
    from matching.mentee import Mentee


class Match:
    """
    This is the class that calculates the score of each Match.

    As of v4, it requires a list of `Rule` objects that will
    determine the score. This object has two Rules built in: one to disqualify mentors and mentees being matched when
    they're the same people (as people may sign up as both), and one that disqualifies if they've previously been
    matched
    """

    def __init__(
        self,
        mentor: "Mentor",
        mentee: "Mentee",
        weightings: Dict[str, int],
        rules: Optional[List["rl.Rule"]],
    ):
        self.weightings = weightings
        self.mentee = mentee
        self.mentor = mentor
        self._disallowed: bool = False
        self._score: int = 0
        self.rules = [
            rl.Disqualify(lambda match: match.mentor.email == match.mentee.email),
            rl.Disqualify(
                lambda match: match.mentor in match.mentee.mentors
                or match.mentee in match.mentor.mentees
            ),
        ]
        if rules:
            self.rules.extend(rules)

    @property
    def score(self):
        if self._disallowed:
            return 0
        else:
            return self._score

    @score.setter
    def score(self, new_value: int):
        self._score += new_value

    @property
    def disallowed(self):
        return self._disallowed

    @disallowed.setter
    def disallowed(self, new_value: bool):
        if self._disallowed is False and new_value is True:
            self._disallowed = new_value

    def calculate_match(self) -> "Match":
        """
        This method calculates the score for this Match object. It does this by applying the functions below. If at any
        point the match becomes disallowed, the loop breaks. Note that if the match is disallowed, the score property
        always returns 0. One complete, it returns the object
        """
        while not self.disallowed and self.rules:
            rule = self.rules.pop()
            self.score += rule.apply(self)
        return self

    def mark_successful(self):
        if not self.disallowed:
            self.mentor.mentees.append(self.mentee)
            self.mentee.mentors.append(self.mentor)
        else:
            logging.debug("Skipping this match as disallowed")
