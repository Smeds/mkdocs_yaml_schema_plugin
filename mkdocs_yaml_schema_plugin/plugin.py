
from mkdocs import plugins, config
from .markdown import markdown_gen


class YamlSchema(plugins.BasePlugin):

    config_scheme = (
        ('yaml_files', config.config_options.Type(list, default={})),
#        ('yaml_tag', config.config_options.Type(str, default=''))
    )
    generator = markdown_gen()

    def on_config(self, config):
        self.generator = markdown_gen()
        self.generator.set_config(self.config)

    def __init__(self):
        super().__init__()


    def on_page_markdown(self, markdown, **kwargs):
        return self.generator.get_markdown(markdown, **kwargs)