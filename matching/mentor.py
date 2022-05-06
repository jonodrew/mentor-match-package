from matching.person import Person
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matching.mentee import Mentee


class Mentor(Person):
    def __init__(self, **kwargs):
        super(Mentor, self).__init__(**kwargs)

    @property
    def mentees(self):
        return super(Mentor, self).connections

    @mentees.setter
    def mentees(self, new_mentee: "Mentee"):
        super(Mentor, self).connections.append(new_mentee)

    @classmethod
    def __str__(cls):
        return "mentor"
