import operator
from unittest.mock import Mock

from matching.rules import rule as rl
from matching.match import Match
import pytest


@pytest.fixture(scope="function")
def test_match(base_mentor, base_mentee):
    return Match(base_mentor, base_mentee, weightings={}, rules=[])


class TestRules:
    def test_matching_scores_scores_correct_points(self, test_match):
        profession_rule = rl.Equivalent({True: 4, False: 0}, "profession")
        assert profession_rule.apply(test_match) == 4

    @pytest.mark.parametrize("mentee_grade", [grade for grade in range(11)])
    @pytest.mark.parametrize("mentor_grade", [grade for grade in range(11)])
    def test_disqualify_on_large_grade_gap(
        self, test_match, mentor_grade, mentee_grade
    ):
        test_match = Mock()
        test_match.mentor.grade = mentor_grade
        test_match.mentee.grade = mentee_grade
        grade_diff = mentor_grade - mentee_grade
        test_match.disallowed = False
        dq_rule = rl.Disqualify(rl.Grade({True: 0, False: 0}, 3, operator.ge).evaluate)
        dq_rule.apply(test_match)
        if grade_diff > 2:
            assert test_match.disallowed
        else:
            assert not test_match.disallowed

    @pytest.mark.parametrize("mentee_grade", [grade for grade in range(11)])
    @pytest.mark.parametrize("mentor_grade", [grade for grade in range(11)])
    def test_grade_rule(self, test_match, mentor_grade, mentee_grade):
        test_match = Mock()
        test_match.mentor.grade = mentor_grade
        test_match.mentee.grade = mentee_grade
        grade_diff = test_match.mentor.grade - test_match.mentee.grade
        rules = [
            rl.Grade({True: 2, False: 0}, target_diff=1, logical_operator=operator.eq),
            rl.Grade({True: 4, False: 0}, target_diff=2, logical_operator=operator.eq),
        ]
        score = sum(map(lambda rule: rule.apply(test_match), rules))
        if grade_diff == 1:
            assert score == 2
        elif grade_diff == 2:
            assert score == 4
        else:
            assert score == 0
