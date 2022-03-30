import glob
import os
import shutil
import sys
from distutils.cmd import Command
from distutils.errors import DistutilsError
from pathlib import Path

from setuptools import setup, find_packages


HERE = Path(os.path.dirname(__file__)).absolute()
# get __version__ from gutenTAG/_version.py
with open(HERE / "gutenTAG" / "_version.py") as f:
    exec(f.read())
VERSION: str = __version__  # noqa
README = (HERE / "README.md").read_text(encoding="UTF-8")
DOC_NAME = "GutenTAG"
PYTHON_NAME = "gutenTAG"


class PyTestCommand(Command):
    description = f"run PyTest for {DOC_NAME}"
    user_options = []

    def initialize_options(self) -> None:
        pass

    def finalize_options(self) -> None:
        pass

    def run(self) -> None:
        import pytest
        from pytest import ExitCode

        exit_code = pytest.main(["--cov-report=term", "--cov-report=xml:coverage.xml",
                                 f"--cov={PYTHON_NAME}", "tests"])
        if exit_code == ExitCode.TESTS_FAILED:
            raise DistutilsError("Tests failed!")
        elif exit_code == ExitCode.INTERRUPTED:
            raise DistutilsError("pytest was interrupted!")
        elif exit_code == ExitCode.INTERNAL_ERROR:
            raise DistutilsError("pytest internal error!")
        elif exit_code == ExitCode.USAGE_ERROR:
            raise DistutilsError("Pytest was not correctly used!")
        elif exit_code == ExitCode.NO_TESTS_COLLECTED:
            raise DistutilsError("No tests found!")
        # else: everything is fine


class MyPyCheckCommand(Command):
    description = f"run MyPy for {DOC_NAME}; performs static type checking"
    user_options = []

    def initialize_options(self) -> None:
        pass

    def finalize_options(self) -> None:
        pass

    def run(self) -> None:
        from mypy.main import main as mypy

        args = ["--pretty", PYTHON_NAME, "tests"]
        mypy(None, stdout=sys.stdout, stderr=sys.stderr, args=args)


class CleanCommand(Command):
    description = "Remove build artifacts from the source tree"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        files = [
            ".coverage*",
            "coverage.xml"
        ]
        dirs = ["build", "dist", "*.egg-info", "**/__pycache__", ".mypy_cache",
                ".pytest_cache", "**/.ipynb_checkpoints"]
        for d in dirs:
            for filename in glob.glob(d):
                shutil.rmtree(filename, ignore_errors=True)

        for f in files:
            for filename in glob.glob(f):
                try:
                    os.remove(filename)
                except OSError:
                    pass


if __name__ == "__main__":
    with open('requirements.txt') as fh:
        required = fh.read().splitlines()

    setup(
        name=f"timeeval-{PYTHON_NAME}",
        version=VERSION,
        description="A good Timeseries Anomaly Generator.",
        long_description=README,
        long_description_content_type="text/markdown",
        author="Phillip Wenig and Sebastian Schmidl",
        author_email="phillip.wenig@hpi.de",
        url="https://github.com/HPI-Information-Systems/gutentag",
        license="MIT",
        classifiers=[
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9"
        ],
        packages=find_packages(exclude=("tests", "tests.*")),
        package_data={"gutenTAG": ["py.typed"]},
        install_requires=required,
        python_requires=">=3.7",
        test_suite="tests",
        cmdclass={
            "test": PyTestCommand,
            "typecheck": MyPyCheckCommand,
            "clean": CleanCommand
        },
        zip_safe=False,
        # provides="gutenTAG",
        entry_points={
            "console_scripts": [
                "gutenTAG=gutenTAG.__main__:cli"
            ]
        }
    )
