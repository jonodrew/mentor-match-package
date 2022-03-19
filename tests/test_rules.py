import matching.rules.rule as rules
from matching.match import Match


class TestRules:
    def test_matching_scores_scores_correct_points(self, base_mentor, base_mentee):
        profession_rule = rules.Equivalent({True: 4, False: 0}, "profession")
        test_match = Match(base_mentor, base_mentee, weightings={}, rules=[])
        assert profession_rule.apply(test_match) == 4
