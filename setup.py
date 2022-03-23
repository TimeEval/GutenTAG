import glob
import os
import shutil
import sys
from distutils.cmd import Command
from distutils.errors import DistutilsError
from pathlib import Path

from setuptools import setup, find_packages


DOC_NAME = "GutenTAG"
PYTHON_NAME = "gutenTAG"

HERE = Path(os.path.dirname(__file__)).absolute()
# get __version__ from gutenTAG/_version.py
with open(HERE / "gutenTAG" / "_version.py") as f:
    exec(f.read())
VERSION: str = __version__  # noqa


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
    description = f'run MyPy for {DOC_NAME}; performs static type checking'
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


with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name=PYTHON_NAME,
    version=VERSION,
    packages=find_packages(exclude=("tests",)),
    url='https://gitlab.hpi.de/akita/guten-tag',
    license='MIT',
    author='Phillip Wenig',
    author_email='phillip.wenig@hpi.de',
    description='A good Timeseries Anomaly Generator.',
    install_requires=required,
    python_requires=">=3.8",
    cmdclass={
        "test": PyTestCommand,
        "typecheck": MyPyCheckCommand,
        "clean": CleanCommand
    },
    zip_safe=False
)
