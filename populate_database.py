import argparse
import os
import shutil
import json
from langchain.document_loaders.pdf import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from get_embedding_function import get_embedding_function
from langchain_chroma import Chroma
import urllib



CHROMA_PATH = "chroma"
DATA_PATH = "docs"

local_to_web_mapping = {
    "data\\ffug.pdf": "https://docs.oracle.com/cd/A60725_05/pdf/ffug.pdf",
    "data\\ffg2.pdf": "https://docs.oracle.com/en/cloud/saas/human-resources/24d/oapff/administering-fast-formulas.pdf",
    # Add more mappings as needed
}


def populate():

    # Check if the database should be cleared (using the --clear flag).
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    args = parser.parse_args()
    if args.reset:
        print("✨ Clearing Database")
        clear_database()

    # Create (or update) the data store.
    documents = load_documents()
    chunks = split_documents(documents)
    i = 0
    while i < len(chunks):
        if i + 1 < len(chunks) and not chunks[i + 1].page_content.startswith(' ##'):
            chunks[i].page_content += chunks[i + 1].page_content
            chunks.pop(i + 1)
            i -= 1
        i += 1
    add_to_chroma(chunks)


def load_documents():
    document_loader = PyPDFDirectoryLoader(DATA_PATH)
    return document_loader.load()


def split_documents(documents: list[Document]):
    # text_splitter = RecursiveCharacterTextSplitter(
    #     chunk_size=800,
    #     chunk_overlap=80,
    #     length_function=len,
    #     is_separator_regex=False,
    # )
    # return text_splitter.split_documents(documents)
    text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,
    chunk_overlap=100,
    length_function = len,
    is_separator_regex = True,
    separators=[" ##"]
    )
    return text_splitter.split_documents(documents)


def add_to_chroma(chunks: list[Document]):
    # Load the existing database.
    db = Chroma(
        collection_name="docs_collection",persist_directory=CHROMA_PATH, embedding_function=get_embedding_function()
    )

    # Calculate Page IDs.
    chunks_with_ids = calculate_chunk_ids(chunks)

    # Add or Update the documents.
    existing_items = db.get(include=[])  # IDs are always included by default
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    # Only add documents that don't exist in the DB.
    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks):
        print(f"👉 Adding new documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)
        #db.persist()
    else:
        print("✅ No new documents to add")


def calculate_chunk_ids(chunks):
    # This will create IDs like "data/monopoly.pdf:6:2"
    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"
        if source:
            base_path = "/hackathon"
            file_path = os.path.join(base_path, source).replace("\\", "/")
            local_file_path = urllib.parse.quote(file_path)
            page_link = f"file:///D:{local_file_path}#page={page}"
            chunk.metadata["page_link"] = page_link
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id
        chunk.metadata["id"] = chunk_id

    return chunks

def load_prompts():
    with open("docs/documents.json", "r") as file:
        documents_data = json.load(file)

# Recreate Document objects
    promptDocuments = [
        Document(page_content=doc["page_content"], metadata=doc["metadata"])
        for doc in documents_data
    ]
    add_to_chroma(promptDocuments)


# Function to convert local link to web link
def convert_to_web_link(local_source):
    return local_to_web_mapping.get(local_source)

def on_error(func, path, exc_info):
    import stat
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise

def clear_database():
    db = Chroma(
        collection_name="docs_collection",persist_directory=CHROMA_PATH, embedding_function=get_embedding_function()
    )
    db.delete_collection()
    if os.path.exists(DATA_PATH):
        try:
            shutil.rmtree(DATA_PATH)
            print(f"Deleted: {DATA_PATH}")
        except Exception as e:
            print(f"Failed to delete {DATA_PATH}: {e}")



