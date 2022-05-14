from typing import TYPE_CHECKING

from matching.person import Person

if TYPE_CHECKING:
    from matching.mentor import Mentor


class Mentee(Person):
    def __init__(self, **kwargs):
        """
        Mentees should have a target profession. If they don't have a target profession, we assume it's the same one
        they're in at the moment
        :param kwargs:
        """
        self.target_profession = kwargs.get(
            "target profession", kwargs.get("current profession")
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
        core[self.class_name()]["target profession"] = self.target_profession
        return core

    @classmethod
    def __str__(cls):
        return "mentee"
