import yaml
from dateutil.parser import parse


def read_config(path: str) -> dict:
    """
    Read and parse YAML config file.

    :param path: filepath to YAML config file
    :return: dictionary with config settings
    """
    with open(path) as fin:
        data = yaml.load(fin)

    return data


def is_date(string: str, fuzzy: bool = False) -> bool:
    """
    Return whether the string can be interpreted as a date.

    :param string: string to check for date
    :param fuzzy: ignore unknown tokens in string if True
    :return: True if string can be interpreted as a date else False
    """
    try:
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False
