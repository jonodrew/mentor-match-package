from typing import Dict, List

from matching.mentee import Mentee
from matching.mentor import Mentor
from matching.person import GRADES, Person


class ParticipantFactory:
    participant_types = {"mentor": Mentor, "mentee": Mentee}

    @classmethod
    def create_from_dict(cls, data_as_dict: Dict):
        participant_type_str = list(data_as_dict).pop()
        participant_type = cls.participant_types.get(participant_type_str, Person)
        participant_data = data_as_dict.get(participant_type_str, dict())
        participant = participant_type()
        participant._grade = GRADES.index(participant_data["grade"])
        participant.department = participant_data["department"]
        participant.profession = participant_data["profession"]
        participant.email = participant_data["email"]
        participant.first_name = participant_data["first name"]
        participant.last_name = participant_data["last name"]
        participant.role = participant_data["role"]
        connections: List[Dict[str, str]] = participant_data.get("connections", [])
        participant._connections = [
            ParticipantFactory.create_from_dict(connection_data)
            for connection_data in connections
        ]
        return participant
