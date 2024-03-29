# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [7.0.1] - 2022-09-01
### Changed

- `process_data` now returns a bound variable, because my IDE was getting annoyed with me. That's it. That's the
  whole reason

## [7.0.0] - 2022-06-25

### Changed

- "target profession" and "current profession" have been reverted to "profession" on the Mentee and Mentor object
  respectively. You are welcome to override these in your subclasses, but it's too confusing to have different
  values on the base model
- the participant.csv file has been changed

### Added

## [6.3.0] - 2022-06-10

### Changed

- there's now a `RuleProtocol` interface, which describes what a `Rule` should look like

## [6.2.0] - 2022-05-14

### Changed

- There is a `PendingDeprecationWarning` on the changes marked above, which are mooted for version 7. Please
  consider now what will happen when you can't pass "current profession" and "target profession" to the classes.
  There are a couple of approaches you could consider:
  - Subclassing the class you want and adding another attribute, accessible from kwargs. You'll also want to
    override the `core_to_dict` methods
  - Subclassing the class and adding a `property` that describes the `profession` attribute the way you think it
    should be described. This way you can keep using the normal template and do the transformation in code.

## 6.1.0 2022-05-18

### Added

- there's now two new classes for exporting data. If you're using this library, you can either just use the
`ExportToSpreadsheet` class to...well...export to a spreadsheet. Alternatively, if you're using email to contact
successful matches, why not subclass `ExportToEmail` and pass it your favourite email client?

## 6.0.0 2022-05-14

### Removed

- Weightings have been removed. All weightings must be tied to `Rule` objects.

## 5.1.4 2022-05-08

### Added

- The `Person` base class now has a method `to_dict_for_export`. This could be useful if users want a different
  representation for exporting - for example, if they don't need every attribute on the model, or they want to do
  some calculations before exporting. By default, it just calls `to_dict_for_output`. In a future major version,
  this method will be renamed simply to `to_dict`, to reflect that it's a full representation of the model.

## 5.1.0 2022-04-15

### Added

- Users can pass a mapping function to `create_participant_list_from_path`. The function will be passed
  a `dict[str, str]`, representing a row in the user-uploaded spreadsheet, and can also access a string representation
  of the type of participant - "mentor" or "mentee". This function is optional, but the software will break in ugly
  ways if your spreadsheet doesn't have the headings in the [example csv file](./example.csv). It can have others,
  but they'll be ignored

### Changed

- I've updated the csv file and removed the "role type" heading, because it's currently not important. I will put an
  issue on the roadmap to allow users to upload a single spreadsheet with everyone on it

## 5.0.0 2022-04-14

### Changed

- The `Person` object must now be instantiated from a simpler dictionary, with one-word keys. See the example csv for
  what those are
- Oh, I added an example csv file!
- `profession` has been renamed to `current_profession`

### Removed

- `Person.grade` is now always an `int`. This generalises the software away from a purely Civil Service basis, but does
  mean that users are required to do their own mapping of integers to human-readable strings

### Added

- `Mentee` objects now have a `target_profession` as well as a `current_profession`
- There is now a `Generic` rule object, where you can pass a `lambda` if your condition is nice and simple. Or even if
  it's not, I'm not the boss of you.

## 4.0.0 2022-03-20

### Removed

- The functions that scored matches have been moved outside of the `Match` object and must be passed when the object is
  initialised. This change is breaking because the API of the `Match` object has changed. However, if clients are
  calling `process_data` to do their data processing, there should be no change to their workflow and this will be
  **non-breaking**.

### Added

- A `Rule` class, which describes the rules to be used for scoring `Match` objects. All `Rule` subclasses must implement
  an `evaluate` method that takes a `Match` object and returns a `bool`

### Deprecated

- In the next release, clients will create `Rule` objects with scores, and `weighting_list` will not be passed to
  `process_data`

## 3.0.0 2022-03-13

### Removed

- The weightings for each round of matching were hard-coded into the software. This is removed in this version, and
  clients must pass their weightings as a `List[Dict[str, int]]` to the `process_data` function
