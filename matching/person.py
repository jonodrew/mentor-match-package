import warnings
from typing import List, Dict, Union

CorePersonDict = Dict[str, Dict[str, Union[str, int]]]
PersonDict = Dict[str, Dict[str, Union[str, int, list[CorePersonDict]]]]


class Person:
    def __init__(self, **kwargs):
        """
        When creating a person from a dictionary, we expect a grade as an integer. The lower the `int`, the lower the
        grade. It is the client's responsibility to turn this integer back into a human-readable `str` if needed
        :param kwargs:
        """
        self.grade: int = int(kwargs.get("grade"))
        self.organisation: str = kwargs.get("organisation", None)
        if (profession := kwargs.get("current profession")) is not None:
            warnings.warn(
                "In version 7, 'current profession' will be deprecated in favour of"
                " 'profession'. If you need to keep using 'current profession', please"
                " subclass Person",
                PendingDeprecationWarning,
            )
            self.current_profession = self.profession = profession
        else:
            self.profession = self.current_profession = kwargs.get("profession", "")
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
    ) -> PersonDict:
        connections_list = [
            connection.core_to_dict() for connection in self.connections
        ]
        output: PersonDict = {
            self.class_name(): {
                "connections": connections_list,
                **self.core_to_dict()[self.class_name()],
            }
        }
        return output

    def core_to_dict(self) -> CorePersonDict:
        return {
            self.class_name(): {
                "email": self.email,
                "first name": self.first_name,
                "last name": self.last_name,
                "role": self.role,
                "organisation": self.organisation,
                "grade": self.grade,
                "profession": self.profession,
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

    def to_dict_for_export(self, depth=1) -> dict:
        """
        This method converts the class into a dictionary suitable for export. It might be useful if you don't want
        every attribute on the model exposed, or if there's some mapping you need to do - for example, 'grade' might be
        'rank' in your organisation. By default, this method just calls `to_dict_for_output`
        """
        return self.to_dict_for_output(depth)

    def class_name(self):
        return self.__class__.__name__.lower()

    def __eq__(self, other: object):
        if not isinstance(other, Person):
            raise NotImplementedError
        return self.email == other.email
