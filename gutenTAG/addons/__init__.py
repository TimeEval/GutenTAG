import argparse
from typing import List

from gutenTAG import GutenTAG
from gutenTAG.generator import Overview


class BaseAddOn:
    def process_overview(self, overview: Overview, args: argparse.Namespace) -> Overview:
        """Gets called before `process_generators`"""
        return overview

    def process_generators(self, generators: List[GutenTAG], args: argparse.Namespace) -> List[GutenTAG]:
        """Gets called after `process_overview`"""
        return generators
