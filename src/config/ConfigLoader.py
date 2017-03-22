"""ConfigLoader converts yaml into dict of dicts via PyYaml."""


import Constants as CONST
import os
import yaml


class ConfigLoader():
    """Object that handles YAML loading."""

    def __init__(self):
        """Init ConfigLoader to load all game config data files."""
        # Fetch list of all config files we want to load.
        # First, get paths and globals set up.
        global _master_config
        _manifest_path = CONST.YAML_MANIFEST_PATH
        _script_dir = os.path.dirname(os.path.dirname(__file__))
        _relative_path = os.path.join(_script_dir, _manifest_path)

        # Get the config file manifest list from PyYaml.
        config_file_list = self.yaml_loader(_relative_path)

        # Create yaml doc generator, then convert it into a list of dicts.
        _configs_list = []
        for i in config_file_list:
            adjusted_path = os.path.join(_script_dir, i)
            _configs_list.extend(self.yaml_loader(adjusted_path))

        # Create master config dict of dicts.
        _master_config = {}
        for d in _configs_list:
            _master_config.update(d)

    @property
    def _master_config(self):
        return _master_config

    def yaml_loader(self, filepath):
        """Load a yaml file and return a list of the documents."""
        # Multi-document yaml method must cast generator to list.
        with open(filepath, "r") as file_descriptor:
            yaml_generator = yaml.load_all(file_descriptor)
            yaml_nested_list = list(yaml_generator)
            if len(yaml_nested_list) == 1:
                return yaml_nested_list[0]
            else:
                return yaml_nested_list

    def yaml_dump(self, filepath, data):
        """Dump data to a yaml file."""
        with open(filepath, "w") as file_descriptor:
            yaml.dump(data, file_descriptor, default_flow_style=False)

if __name__ == "__main__":
    config = ConfigLoader()

    print(config._master_config)
