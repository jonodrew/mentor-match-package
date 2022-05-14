# Mentor Match

This is a package to help match mentees and mentors.

It uses [this implementation of Munkres](https://github.com/bmc/munkres) to find the most effective pairings. The Munkres algorithm works on a grid of scores.

## Scoring

Full details of how the matches are calculated can be read in the code itself. Customisable configurations are on the
roadmap but are not planned for any upcoming releases.

## Installation

You can install this project with `python -m pip install mentor-match`

## Use

To use this library, first install it (see above). You may need to munge your data for the system to be happy with it.
Use the [example CSV file](example.csv) as guides for your mentor and mentee data, then put them together in the same folder.

The software will run as many matching exercises as you pass `list[AbstractRule]`. So you'll need to come up with
some rules as to how you want your mentors and mentees to be matched. For more information on rules, see [Rules](#rules).

Here is a snippet that outlines a minimal use in a Python project:

```python
from matching import process
from pathlib import Path
from matching.rules.rule import Generic

data_folder = Path("Documents/mentoring-data")
mentors, mentees = process.conduct_matching_from_file(
    path_to_data=data_folder,
    rules=[[Generic({True: 3, False: 0}, lambda match: match.mentee.organisation != match.mentor.organisation)]]
)

output_folder = data_folder / "output"
process.create_mailing_list(mentors, output_folder)
process.create_mailing_list(mentees, output_folder)
```
This weights matches where mentors and mentees are in different organisations. For more on rules, see [Rules](#rules).
The system then creates a mailing list according to a set template, ready for processing by your
favourite/enterprise mandated email solution

## Rules

All rules are subclassed from the `AbstractRule` class. They need an `evaluate` method, which should take a `Match`
object and return a `boolean`, and an `apply` method, which takes a `Match` object, evaluates it, and changes the
internal state of the `Match` object.

I've included a couple of pre-defined rules to help start you off:

### Grade
`Grade` needs a target difference in grades between mentors and mentees, an operator to compare them, and a score to
give if the operation is true or if it's false. So `Grade(2, operator.gt, {True: 3, False: 0})` will create a rule
that gives 3 points to a grade difference between the mentor and the mentee that's greater than 2.

### UnmatchedBonus
`UnmatchedBonus` only needs an integer value to add to the Match score. It'll add it if either the mentor or the
mentee doesn't have any connections. This is helpful if you run multiple rounds, as it'll give the edge to
mentors/mentees who haven't been successfully matched yet.

### Disqualify
`Disqualify` needs to be passed a function that takes a `Match` object and returns a `bool`. It's an anti-rule: if the
condition evaluates to `True`, then that `Match` is disqualified for this round. Two `Disqualify` rules are
pre-defined on the `Match` object - a `Match` is disqualified if both `Mentor` and `Mentee` are the same person, or
if they've already been matched once.

### Generic
`Generic`, like `Disqualify`, takes a function with the signature `[[Match], bool]`. It also takes a dictionary,
like `Grade`, where you define what score to be given to the `Match` if the function evaluates to true, or indeed if
it evaluates to false!
