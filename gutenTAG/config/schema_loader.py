import abc
import os
from pathlib import Path
from typing import Dict

import yaml

from ..utils.global_variables import CONFIG_SCHEMA


class ConfigSchemaLoader(abc.ABC):
    @abc.abstractmethod
    def load_schema_file(self, schema_id: str) -> Dict:
        raise NotImplementedError()


class FileSystemConfigSchemaLoader(ConfigSchemaLoader):
    def __init__(self, base_path: Path = CONFIG_SCHEMA.SCHEMA_FOLDER_PATH):
        super().__init__()
        self.base_path = base_path

    def load_schema_file(self, schema_id: str) -> Dict:
        schema_path = CONFIG_SCHEMA.schema_path(schema_id, path=self.base_path)
        with schema_path.open("r") as fh:
            schema = yaml.safe_load(fh)
        return schema

    @staticmethod
    def from_packaged_schema() -> "ConfigSchemaLoader":
        current_path = Path(os.path.dirname(__file__)).absolute()
        return FileSystemConfigSchemaLoader(current_path / "schema")


# We could add a second method of loading the schema using the python package structure similar to
# https://github.com/pallets/jinja/blob/c3a61d6ef654f389ea2bdeddce0ffc74d656be8b/src/jinja2/loaders.py#L238

# class PackageConfigSchemaLoader(ConfigSchemaLoader):
#   pass
