"""Exception adn error handler module"""

import logging


class PathNotFound(Exception):
    """Not found path in os"""


def handle_error(func):
    """Decorator function to handle errors"""

    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PathNotFound:
            logging.error("Path not found.")
        except PermissionError:
            logging.error("Permission denied for this folder.")
        except TypeError:
            logging.error("Opps...Some type not correct...")
        except Exception as e:  # disable it to show error
            logging.error("Opps...Some error happend...%s", e)

    return inner
