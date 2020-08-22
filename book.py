from quarry.types.nbt import TagString, TagList, TagCompound, TagRoot, TagInt

def unlinked_book(token, bedrock=False):
    book_pages = []

    if bedrock:
        from books.unlinked_bedrock import pages

        for page in pages:
            book_pages.append(TagString(page.replace("[token]", token)))

    else :
        from books.unlinked import pages

        for page in pages:
            book_pages.append(TagString(page.replace("[token]", token)))

    return TagRoot({
            '': TagCompound({
                'resolved': TagInt(1),
                'generation': TagInt(2),
                'author': TagString("NotKatuen"),
                'title': TagString("Linking Instructions"),
                'pages': TagList(book_pages)
            })
    })

def unverified_book(token, bedrock=False):
    book_pages = []

    if bedrock:
        from books.unverified_bedrock import pages

        for page in pages:
            book_pages.append(TagString(page.replace("[token]", token)))

    else :
        from books.unverified import pages

        for page in pages:
            book_pages.append(TagString(page.replace("[token]", token)))

    return TagRoot({
            '': TagCompound({
                'resolved': TagInt(1),
                'generation': TagInt(2),
                'author': TagString("NotKatuen"),
                'title': TagString("Role Missing"),
                'pages': TagList(book_pages)
            })
    })