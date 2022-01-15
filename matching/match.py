import logging
from typing import TYPE_CHECKING, Callable, List

if TYPE_CHECKING:
    from matching.mentor import Mentor
    from matching.mentee import Mentee


class Match:
    def __init__(self, mentor: "Mentor", mentee: "Mentee", weightings=None):
        self.weightings = (
            {"profession": 4, "grade": 3, "unmatched bonus": 0}
            if weightings is None
            else weightings
        )
        self.mentee = mentee
        self.mentor = mentor
        self._disallowed: bool = False
        self._score: int = 0
        self.calculate_match()

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

    def calculate_match(self) -> None:
        """
        This method calculates the score for this Match object. It does this by applying the functions below. If at any
        point the match becomes disallowed, the loop breaks. Note that if the match is disallowed, the score property
        always returns 0.
        """
        scoring_methods: List[Callable[[], None]] = [
            self.check_not_already_matched,
            self.score_department,
            self.score_grade,
            self.score_profession,
            self.score_unmatched,
        ]
        while not self._disallowed and scoring_methods:
            scoring_method = scoring_methods.pop()
            scoring_method()

    def score_grade(self) -> None:
        """
        If the grade difference is 1 or 2, it's multiplied by the grade weighting and added to the score.
        Otherwise, the match is disallowed.
        """
        grade_diff = self.mentor.grade - self.mentee.grade
        if not (2 >= grade_diff > 0):
            self._disallowed = True
        else:
            self._score += grade_diff * self.weightings["grade"]

    def score_profession(self) -> None:
        """
        If the mentor and mentee are in the same profession, the score is increased by the 'profession' value in the
        weightings dict
        """
        if self.mentee.profession == self.mentor.profession:
            self._score += self.weightings["profession"]

    def score_department(self, same_department_permitted: bool = False) -> None:
        """
        Mentor/mentee matches in the same department default to disallowed
        """
        if (
            self.mentee.department == self.mentor.department
            and not same_department_permitted
        ):
            self._disallowed = True

    def score_unmatched(self) -> None:
        """
        If either the mentor or the mentee in this match has no other matches, increase the score by the unmatched
        bonus in the weightings dict
        """
        if any(
            map(
                lambda participant: len(participant.connections) == 0,
                (self.mentee, self.mentor),
            )
        ):
            self._score += self.weightings.get("unmatched bonus")

    def mark_successful(self):
        if not self.disallowed:
            self.mentor.mentees.append(self.mentee)
            self.mentee.mentors.append(self.mentor)
        else:
            logging.debug("Skipping this match as disallowed")

    def check_not_already_matched(self):
        """
        Mentees/mentors can't be matched if they've already been matched
        """
        if self.mentee in self.mentor.mentees or self.mentor in self.mentee.mentors:
            self._disallowed = True
