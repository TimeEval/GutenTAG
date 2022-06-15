import argparse
from typing import Tuple

from gutenTAG import GutenTAG
from gutenTAG.generator import Overview


class BaseAddOn:
    def process(self, overview: Overview, gutenTAG: GutenTAG, args: argparse.Namespace) -> Tuple[Overview, GutenTAG]:
        """Gets called before `process_generators`"""
        return overview, gutenTAG
