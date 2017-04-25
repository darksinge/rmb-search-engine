"""
Simply holds where things have happened.
"""
import os


def get_path():
    """
    Function to determine which path to use depending on environment.

    Returns:
        str: proper file path for the environment and os
    """
    try:
        env = os.environ['PYTHON_ENV']
    except KeyError:
        env = 'development'

    if env == 'production':
        return os.path.join('/var', 'www', 'rmb-search-engine')

    else:
        return ""


default_path = get_path()