import warnings
from typing import TYPE_CHECKING

from matching.person import Person

if TYPE_CHECKING:
    from matching.mentor import Mentor


class Mentee(Person):
    def __init__(self, **kwargs):
        """
        Base class for mentees
        :param kwargs:
        """
        if kwargs.get("target_profession") or kwargs.get("target profession"):
            warnings.warn(
                "`target_profession` is now deprecated. Please use `profession`"
                " instead",
                DeprecationWarning,
            )
        super(Mentee, self).__init__(**kwargs)

    @property
    def mentors(self):
        return super(Mentee, self).connections

    @mentors.setter
    def mentors(self, new_mentor: "Mentor"):
        super(Mentee, self).connections.append(new_mentor)

    def core_to_dict(self):
        core = super(Mentee, self).core_to_dict()
        return core

    @classmethod
    def __str__(cls):
        return "mentee"
