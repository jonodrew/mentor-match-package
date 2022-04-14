import functools
import operator

import matching.rules.rule as rl
from matching.match import Match
from matching.mentor import Mentor
from matching.mentee import Mentee
from matching.person import GRADES
import pytest


class TestMatch:
    new_match = functools.partial(
        Match, weightings={"profession": 4, "grade": 3, "unmatched bonus": 0}
    )

    @pytest.mark.integration
    def test_cant_match_with_same_department(
        self, base_mentee: Mentee, base_mentor: Mentor
    ):
        base_mentee.department = base_mentor.department = "Department of Fun"
        match = TestMatch.new_match(
            mentor=base_mentor,
            mentee=base_mentee,
            rules=[
                rl.Disqualify(rl.Equivalent("department", {True: 0, False: 0}).evaluate)
            ],
        )
        match.calculate_match()
        assert match.disallowed

    @pytest.mark.integration
    @pytest.mark.parametrize("mentee_grade", [grade for grade in GRADES])
    @pytest.mark.parametrize("mentor_grade", [grade for grade in GRADES])
    def test_cant_match_with_greater_than_two_grade_difference(
        self, base_mentee, base_mentor, mentee_grade, mentor_grade
    ):
        base_mentee.grade = mentee_grade
        base_mentor.grade = mentor_grade

        base_mentee.email = "mentee"
        base_mentor.email = "mentor"

        match = TestMatch.new_match(
            mentor=base_mentor,
            mentee=base_mentee,
            rules=[
                rl.Disqualify(
                    rl.Grade(target_diff=2, logical_operator=operator.gt).evaluate
                ),
                rl.Disqualify(
                    rl.Grade(target_diff=0, logical_operator=operator.le).evaluate
                ),
            ],
        )
        match.calculate_match()
        grade_diff = base_mentor.grade - base_mentee.grade
        if not (2 >= grade_diff > 0):
            assert match.disallowed
        else:
            assert not match.disallowed

    def test_mark_successful(self, base_mentee, base_mentor):
        match = TestMatch.new_match(mentor=base_mentor, mentee=base_mentee, rules=[])
        match.mark_successful()
        assert base_mentor in base_mentee.mentors
        assert base_mentee in base_mentor.mentees

    def test_cant_match_with_self(self, base_mentee, base_data):
        mentor = Mentor(**base_data)
        mentor.email = base_mentee.email = "same@email.com"
        match = TestMatch.new_match(mentor=mentor, mentee=base_mentee, rules=[])
        match.calculate_match()
        assert match.disallowed

    def test_cant_match_with_someone_already_matched_with(
        self, base_mentee, base_mentor
    ):
        base_mentor.mentees.append(base_mentee)
        test_match = TestMatch.new_match(
            mentor=base_mentor, mentee=base_mentee, rules=[]
        )
        test_match.calculate_match()
        assert test_match.disallowed
