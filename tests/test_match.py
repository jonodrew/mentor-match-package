import functools
from unittest.mock import Mock

import matching.rules.rule as rules
from matching.match import Match
from matching.mentor import Mentor
from matching.mentee import Mentee
from matching.person import GRADES
import pytest


class TestMatch:
    new_match = functools.partial(
        Match, weightings={"profession": 4, "grade": 3, "unmatched bonus": 0}
    )

    def test_cant_match_with_same_department(
        self, base_mentee: Mentee, base_mentor: Mentor
    ):
        base_mentee.department = base_mentor.department = "Department of Fun"
        match = TestMatch.new_match(mentor=base_mentor, mentee=base_mentee)
        match.calculate_match()
        assert match.disallowed

    @pytest.mark.parametrize("mentee_grade", [grade for grade in GRADES])
    @pytest.mark.parametrize("mentor_grade", [grade for grade in GRADES])
    def test_cant_match_with_greater_than_two_grade_difference(
        self, base_mentee, base_mentor, mentee_grade, mentor_grade
    ):
        base_mentee.grade = mentee_grade
        base_mentor.grade = mentor_grade

        match = TestMatch.new_match(mentor=base_mentor, mentee=base_mentee)
        match.calculate_match()
        grade_diff = base_mentor.grade - base_mentee.grade
        if not (2 >= grade_diff > 0):
            assert match.disallowed
        else:
            assert not match.disallowed

    def test_matching_profession_scores_four_points(self, base_mentor, base_mentee):
        base_mentor.department = "Department of Sad"
        match = TestMatch.new_match(mentor=base_mentor, mentee=base_mentee)
        rule = Mock(spec=rules.Equivalent)
        rule.apply.return_value = 4
        match.rules = [rule]
        match.calculate_match()
        assert match.score == 4

    def test_mark_successful(self, base_mentee, base_mentor):
        match = TestMatch.new_match(mentor=base_mentor, mentee=base_mentee)
        match.mark_successful()
        assert base_mentor in base_mentee.mentors
        assert base_mentee in base_mentor.mentees

    def test_cant_match_with_self(self, base_mentee, base_data):
        mentor = Mentor(**base_data)
        match = TestMatch.new_match(mentor=mentor, mentee=base_mentee)
        match.calculate_match()
        assert match.disallowed

    def test_cant_match_with_someone_already_matched_with(
        self, base_mentee, base_mentor
    ):
        base_mentor.mentees.append(base_mentee)
        test_match = TestMatch.new_match(mentor=base_mentor, mentee=base_mentee)
        test_match.calculate_match()
        assert test_match.disallowed
