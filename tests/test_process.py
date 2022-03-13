import csv
import logging

from matching.mentor import Mentor
from matching.process import (
    create_participant_list_from_path,
    Mentee,
    create_matches,
    conduct_matching_from_file,
    create_mailing_list,
)


class TestProcess:
    def test_create_mentee_list(self, known_file, test_data_path):
        known_file(test_data_path, "mentee", 50)
        mentees = create_participant_list_from_path(Mentee, test_data_path)
        assert len(mentees) == 50
        assert all(map(lambda role: type(role) is Mentee, mentees))

    def test_create_matches(self, known_file, test_data_path):
        known_file(test_data_path, "mentee", 50)
        known_file(test_data_path, "mentor", 50)
        matches = create_matches(
            create_participant_list_from_path(Mentor, test_data_path),
            create_participant_list_from_path(Mentee, test_data_path),
            {"profession": 4, "grade": 3, "unmatched bonus": 0},
        )
        assert len(matches) == 50
        assert len(matches[0]) == 50

    def test_conduct_matching_from_file(self, known_file, test_data_path):
        known_file(test_data_path, "mentee", 50)
        known_file(test_data_path, "mentor", 50)
        mentors, mentees = conduct_matching_from_file(
            test_data_path,
            [
                {"profession": 4, "grade": 3, "unmatched bonus": 0},
                {"profession": 4, "grade": 3, "unmatched bonus": 50},
                {"profession": 0, "grade": 3, "unmatched bonus": 100},
            ],
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
            [
                {"profession": 4, "grade": 3, "unmatched bonus": 0},
                {"profession": 4, "grade": 3, "unmatched bonus": 50},
                {"profession": 0, "grade": 3, "unmatched bonus": 100},
            ],
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
