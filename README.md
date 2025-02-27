# cs262-logical-clocks

CS262 Design Exercise 3: Scale Models and Logical Clocks

This project is a model of a small, asynchronous distributed system with multiple machines running at different speeds.

## Setup

1. Duplicate [config_example.json](config_example.json) and rename to `config.json`.
   - Fill in your configuration details.
2. Install the python dependencies for the client (this requires `poetry` to be installed):

```
poetry install
```

## Documentation

More comprehensive internal documentation (including engineering notebooks with our log analysis & observations) is in the [docs/](docs/) folder.

- Our implementation design notes are located in [docs/design.md](docs/design.md).
