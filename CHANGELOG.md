# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
