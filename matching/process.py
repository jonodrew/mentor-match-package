import collections
import csv

import functools
import pathlib
import sys
import copy
from pathlib import Path
from typing import Union, Type, List, Dict, Tuple, Generator, Callable

from munkres import Munkres, make_cost_matrix, Matrix  # type: ignore

import matching.rules.rule as rl
from matching.match import Match
from matching.mentee import Mentee
from matching.mentor import Mentor
from matching.person import Person
from matching.export import ExportToSpreadsheet


def generate_match_matrix(
    mentor_list: List[Mentor], mentee_list: List[Mentee], rules: List[rl.RuleProtocol]
) -> List[List[Match]]:
    return [
        [Match(mentor, mentee, rules).calculate_match() for mentee in mentee_list]
        for mentor in mentor_list
    ]


def process_form(path_to_form) -> Generator[Dict[str, str], None, None]:
    with open(path_to_form, "r") as data_form:
        file_reader = csv.DictReader(data_form)
        for row in file_reader:
            yield row


def create_participant_list_from_path(
    participant: Union[Type[Mentee], Type[Mentor]],
    path_to_data: pathlib.Path,
    mapping_func: Callable[
        [dict[str, str], str], dict[str, str]
    ] = lambda row, name: row,
):
    path_to_data = path_to_data / f"{participant.__str__()}s.csv"
    return [
        participant(**mapping_func(row, participant.__str__()))
        for row in process_form(path_to_data)
    ]


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
    for successful_match_y, successful_match_x in calculate_matches(
        prepare_matrix(good_matches)
    ):
        match = good_matches[successful_match_y][successful_match_x]
        match.mark_successful()
    return good_matches


def process_data(
    mentors: List[Mentor], mentees: List[Mentee], all_rules: List[List[rl.RuleProtocol]]
) -> Tuple[List[Mentor], List[Mentee]]:
    """
    This is the main entrypoint for this software. It lazily generates three matrices, which allows for them to be
    mutated over the course of the matching process.
    :param all_rules:
    :param mentors:
    :param mentees:
    :return:
    """
    matrices = map(
        functools.partial(generate_match_matrix, mentors, mentees),
        all_rules,
    )
    for matrix in matrices:
        match_and_assign_participants(matrix)
    return mentors, mentees


def process_with_minimum_matching(
    acceptable_percentage: float,
    mentors: List[Mentor],
    mentees: List[Mentee],
    all_rules: List[List[rl.Rule]],
):
    current_percentage = 0.0
    unmatched_bonus = 0
    options = []
    Outcome = collections.namedtuple("Outcome", ["participants", "percentage"])
    while current_percentage <= acceptable_percentage and unmatched_bonus < sum(
        [rule.results.get(True) for rule in all_rules[0]]
    ):
        copy_mentors = mentors.copy()
        copy_mentees = mentees.copy()
        all_rules_copy = copy.deepcopy(all_rules)
        for rule_list in all_rules_copy:
            rule_list.append(rl.UnmatchedBonus(unmatched_bonus))
        this_round_pairs = process_data(copy_mentors, copy_mentees, all_rules_copy)
        current_percentage = calculate_percentage_mentees_matched(this_round_pairs[1])
        options.append(Outcome(this_round_pairs, current_percentage))
        unmatched_bonus += 1
    options.sort(key=lambda outcome: outcome.percentage)
    return options[0].participants


def calculate_percentage_mentees_matched(mentees: list[Mentee]):
    return len([mentee for mentee in mentees if len(mentee.mentors) > 0]) / len(mentees)


def conduct_matching_from_file(
    path_to_data: Path, rules: list[list[rl.RuleProtocol]]
) -> Tuple[List[Mentor], List[Mentee]]:
    mentors = create_participant_list_from_path(Mentor, path_to_data)
    mentees = create_participant_list_from_path(Mentee, path_to_data)
    return process_data(mentors, mentees, rules)


def create_mailing_list(participant_list: List[Person], output_folder: Path):
    ExportToSpreadsheet(participant_list, output_folder).export()
