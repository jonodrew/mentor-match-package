import pytest as pytest

from matching.mentee import Mentee
from matching.mentor import Mentor
from matching.process import create_participant_list_from_path
import math
import csv


@pytest.fixture
def known_file(base_data):
    def _known_file(path_to_file, role_type: str, quantity=50):
        padding_size = int(math.log10(quantity)) + 1
        data_path = path_to_file / f"{role_type}s.csv"
        with open(data_path, "w", newline="") as test_data:
            headings = [
                "first name",
                "last name",
                "email",
                "role",
                "organisation",
                "grade",
                "current profession",
                "target profession",
            ]
            data = [headings]
            for i in range(quantity):
                data.append(
                    [
                        role_type,
                        str(i).zfill(padding_size),
                        f"{role_type}.{str(i).zfill(padding_size)}@gov.uk",
                        "Some role",
                        f"Department of {role_type.capitalize()}s",
                        2 if role_type == "mentor" else 0,
                        "Policy",
                        "Policy",
                    ]
                )
            file_writer = csv.writer(test_data)
            file_writer.writerows(data)

    return _known_file


@pytest.fixture(scope="session")
def test_data_path(tmpdir_factory):
    return tmpdir_factory.mktemp("data")


@pytest.fixture
def test_participants(test_data_path, known_file):
    known_file(test_data_path, "mentee", 50)
    known_file(test_data_path, "mentor", 50)
    create_participant_list_from_path(Mentee, test_data_path)
    create_participant_list_from_path(Mentor, test_data_path)
    yield


@pytest.fixture
def base_data() -> dict:
    return {
        "first name": "Test",
        "last name": "Data",
        "email": "test@data.com",
        "role": "N/A",
        "organisation": "Department of Fun",
        "grade": 5,
        "current profession": "Policy",
    }


@pytest.fixture
def base_mentee(base_data):
    mentee = Mentee(**base_data)
    mentee.target_profession = "Policy"
    return mentee


@pytest.fixture
def base_mentor(base_data):
    data_copy = base_data.copy()
    data_copy["grade"] = 6
    data_copy["organisation"] = "Ministry of Silly Walks"
    return Mentor(**data_copy)
