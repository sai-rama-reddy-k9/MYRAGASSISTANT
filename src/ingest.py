import os
import torch
import chromadb
import shutil
from src.paths import VECTOR_DB_DIR
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
# from utils import load_all_publications
# from utils import load_publications_from_json
from src.utils import load_publication
from src.paths import PUBLICATION_FPATH



device = (
    "cuda"
    if torch.cuda.is_available()
    else "mps" if torch.backends.mps.is_available() else "cpu"
)
embeddings_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": device},
)

def initialize_db(
    persist_directory: str = VECTOR_DB_DIR,
    collection_name: str = "publications",
    delete_existing: bool = False,
) -> chromadb.Collection:
    if os.path.exists(persist_directory) and delete_existing:
        #made a change here
        if delete_existing and os.path.exists(persist_directory):
            shutil.rmtree(persist_directory, ignore_errors=True)

    os.makedirs(persist_directory, exist_ok=True)

    # Initialize ChromaDB client with persistent storage
    client = chromadb.PersistentClient(path=persist_directory)

    # Create or get a collection
    try:
        # Try to get existing collection first
        collection = client.get_collection(name=collection_name)
        print(f"Retrieved existing collection: {collection_name}")
    except Exception:
        # If collection doesn't exist, create it
        collection = client.create_collection(
            name=collection_name,
            metadata={
                "hnsw:space": "cosine",
                "hnsw:batch_size": 10000,
            },  # Use cosine distance for semantic search
        )
        print(f"Created new collection: {collection_name}")

    print(f"ChromaDB initialized with persistent storage at: {persist_directory}")

    return collection

def get_db_collection(
    persist_directory: str = VECTOR_DB_DIR,
    collection_name: str = "publications",
):
    return chromadb.PersistentClient(path=persist_directory).get_collection(
        name=collection_name
    )

def chunk_publication(publication, chunk_size = 1000, chunk_overlap = 200):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return text_splitter.split_text(publication)

def embed_documents(documents):
    return embeddings_model.embed_documents(documents)

def insert_publications(collection, publications):
    next_id = collection.count()
    for publication in publications:
        chunked_publication = chunk_publication(publication)
        embeddings = embed_documents(chunked_publication)
        ids = list(range(next_id, next_id + len(chunked_publication)))
        ids = [f"document_{id}" for id in ids]
        metadatas = [{"source": "publication", "chunk_index": i} for i in range(len(chunked_publication))]

        collection.add(
            embeddings=embeddings,
            ids=ids,
            documents=chunked_publication,
            metadatas=metadatas,
        )
        next_id += len(chunked_publication)

def main():
    collection = initialize_db(
        persist_directory=VECTOR_DB_DIR,
        collection_name="publications",
        delete_existing=True, # Change to True to reset the DB
    )
    # if os.path.exists(PUBLICATIONS_JSON_FPATH):
    #     publications = load_publications_from_json(PUBLICATIONS_JSON_FPATH)
    # else:
    #     publications = load_all_publications()
    # insert_publications(collection, publications)

    # print(f"Total documents in collection: {collection.count()}")
    
    publication = load_publication()
    insert_publications(collection, [publication])  # wrap in list since insert expects multiple

    print(f"Total documents in collection: {collection.count()}")

if __name__ == "__main__":
    main()
