from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='gutenTAG',
    version='0.1.0',
    packages=find_packages(exclude=("tests",)),
    url='https://gitlab.hpi.de/akita/guten-tag',
    license='MIT',
    author='Phillip Wenig',
    author_email='phillip.wenig@hpi.de',
    description='A good Timeseries Anomaly Generator.',
    install_requires=required
)
