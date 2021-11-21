import csv
import logging
import os
import pathlib
from typing import List

import pytest

from matching.mentor import Mentor
from matching.person import Person
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
        )
        assert len(matches) == 50
        assert len(matches[0]) == 50

    def test_conduct_matching_from_file(self, known_file, test_data_path):
        known_file(test_data_path, "mentee", 50)
        known_file(test_data_path, "mentor", 50)
        mentors, mentees = conduct_matching_from_file(test_data_path)
        assert len(mentors) == 50
        assert len(mentees) == 50
        for mentor in mentors:
            assert len(mentor.mentees) > 0
        for mentee in mentees:
            assert len(mentee.mentors) > 0

    def test_conduct_matching_with_unbalanced_inputs(self, test_data_path, known_file):
        known_file(test_data_path, "mentee", 50)
        known_file(test_data_path, "mentor", 35)
        mentors, mentees = conduct_matching_from_file(test_data_path)
        every_mentee_has_a_mentor = list(
            map(lambda mentee: len(mentee.mentors) > 0, mentees)
        )
        logging.debug(
            f"Mentees without a mentor: {every_mentee_has_a_mentor.count(False)}"
        )
        assert all(every_mentee_has_a_mentor)

    @pytest.mark.skipif(
        os.environ.get("TEST") is None, reason="can't put integration data on Github"
    )
    def test_integration_data(self):
        def _unmatchables(list_participants: List[Person]):
            return len(
                [
                    participant
                    for participant in list_participants
                    if participant.has_no_match and len(participant.connections) == 0
                ]
            )

        mentors, mentees = conduct_matching_from_file(
            pathlib.Path(".").absolute() / "integration"
        )
        every_mentee_has_a_mentor = list(
            map(lambda mentee: len(mentee.mentors) > 0, mentees)
        )
        logging.info(
            f"Mentees without a mentor: {every_mentee_has_a_mentor.count(False)}\n"
            f"Mentors without any mentees {list(map(lambda mentor: len(mentor.mentees) > 0, mentors)).count(False)}"
        )
        logging.info(
            f"Total matches made: {sum(map(lambda participant: len(participant.connections), mentees))}"
        )
        logging.info(
            f"Unmatchable mentors: {_unmatchables(mentors)} | mentees: {_unmatchables(mentees)}"
        )
        assert all(every_mentee_has_a_mentor)

    def test_create_mailing_list(self, tmp_path, base_mentee, base_mentor, base_data):
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
