import weaviate.classes.config as wvc
COLLECTION_NAME = "Memory"

def createMemoryCollection(client):
    client.collections.create(
        # "class" from v3 becomes the 'name'
        name=COLLECTION_NAME,

        # "description" is a top-level argument
        description="A node representing a single piece of memory.",

        # "vectorizer": "none" becomes this configuration object
        vectorizer_config=wvc.Configure.Vectorizer.none(),

        # The "properties" list is now a list of Property objects
        properties=[
            wvc.Property(
                name="shortDescription",
                data_type=wvc.DataType.TEXT,
                description="A one-sentence summary of the memory.",
            ),
            wvc.Property(
                name="mediumDescription",
                data_type=wvc.DataType.TEXT,
                description="A one-paragraph summary of the memory.",
            ),
            wvc.Property(
                name="longDescription",
                data_type=wvc.DataType.TEXT,
                description="The full, detailed content of the memory.",
            ),
            wvc.Property(
                name="timestamp",
                data_type=wvc.DataType.DATE,
                description="When the memory was created.",
            )
        ]
    )
