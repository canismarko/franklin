from pathlib import Path
import configparser


class FranklinConfig(configparser.ConfigParser):
    default_filename = Path("~/.franklinrc").expanduser()

    def read(self, filenames=None, *args, **kwargs):
        if filenames is None:
            filenames = self.default_filename
        return super().read(filenames, *args, **kwargs)


franklin_config = FranklinConfig()


def load_config():
    """Load the configuration file from disk."""
    config = configparser.ConfigParser()
    config['Elsevier'] = {
        'api_key': '',
    }
    # Read the file from disk
    config.read(os.path.expanduser('~/.franklinrc'))
    return config
