"""Exception adn error handler module"""

import logging


class PathNotFound(Exception):
    """Not found path in os"""


def handle_error(func):
    """Decorator function to handle errors"""

    async def inner(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except PathNotFound:
            logging.error("Path not found.")
        except PermissionError:
            logging.error("Permission denied for this folder.")
        except TypeError:
            logging.error("Opps...Some type not correct...")
        except FileNotFoundError as e:
            logging.error("File not found error... %s", e)
        except Exception as e:  # pylint: disable=W0703
            logging.error("Opps...Some error happend...%s", e)

    return inner
