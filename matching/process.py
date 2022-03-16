import csv
import logging
import os
import pathlib
import sys
from functools import reduce
from pathlib import Path
from typing import Union, Type, List, Dict, Tuple, Generator

from munkres import Munkres, make_cost_matrix, Matrix  # type: ignore

from matching.match import Match
from matching.mentee import Mentee
from matching.mentor import Mentor


def generate_match_matrix(
    mentor_list: List[Mentor],
    mentee_list: List[Mentee],
    weightings: Dict[str, int],
) -> List[List[Match]]:
    return [
        [Match(mentor, mentee, weightings).calculate_match() for mentee in mentee_list]
        for mentor in mentor_list
    ]


def process_form(path_to_form) -> Generator[Dict[str, str], None, None]:
    with open(path_to_form, "r") as data_form:
        file_reader = csv.DictReader(data_form)
        for row in file_reader:
            yield row


def create_participant_list_from_path(
    participant: Union[Type[Mentee], Type[Mentor]], path_to_data: pathlib.Path
):
    path_to_data = path_to_data / f"{participant.__name__.lower()}s.csv"
    return [participant(**row) for row in process_form(path_to_data)]


def _mark_participants_with_no_matches(
    matrix: List[List[Match]], role_as_str: str
) -> None:
    """
    This method goes through every row in the matrix. If the row has no possible matches, then the mentor/mentee in
    that row is marked as `has_no_match`
    :param matrix:
    :param role_as_str:
    :return: None
    """
    for row in matrix:
        if all([match.disallowed for match in row]):
            row[0].__getattribute__(role_as_str).has_no_match = True
            logging.debug(
                f"Participant {row[0].__getattribute__(role_as_str).email} has no"
                " matches"
            )


def create_matches(
    mentor_list: List[Mentor],
    mentee_list: List[Mentee],
    weightings: Dict[str, int],
) -> List[List[Match]]:
    """
    Create a preliminary grid of matches and then strip out folks who have zero potential matches.
    :param mentor_list:
    :param mentee_list:
    :param weightings:
    :return:
    """

    def _can_match(participant: Union[Mentor, Mentee]):
        return not participant.has_no_match

    preliminary_matches = generate_match_matrix(mentor_list, mentee_list, weightings)
    _mark_participants_with_no_matches(preliminary_matches, "mentor")
    _mark_participants_with_no_matches(transpose_matrix(preliminary_matches), "mentee")
    return generate_match_matrix(
        list(filter(_can_match, mentor_list)),
        list(filter(_can_match, mentee_list)),
        weightings,
    )


def prepare_matrix(matches: List[List[Match]]) -> Matrix:
    prepared_matrix = make_cost_matrix(
        matches,
        lambda match: sys.maxsize - match.score,
    )
    return prepared_matrix


def transpose_matrix(matrix):
    return [list(row) for row in zip(*matrix)]


def calculate_matches(prepared_matrix: Matrix):
    algorithm = Munkres()
    return algorithm.compute(prepared_matrix)


def match_and_assign_participants(
    participant_lists: Tuple[List[Mentor], List[Mentee]],
    weightings: Dict[str, int],
) -> Tuple[List[Mentor], List[Mentee]]:
    matches = create_matches(participant_lists[0], participant_lists[1], weightings)
    for successful_match in calculate_matches(prepare_matrix(matches)):
        match = matches[successful_match[0]][successful_match[1]]
        match.mark_successful()
    return participant_lists[0], participant_lists[1]


def process_data(
    mentors: List[Mentor], mentees: List[Mentee], weightings_list: List[Dict[str, int]]
) -> Tuple[List[Mentor], List[Mentee]]:
    return reduce(
        match_and_assign_participants,
        weightings_list,
        (mentors, mentees),
    )


def conduct_matching_from_file(
    path_to_data: Path, weightings_list: [List[Dict[str, int]]]
) -> Tuple[List[Mentor], List[Mentee]]:
    mentors = create_participant_list_from_path(Mentor, path_to_data)
    mentees = create_participant_list_from_path(Mentee, path_to_data)
    return process_data(mentors, mentees, weightings_list)


def create_mailing_list(
    participant_list: List[Union[Mentor, Mentee]], output_folder: Path
):
    """
    This function takes a list of either matched mentors or matched mentees. For each participant, it outputs their
    data and the information of the participants they've been matched with. If a particpant doesn't have the full
    compliment of three matches, the empty spaces are ignored.
    """
    file_name = f"{type(participant_list[0]).__name__.lower()}s-list.csv"
    file = output_folder.joinpath(file_name)
    list_participants_as_dicts = [
        participant.to_dict_for_output() for participant in participant_list
    ]
    field_headings = max(
        list_participants_as_dicts, key=lambda participant: len(participant.keys())
    ).keys()
    try:
        os.mkdir(output_folder)
    except FileExistsError:
        pass
    with open(file, "w", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=list(field_headings))
        writer.writeheader()
        for participant in list_participants_as_dicts:
            writer.writerow(participant)
