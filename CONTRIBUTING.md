# Contributing

## Code style and format

We use [black](https://black.readthedocs.io/) to automatically format our python files.
Please stick to the black code style.

Please consider using the pre-commit hooks.
They automatically run i.a. black for you.
See next section.

### Black quick-installation guide

```bash
pip install black
black
```

## Running pre-commit hooks

We use [pre-commit](https://pre-commit.com/) to run some checks on your files before they are commited.
Find the configured hooks in [`.pre-commit-config.yaml`](./pre-commit-config.yaml).
If there are errors, you have to re-add the files to the index and commit the fixed files.

### Pre-commit quick-installation guide

```bash
pip install pre-commit
pre-commit install
```

Optionally, cou can then run the hooks against all files with:

```bash
pre-commit run --all-files
```
