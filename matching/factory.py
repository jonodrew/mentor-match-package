from typing import Dict, List

from matching.mentee import Mentee
from matching.mentor import Mentor
from matching.person import Person


class ParticipantFactory:
    participant_types = {"mentor": Mentor, "mentee": Mentee}

    @classmethod
    def create_from_dict(cls, data_as_dict: Dict):
        participant_type_str = list(data_as_dict).pop()
        participant_type = cls.participant_types.get(participant_type_str, Person)
        participant_data = data_as_dict.get(participant_type_str, dict())
        participant = participant_type(**participant_data)
        connections: List[Dict[str, str]] = participant_data.get("connections", [])
        participant._connections = [
            cls.create_from_dict(connection_data) for connection_data in connections
        ]
        if type(participant) is Mentee:
            participant.target_profession = participant_data["target profession"]
        return participant
