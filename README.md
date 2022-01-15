# Mentor Match

This is a package to help match mentees and mentors. It's specifically designed for a volunteer programme I support, but you could probably extend or alter it to suit whatever you're doing.

It uses [this implementation of Munkres](https://github.com/bmc/munkres) to find the most effective pairings. The Munkres algorithm works on a grid of scores.

## Scoring

Full details of how the matches are calculated can be read in the code itself. Customisable configurations are on the 
roadmap but are not planned for any upcoming releases.

## Installation

You can install this project with `python -m pip install mentor-match`

## Use

To use this library, first install it (see above). You may need to munge your data for the system to be happy with it. 
Use the attached CSV files as guides for your mentor and mentee data, then put them together in the same folder.

Here is a snippet that outlines a minimal use:

```python
from matching import process

data_folder = "Documents/mentoring-data"
mentors, mentees = process.conduct_matching_from_file(data_folder)

output_folder = data_folder / "output"
process.create_mailing_list(mentors, output_folder)
process.create_mailing_list(mentees, output_folder)
```
This creates a mailing list according to a set template, ready for processing by your favourite/enterprise mandated 
email solution