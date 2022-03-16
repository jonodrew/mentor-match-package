import csv
import functools
import os
import pathlib
import sys
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


def transpose_matrix(matrix):
    return [list(row) for row in zip(*matrix)]


def create_matches(
    preliminary_matches: List[List[Match]],
) -> List[List[Match]]:
    """
    Create a preliminary grid of matches and then strip out folks who have zero potential matches.
    :param: preliminary_matches:
    :return:
    """

    def _at_least_one_match(row: List[Match]) -> bool:
        return not all(match.disallowed for match in row)

    good_mentees = [row for row in preliminary_matches if _at_least_one_match(row)]
    good_mentors = [
        row for row in transpose_matrix(good_mentees) if _at_least_one_match(row)
    ]
    return transpose_matrix(good_mentors)


def prepare_matrix(matches: List[List[Match]]) -> Matrix:
    prepared_matrix = make_cost_matrix(
        matches,
        lambda match: sys.maxsize - match.score,
    )
    return prepared_matrix


def calculate_matches(prepared_matrix: Matrix):
    algorithm = Munkres()
    return algorithm.compute(prepared_matrix)


def match_and_assign_participants(
    good_matches: List[List[Match]],
) -> List[List[Match]]:
    for successful_match in calculate_matches(prepare_matrix(good_matches)):
        match = good_matches[successful_match[0]][successful_match[1]]
        match.mark_successful()
    return good_matches


def process_data(
    mentors: List[Mentor], mentees: List[Mentee], weightings_list: List[Dict[str, int]]
) -> Tuple[List[Mentor], List[Mentee]]:
    """
    This is the main entrypoint for this software. It lazily generates three matrices, which allows for them to be
    mutated over the course of the matching process.
    :param mentors:
    :param mentees:
    :param weightings_list:
    :return:
    """
    matrices = map(
        functools.partial(generate_match_matrix, mentors, mentees), weightings_list
    )
    for matrix in matrices:
        match_and_assign_participants(matrix)
    return mentors, mentees


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
