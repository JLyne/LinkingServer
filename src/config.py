import logging

import yaml
from yaml import SafeLoader

from linkingserver import stderrLogger

from book import Book

logger = logging.getLogger('config')
logger.addHandler(stderrLogger)
logger.setLevel(logging.INFO)

books = {}


def load_config():
    with open(r'./config.yml') as file:
        config = yaml.load(file, Loader=SafeLoader)
        book_config = config.get('books', {})

        secret = config.get('secret', '')

        if len(secret) == 0:
            raise TypeError("A linking secret must be provided in the config")

        unlinked = book_config.get('unlinked')
        unverified = book_config.get('unverified')

        if unlinked is None:
            raise TypeError("Unlinked book is missing from config")

        if unverified is None:
            raise TypeError("Unverified book is missing from config")

        books['unlinked'] = Book(unlinked.get('title', ''),
                              unlinked.get('author', ''),
                              unlinked.get('pages', []),
                              unlinked.get('bedrock_pages', []))

        books['unverified'] = Book(unverified.get('title', ''),
                                unverified.get('author', ''),
                                unverified.get('pages', []),
                                unverified.get('bedrock_pages', []))

        return {
            'books': books,
            'secret': secret
        }
