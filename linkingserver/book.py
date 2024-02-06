from quarry.types.nbt import TagRoot


class Book:

    def __init__(self, title: str, author: list, pages: list, bedrock_pages: list):
        self.title = title
        self.author = author
        self.pages = pages
        self.bedrock_pages = bedrock_pages

    def nbt(self, token: str, bedrock: bool):
        pages = []

        if bedrock:
            for page in self.bedrock_pages:
                pages.append(page.replace("[token]", token))
        else:
            for page in self.pages:
                pages.append(page.replace("[token]", token))

        return TagRoot.from_obj({
            'resolved': 1,
            'generation': 2,
            'author': self.author,
            'title': self.title,
            'pages': pages
        })
