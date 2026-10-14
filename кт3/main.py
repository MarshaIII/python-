def get_books(filename: str) -> list[list]:
    with open(filename, 'r', encoding='utf-8') as f:
        lines = map(str.strip, f.readlines())

    data_lines = filter(
        lambda line: line
                     and not line.startswith('isbn|')
                     and len(line.split('|')) == 5,
        lines
    )

    books = map(lambda line: line.split('|'), data_lines)
    books = map(lambda parts: [
        parts[0],
        parts[1],
        parts[2],
        int(parts[3]),
        float(parts[4])
    ], books)

    return list(books)


def filtered_books(books: list[list], substring: str) -> list[list]:
    substring_lower = substring.lower()

    filtered = filter(lambda book: substring_lower in book[1].lower(), books)

    result = map(lambda book: [
        book[0],
        f"{book[1]}, {book[2]}",
        book[3],
        book[4]
    ], filtered)

    return list(result)


def total_prices(books: list[list]) -> list[tuple]:
    return list(map(lambda book: (book[0], book[2] * book[3]), books))


books = get_books("books.csv")
filtered = filtered_books(books, "python")
prices = total_prices(filtered)
print(prices)