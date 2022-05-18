import csv
import os
from abc import abstractmethod
from pathlib import Path

from matching.mentee import Person


class ExportToSpreadsheet:
    def __init__(self, participants: list[Person], path_to_output_folder: Path):
        self.output_path = path_to_output_folder
        self.participants = participants

    def export(self):
        """
        This function takes a list of either matched mentors or matched mentees. For each participant, it outputs their
        data and the information of the participants they've been matched with. If a participant doesn't have the full
        complement of three matches, the empty spaces are ignored.
        """
        participant_type = self.participants[0].class_name()
        file_name = f"{participant_type}s-list.csv"
        file = self.output_path.joinpath(file_name)
        list_participants_as_dicts = [
            participant.to_dict_for_export() for participant in self.participants
        ]
        field_headings = max(
            list_participants_as_dicts, key=lambda participant: len(participant.keys())
        ).keys()
        try:
            os.mkdir(self.output_path)
        except FileExistsError:
            pass
        with open(file, "w", newline="") as output_file:
            writer = csv.DictWriter(output_file, fieldnames=list(field_headings))
            writer.writeheader()
            for participant in list_participants_as_dicts:
                writer.writerow(participant)


class ExportToEmail:
    def __init__(self, participants: list[Person], api_client: object):
        self.participants = participants
        self.client = api_client

    @abstractmethod
    def export(self):
        raise NotImplementedError
