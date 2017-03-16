"""ConfigLoader converts yaml into dict of dicts via PyYaml."""


import Constants as CONST
import os
import yaml


class ConfigLoader():
    """Object that handles YAML loading."""

    def __init__(self, log):
        """Init ConfigLoader to load all game config data files."""
        global _ecs_config_filepath
        global _items_config_filepath
        global _master_config


        # Fetch list of all config files we want to load.
        # First, get paths
        _manifest_path = CONST.YAML_MANIFEST_PATH
        _script_dir = os.path.dirname(os.path.dirname(__file__))
        _config_path = os.path.join(_script_dir, _manifest_path)
        config_manifest = self.yaml_loader(_config_path)

        # Create yaml doc generator, then convert it into a list of dicts.
        _configs_list = []
        for i in config_manifest:
            adjusted_path = os.path.join(_script_dir, i)
            _configs_list.append(self.yaml_loader(adjusted_path))


        #Create master config dictionary that will hold all of the game's config dictionaries.
        _master_config = {}
        for d in _configs_list:
            _master_config.update(d)

    @property
    def _master_config(self):
        return _master_config

    def yaml_loader(self, filepath):
        """Load a yaml file and return a list of the documents."""
        with open(filepath, "r") as file_descriptor:
            try:
                # Single-document yaml method.
                data = yaml.load(file_descriptor)
                return data
            except yaml.YAMLError:
                print("ConfigLoader(): tried to load yaml as single-document yaml, but found multiple documents. Trying multi-document load method.")
        # Multi-document yaml method must cast generator to list.
        with open(filepath, "r") as file_descriptor:
            data = list(yaml.load_all(file_descriptor))
            if not data:
                print("ERROR: Empty list yaml.")
            return data

    def yaml_dump(self, filepath, data):
        """Dump data to a yaml file."""
        with open(filepath, "w") as file_descriptor:
            yaml.dump(data, file_descriptor, default_flow_style=False)

if __name__ == "__main__":
    config = ConfigLoader()

    print(config._master_config)
