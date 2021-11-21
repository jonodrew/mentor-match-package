import argparse
import logging
from pathlib import Path

from matching.process import conduct_matching_from_file, create_mailing_list


def main():
    parser = argparse.ArgumentParser(
        description='Match mentors to mentees. Your files should be called "mentees.csv" and "mentors.csv".'
    )
    parser.add_argument(
        "filepath", type=str, help="the path to the data containing the files"
    )
    path_to_data = Path(parser.parse_args().filepath)
    logging.info("Beginning matching exercise. This might take up to five minutes.")
    mentors, mentees = conduct_matching_from_file(path_to_data)
    logging.info("Matches found. Exporting to output folder!")
    out_put_folder = path_to_data / "output"
    create_mailing_list(mentors, out_put_folder)
    create_mailing_list(mentees, out_put_folder)


if __name__ == "__main__":
    main()
