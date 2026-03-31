# Development

This page describes the local workflow for contributing to bulletin-fetcher.

## Local Setup

1. Create a virtual environment.
2. Activate it.
3. Install development and documentation dependencies.

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .[dev,docs]
```

## Run Tests

Run all tests:

```bash
pytest
```

Generate coverage XML report:

```bash
pytest --cov --cov-branch --cov-report=xml
```

## Build Docs

Serve docs locally:

```bash
mkdocs serve -a 127.0.0.1:8000
```

Build static docs:

```bash
mkdocs build
```

## Reporting Issues

If you encounter any issues, please report them on the [GitHub Issues page](https://github.com/diegoglezsu/bulletin-fetcher/issues). When reporting an issue, please include:

- A clear and descriptive title.
- A detailed description of the problem.
- Steps to reproduce the issue.
- Any relevant screenshots or error messages.

## Contributing

Contributions are welcome! Please follow the standard steps:

1. Fork the project.
2. Create a branch for your feature (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a pull request describing your changes and the problem they solve.
