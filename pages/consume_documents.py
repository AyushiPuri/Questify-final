import os
import glob
from typing import List
from dotenv import load_dotenv
import streamlit as st

from langchain.document_loaders import (
    CSVLoader,
    EverNoteLoader,
    PDFMinerLoader,
    TextLoader,
    UnstructuredEmailLoader,
    UnstructuredEPubLoader,
    UnstructuredHTMLLoader,
    UnstructuredMarkdownLoader,
    UnstructuredODTLoader,
    UnstructuredPowerPointLoader,
    UnstructuredWordDocumentLoader,
)

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document
from constants import CHROMA_SETTINGS


# Map file extensions to document loaders and their arguments
LOADER_MAPPING = {
    ".csv": (CSVLoader, {}),
    # ".docx": (Docx2txtLoader, {}),
    ".doc": (UnstructuredWordDocumentLoader, {}),
    ".docx": (UnstructuredWordDocumentLoader, {}),
    ".enex": (EverNoteLoader, {}),
    ".eml": (UnstructuredEmailLoader, {}),
    ".epub": (UnstructuredEPubLoader, {}),
    ".html": (UnstructuredHTMLLoader, {}),
    ".md": (UnstructuredMarkdownLoader, {}),
    ".odt": (UnstructuredODTLoader, {}),
    ".pdf": (PDFMinerLoader, {}),
    ".ppt": (UnstructuredPowerPointLoader, {}),
    ".pptx": (UnstructuredPowerPointLoader, {}),
    ".txt": (TextLoader, {"encoding": "utf8"}),
    # Add more mappings for other file extensions and loaders as needed
}


load_dotenv()


def load_single_document(file_path: str) -> Document:
    ext = "." + file_path.rsplit(".", 1)[-1]
    if ext in LOADER_MAPPING:
        loader_class, loader_args = LOADER_MAPPING[ext]
        loader = loader_class(file_path, **loader_args)
        return loader.load()[0]

    raise ValueError(f"Unsupported file extension '{ext}'")


def load_documents(source_dir: str) -> List[Document]:
    # Loads all documents from source documents directory
    all_files = []
    for ext in LOADER_MAPPING:
        all_files.extend(
            glob.glob(os.path.join(source_dir, f"**/*{ext}"), recursive=True)
        )
    return [load_single_document(file_path) for file_path in all_files]


def main():
    # Load environment variables
    persist_directory = os.environ.get('PERSIST_DIRECTORY') or "db"
    source_directory = os.environ.get('SOURCE_DIRECTORY', 'source_documents')
    embeddings_model_name = os.environ.get('EMBEDDINGS_MODEL_NAME') or 'distilbert-base-uncased'

    # Load documents and split in chunks
    st.info(f"Loading documents from {source_directory}")
    chunk_size = 500
    chunk_overlap = 50
    documents = load_documents(source_directory)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    texts = text_splitter.split_documents(documents)
    st.info(f"Loaded {len(documents)} documents from {source_directory}")
    st.info(f"Split into {len(texts)} chunks of text (max. {chunk_size} characters each)")

    # Create embeddings
    embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)
    st.info(f"Creating embeddings for {len(texts)} chunks of text")
    # Create and store locally vectorstore
    st.info(f"Persisting vectorstore in {persist_directory}")
    db = Chroma.from_documents(texts, embeddings, persist_directory=persist_directory, client_settings=CHROMA_SETTINGS)
    # db.persist()
    db = None
    st.success("Documents processed and stored in vectorstore")

if __name__ == "__main__":

    st.title("Consume Documents")
    st.subheader("Load and process documents into a vectorstore for later retrieval using the questify chat interface.")
    st.warning("This script will load all documents from the source_documents directory, split them into chunks of text, and store them in a vectorstore for later retrieval.")
    if st.button("Load and process documents"):
        with st.spinner("Processing documents..."):
            main()

    # info
    with st.container(
        border=True
    ):
        st.write(f"Chunk size: {500}")
        st.write(f"Chunk overlap: {50}")
        st.write(f"Embeddings model: {os.environ.get('EMBEDDINGS_MODEL_NAME') or 'distilbert-base-uncased'}")
        st.write(f"Persist directory: {os.environ.get('PERSIST_DIRECTORY') or 'db'}")
        st.write(f"Source directory: {os.environ.get('SOURCE_DIRECTORY', 'source_documents')}")
        st.write(f"Collection name: {os.environ.get('COLLECTION_NAME', 'collection')}")
        st.write(f"Model type: {os.environ.get('MODEL_TYPE')}")
        st.write(f"Model path: {os.environ.get('MODEL_PATH')}")
