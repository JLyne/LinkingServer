import json

from quarry.types.chat import Message
from quarry.types.nbt import TagRoot


class Book:

    def __init__(self, title: str, author: list, pages: list, bedrock_pages: list):
        self.title = title
        self.author = author
        self.pages = pages
        self.bedrock_pages = bedrock_pages

    def _pages(self, token: str, bedrock: bool, string=False):
        pages = []

        if bedrock:
            for page in self.bedrock_pages:
                content = page.replace("[token]", token)
                pages.append(content if string else Message(json.loads(content)))
        else:
            for page in self.pages:
                content = page.replace("[token]", token)
                pages.append(content if string else Message(json.loads(content)))

        return pages

    def nbt(self, token: str, bedrock: bool):
        return TagRoot.from_obj({
            'resolved': 1,
            'generation': 2,
            'author': self.author,
            'title': self.title,
            'pages': self._pages(token, bedrock, True)
        })

    def structured_data(self, token: str, bedrock: bool):
        return {
            'written_book_content': {
                'resolved': True,
                'generation': 2,
                'author': self.author,
                'title': {
                    'raw': self.title
                },
                'pages': self._pages(token, bedrock)
            }
        }
