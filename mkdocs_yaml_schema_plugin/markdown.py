import re
import yaml


def extract_yaml_section(parts, yaml_data):
    if len(parts) > 0:
        return extract_yaml_section(parts[1:], yaml_data[parts[0]])
    else:
        return yaml_data


class markdown_gen:
    schema_file = ''
    tag = ''
    indent_val = "    "
    bold_keys = ["NOTE:", "RECOMMENDATION:"]

    def safe_get_value(self, data, key):
        if data is None:
            return None, False
        try:
            output = data[key]
            return output, True
        except KeyError:
            return None, False

    def get_markdown(self, markdown, **kwargs):
        # we can assume the file was set, or it throws a validation error
        if self.yaml_config:
            for index in range(len(self.yaml_config)):
                with open(self.yaml_config[index]['file']) as yaml_file:
                    self.yaml_config[index]['data'] = yaml.safe_load(yaml_file)

            for values in self.yaml_config:
                for g in re.finditer(values['regex'], markdown):
                    parts = g.group()[1:-1].split("__")
                    new_markdown = self.markdown_for_items(parts[1],
                                                           extract_yaml_section(parts[1:],
                                                           values['data']['properties']))
                    markdown = markdown.replace(g.group(), new_markdown)

            return markdown

    def markdown_for_items(self, section, items):
        markdown_data = "| Key | Type | Description |\n"
        markdown_data += "| --- | --- | --- |\n"

        for key, values in items['properties'].items():
            description = values['description'].replace("\n", "<br />")
            for bold_key in self.bold_keys:
                description = description.replace(bold_key, f"**{bold_key}**")
            markdown_data += f"| {key} | {values['type']} | {description} |\n"

        return markdown_data

    def set_config(self, config):
        self.yaml_config = []
        # CHeck why I need to fetch first object
        for f in self.safe_get_value(config, "yaml_files")[0]:
            self.yaml_config.append({
                'tag': f['tag'],
                'file': f['file'],
                'regex': r"#" + re.escape(f['tag']) + r"[A-Za-z0-9_]*#"
            })
            print(f"Got config: File: {f['file']} Tag: {f['tag']}")
