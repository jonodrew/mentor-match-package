from typing import List, Dict, Union


class Person:
    def __init__(self, **kwargs):
        """
        When creating a person from a dictionary, we expect a grade as an integer. The lower the `int`, the lower the
        grade. It is the client's responsibility to turn this integer back into a human-readable `str` if needed
        :param kwargs:
        """
        self.grade: int = int(kwargs.get("grade"))
        self.organisation: str = kwargs.get("organisation", None)
        self.current_profession: str = kwargs.get("current profession", None)
        self.email = kwargs.get("email", None)
        self.first_name = kwargs.get("first name", None)
        self.last_name = kwargs.get("last name", None)
        self.role = kwargs.get("role", None)
        self._connections: List[Person] = []
        self.has_no_match: bool = False

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
        output[self.class_name()]["connections"] = [
            connection.core_to_dict() for connection in self.connections
        ]
        return output

    def core_to_dict(self) -> Dict[str, Dict[str, Union[str, List]]]:
        return {
            self.class_name(): {
                "email": self.email,
                "first name": self.first_name,
                "last name": self.last_name,
                "role": self.role,
                "organisation": self.organisation,
                "grade": self.grade,
                "current profession": self.current_profession,
            }
        }

    def to_dict_for_output(self, depth=1) -> dict:
        output = self.core_to_dict()[self.class_name()]
        if depth == 1:
            for i, connection in enumerate(self._connections):
                for key, value in connection.to_dict_for_output(depth=0).items():
                    output[f"match {i + 1} {key}"] = value
        return output

    def class_name(self):
        return self.__class__.__name__.lower()

    def __eq__(self, other: "Person"):
        return self.email == other.email
