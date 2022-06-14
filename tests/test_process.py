import csv
import logging
from unittest.mock import patch

import matching.rules.rule as rl
from matching.mentor import Mentor
from matching.process import (
    create_participant_list_from_path,
    Mentee,
    create_matches,
    conduct_matching_from_file,
    create_mailing_list,
    generate_match_matrix,
    process_with_minimum_matching,
)


class TestProcess:
    default_rules = [
        rl.Generic(
            {True: 3, False: 0},
            lambda match: match.mentee.organisation != match.mentor.organisation,
        ),
        rl.UnmatchedBonus(5),
    ]

    def test_create_mentee_list(self, known_file, test_data_path):
        known_file(test_data_path, "mentee", 50)
        mentees = create_participant_list_from_path(Mentee, test_data_path)
        assert len(mentees) == 50
        assert all(map(lambda role: type(role) is Mentee, mentees))

    def test_create_matches(self, known_file, test_data_path):
        known_file(test_data_path, "mentee", 50)
        known_file(test_data_path, "mentor", 50)
        matches = create_matches(
            generate_match_matrix(
                create_participant_list_from_path(Mentor, test_data_path),
                create_participant_list_from_path(Mentee, test_data_path),
                self.default_rules,
            )
        )
        assert len(matches) == 50
        assert len(matches[0]) == 50

    def test_conduct_matching_from_file(self, known_file, test_data_path):
        known_file(test_data_path, "mentee", 50)
        known_file(test_data_path, "mentor", 50)
        mentors, mentees = conduct_matching_from_file(
            test_data_path,
            [self.default_rules],
        )
        assert len(mentors) == 50
        assert len(mentees) == 50
        for mentor in mentors:
            assert len(mentor.mentees) > 0
        for mentee in mentees:
            assert len(mentee.mentors) > 0

    def test_conduct_matching_with_unbalanced_inputs(self, test_data_path, known_file):
        known_file(test_data_path, "mentee", 50)
        known_file(test_data_path, "mentor", 35)
        mentors, mentees = conduct_matching_from_file(
            test_data_path,
            [self.default_rules, self.default_rules, self.default_rules],
        )
        every_mentee_has_a_mentor = list(
            map(lambda mentee: len(mentee.mentors) > 0, mentees)
        )
        logging.debug(
            f"Mentees without a mentor: {every_mentee_has_a_mentor.count(False)}"
        )
        assert all(every_mentee_has_a_mentor)

    def test_create_mailing_list(self, tmp_path, base_mentee, base_mentor):
        mentors = [base_mentor]
        for mentor in mentors:
            mentor.mentees.extend([base_mentee for _ in range(3)])
        create_mailing_list(mentors, tmp_path)
        assert tmp_path.joinpath("mentors-list.csv").exists()
        with open(tmp_path.joinpath("mentors-list.csv"), "r") as test_mentors_file:
            file_reader = csv.reader(test_mentors_file)
            assert {"match 1 email", "match 2 email", "match 3 email"}.issubset(
                set(next(file_reader))
            )

    def test_create_mailing_list_when_mentor_has_no_matches(
        self, base_mentor, base_mentee, tmp_path
    ):
        mentors = [base_mentor, base_mentor]
        mentors[0].mentees.extend([base_mentee for _ in range(3)])
        create_mailing_list(mentors, tmp_path)
        with open(tmp_path.joinpath("mentors-list.csv"), "r") as test_mentors_file:
            file_reader = csv.reader(test_mentors_file)
            assert {"match 1 email", "match 2 email", "match 3 email"}.issubset(
                set(next(file_reader))
            )


class TestProcessWithMinimumMatching:
    def test_doesnt_run_forever(self, test_participants):
        """
        This tests that, when the percentage remains stubbornly low, the system will fail gracefully
        """
        mentors, mentees = test_participants()
        with patch(
            "matching.process.calculate_percentage_mentees_matched", return_value=0.0
        ):
            output = process_with_minimum_matching(
                1.0,
                mentors,
                mentees,
                [
                    [
                        rl.Generic(
                            {True: 3, False: 0},
                            lambda match: match.mentee.profession
                            == match.mentor.profession,
                        )
                    ]
                    for _ in range(3)
                ],
            )
            assert output == (mentors, mentees)
