from typing import List, Dict, Union

GRADES = [
    "AA",
    "AO",
    "EO",
    "HEO",
    "SEO",
    "Grade 7",
    "Grade 6",
    "SCS1",
    "SCS2",
    "SCS3",
    "SCS4",
]


class Person:
    def __init__(self, **kwargs):
        self._grade: int = GRADES.index(kwargs.get("Your grade", "AA"))
        self.department: str = kwargs.get("Your department or agency", None)
        self.profession: str = kwargs.get("Your profession", None)
        self.email = kwargs.get("Your Civil Service email address", None)
        self.first_name = kwargs.get("Your first name", None)
        self.last_name = kwargs.get("Your last name", None)
        self.role = kwargs.get("Your job title or role", None)
        self._connections: List[Person] = []
        self.has_no_match: bool = False

    @property
    def grade(self):
        return self._grade

    @grade.setter
    def grade(self, new_grade: str):
        if new_grade in GRADES:
            self._grade = GRADES.index(new_grade)
        else:
            raise NotImplementedError

    @property
    def connections(self) -> List["Person"]:
        return self._connections

    @connections.setter
    def connections(self, new_connection: "Person"):
        if len(self._connections) < 3:
            self._connections.append(new_connection)
        else:
            raise Exception

    def to_dict(
        self,
    ) -> Dict[str, Dict[str, Union[str, List[Dict[str, Dict[str, str]]]]]]:
        output = self.core_to_dict()
        output[self.__class__.__name__.lower()]["connections"] = [
            connection.core_to_dict() for connection in self.connections
        ]
        return output

    def core_to_dict(self) -> Dict[str, Dict[str, Union[str, List]]]:
        return {
            self.__class__.__name__.lower(): {
                "email": self.email,
                "first name": self.first_name,
                "last name": self.last_name,
                "role": self.role,
                "department": self.department,
                "grade": GRADES[self.grade],
                "profession": self.profession,
            }
        }

    def to_dict_for_output(self, depth=1) -> dict:
        output = self.core_to_dict()[self.__class__.__name__.lower()]
        if depth == 1:
            for i, connection in enumerate(self._connections):
                for key, value in connection.to_dict_for_output(depth=0).items():
                    output[f"match {i + 1} {key}"] = value
        return output

    def class_name(self):
        return self.__class__.__name__.lower()

    def __eq__(self, other: "Person"):
        return self.email == other.email
