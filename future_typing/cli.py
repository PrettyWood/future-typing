from .codec import register


def cli():  # pragma: no cover
    """Command line to run the transform process directly on a file"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Support type hinting generics in standard collections and | as Union"
    )
    parser.add_argument("filename", help="the filename to parse and transform")
    args = parser.parse_args()

    with open(args.filename, "rb") as f:
        register()
        print(f.read().decode("future_typing"))
