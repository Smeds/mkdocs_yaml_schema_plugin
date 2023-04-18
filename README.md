# MkDocs Yaml Schema Plugin

MkDocs Plugin to parse yaml schema files.

To use this plugin, install it with pip in the same environment as MkDocs:

```
pip install MkDocsYamlSchemaPlugin
```

Then add the following entry to the MkDocs config file:

```yml
plugins:
- yaml-schema:
yaml_schema: "docs/item.schema.json"
```

In your target file, add a tag to be replaced
```
#JsonSchema#
```
