from typing import Dict, Type

from .interface import BaseOscillationInterface


class BaseOscillation:
    key_mapping: Dict[str, Type[BaseOscillationInterface]] = {}

    @staticmethod
    def from_key(key: str, *args, **kwargs) -> BaseOscillationInterface:
        return BaseOscillation.key_mapping[key](*args, **kwargs)

    @staticmethod
    def register(name: str, bo_class: Type[BaseOscillationInterface]) -> None:
        BaseOscillation.key_mapping[name] = bo_class
