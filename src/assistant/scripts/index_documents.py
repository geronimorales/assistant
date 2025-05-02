from assistant.core.llamaindex import indexer


def main():
    print("Indexing documents")
    indexer.generate()


if __name__ == "__main__":
    main()
