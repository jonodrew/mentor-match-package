import pathlib

from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="mentor-match",
    version="6.2.0",
    description="A series of classes to match mentors and mentees",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Jonathan Kerr",
    author_email="jonathan.drew.kerr@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["matching", "matching/rules"],
    include_package_data=True,
    install_requires=["munkres"],
    setup_requires=["wheel"],
)
