import json

import pytest

from matching.factory import ParticipantFactory
from matching.mentee import Mentee
from matching.mentor import Mentor
from matching.person import Person


class TestPerson:
    def test_to_dict_depth_zero(self, base_data):
        expected_values = base_data.values()
        assert set(Person(**base_data).to_dict_for_output(depth=0).values()) == set(
            expected_values
        )

    def test_to_dict_depth_one(self, base_data):
        test_person = Person(**base_data)
        test_person.connections.extend([Person(**base_data) for _ in range(3)])
        mentor_as_dict = test_person.to_dict_for_output(depth=1)
        assert "match 1 email" in mentor_as_dict.keys()

    @pytest.mark.parametrize(
        ["participant_class", "connection_class"],
        [(Person, Person), (Mentor, Mentee), (Mentee, Mentor)],
    )
    def test_person_is_serializable(
        self, base_data, participant_class, connection_class
    ):
        test_person = participant_class(**base_data)
        test_person.connections.extend(
            [connection_class(**base_data) for _ in range(3)]
        )
        person_as_json = json.dumps(test_person.to_dict())
        assert type(person_as_json) is str

    @pytest.mark.parametrize(
        ["participant_class", "connection_class"], [(Mentor, Mentee), (Mentee, Mentor)]
    )
    def test_person_is_deserializable(
        self, base_data, participant_class, connection_class
    ):
        test_person = participant_class(**base_data)
        test_person.connections.extend(
            [connection_class(**base_data) for _ in range(3)]
        )
        person_as_json = json.dumps(test_person.to_dict())
        person_as_dict = json.loads(person_as_json)
        recreated_person = ParticipantFactory.create_from_dict(person_as_dict)
        assert recreated_person == test_person
