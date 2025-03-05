# cs262-logical-clocks

CS262 Design Exercise 3: Scale Models and Logical Clocks

This project is a model of a small, asynchronous distributed system with multiple machines running at different speeds.

## Setup

1. Duplicate [config_example.json](config_example.json) and rename to `config.json`.
   - Fill in your configuration details.
2. Install the python dependencies (this requires `poetry` to be installed):

```
poetry install
```

## Run Experiments

1. Navigate into [system/](system/) folder:

```
cd system
```

2. Run [main.py](system/main.py):

```
poetry run python main.py
```

Note: our [logs](system/logs/) and [figures](system/figures/) from running experiments are also located in this folder.

## Documentation

More comprehensive internal documentation (including engineering notebooks with our log analysis & observations) is in the [docs/](docs/) folder.

- Our implementation design notes are located in [docs/design.md](docs/design.md).

## Testing

1. Navigate into [system/tests/](system/tests/) folder:

```
cd system/tests
```

2. Start tests:

```
poetry run pytest
```
