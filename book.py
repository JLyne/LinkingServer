from quarry.types.nbt import TagString, TagList, TagCompound, TagRoot, TagInt


class Book:

    def __init__(self, title: str, author: list, pages: list, bedrock_pages: list):
        self.title = title
        self.author = author
        self.pages = pages
        self.bedrock_pages = bedrock_pages

    def nbt(self, token: str, bedrock: bool):
        pages = []

        if bedrock:
            for page in self.pages:
                pages.append(TagString(page.replace("[token]", token)))
        else:
            for page in self.pages:
                pages.append(TagString(page.replace("[token]", token)))

        return TagRoot({
            '': TagCompound({
                'resolved': TagInt(1),
                'generation': TagInt(2),
                'author': TagString(self.author),
                'title': TagString(self.title),
                'pages': TagList(pages)
            })
        })
