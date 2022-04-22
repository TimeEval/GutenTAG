from typing import Dict

import jsonschema
from jsonschema import RefResolver

from gutenTAG.config.schema_loader import ConfigSchemaLoader, FileSystemConfigSchemaLoader
from gutenTAG.utils.global_variables import CONFIG_SCHEMA


class ConfigValidator:
    def __init__(self):
        loader: ConfigSchemaLoader = FileSystemConfigSchemaLoader.from_packaged_schema()
        # load base schema
        base_schema_name = CONFIG_SCHEMA.schema_name(CONFIG_SCHEMA.BASE_ID)
        base_schema = loader.load_schema_file(CONFIG_SCHEMA.BASE_ID)

        # load schema parts
        schema_parts = {}
        for schema_part_id in CONFIG_SCHEMA.SCHEMA_PART_IDS:
            name = CONFIG_SCHEMA.schema_name(schema_part_id)
            schema_parts[name] = loader.load_schema_file(schema_part_id)

        # create resolver containing all schema parts
        self.base_schema = base_schema
        self.resolver = RefResolver(
            base_uri=base_schema_name,
            referrer=base_schema,
            store=schema_parts
        )

    def validate(self, config: Dict) -> None:
        jsonschema.validate(config, self.base_schema, resolver=self.resolver)
