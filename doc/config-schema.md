# GutenTAG generation configuration schema

GutenTAG comes with YAML/JSON schema definitions for the generation configuration files (such as [`example-config.yaml`](../generation_configs/example-config.yaml)).
You can find the schema definitions in the folder [`gutenTAG/config/schema/'](./gutenTAG/config/schema).

The schema can be used to enhance IDEs and editors with syntax highlighting, code completion, and linting features for the GutenTAG configuration files.

The file `guten-tag-generation-config.schema.yaml` is the base schema that references the following sub-schemas:

- `oscillation.guten-tag-generation-config.schema.yaml` for the definition of base oscillations and trends.
- `anomaly.guten-tag-generation-config.schema.yaml` for the definition of anomalies.
- `anomaly-kind.guten-tag-generation-config.schema.yaml` for the definition of anomaly kinds (only used within `anomaly.guten-tag-generation-config.schema.yaml`).
- `formula.guten-tag-generation-config.schema.yaml` for the definition of formula base oscillations (only used within `oscillation.guten-tag-generation-config.schema.yaml`).

## IDE/Editor configuration

### Visual Studio Code

1. Install and enable the [Red Hat VSCode YAML plugin](https://github.com/redhat-developer/vscode-yaml)
2. Add a mapping for files that should be checked against the GutenTAG schema `guten-tag-generation-config.schema.yaml` to your settings.
   E.g. for the `example-config.yaml`-file included in this repository:

   ```json
   {
     "yaml.schemas": {
        "./gutenTAG/config/schema/guten-tag-generation-config.schema.yaml": [
           "generation_configs/example-config.yaml"
        ]
     }
   }
   ```

### JetBrains (PyCharm)

1. Open the desired file (e.g. the [`example-config.yaml`](../generation_configs/example-config.yaml))
2. In the lower right corner, click on _No JSON schema_
   ![PyCharm select schema](images/pycharm-select-schema.png)
3. In the upcoming dropdown list, select _New schema mapping ..._
4. Select the file `gutenTAG/config/schema/guten-tag-generation-config.schema.yaml` and give this schema a representative name. Hit _OK_.
   ![PyCharm create schema mapping](images/pycharm-create-schema-mapping.png)
