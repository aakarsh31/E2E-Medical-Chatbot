from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from typing import List
from langchain.schema import Document
import os

#Extract data from pdf file
def load_pdf_files(data):
    loader = DirectoryLoader(
        data,
        glob="*.pdf",
        loader_cls=PyPDFLoader
    )

    documents = loader.load()
    return documents



def filterer(docs: List[Document], state_map: dict) -> List[Document]:

    """Given List of documents, return Documents with 'source' and 'Page' only in the metadata along with the content"""
    
    filtered_docs:List[Document] = []
    for doc in docs:
        src = doc.metadata.get("source")
        filename = os.path.basename(src)
        state_abbr = filename.split("_")[0]
        state = state_map.get(state_abbr, "Unknown")
        page = int(doc.metadata.get("page", 0))
        filtered_docs.append(
            Document(
                page_content=doc.page_content,
                metadata={"source":src,
                          "page":page,
                          "state": state}
            )
        )
    return filtered_docs

#Split data into fixed size chunks
def chunker(filtered_docs):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 500,
        chunk_overlap=20,
    )
    texts_chunked = text_splitter.split_documents(filtered_docs)
    return texts_chunked

def download_embeddings():
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    
    embeddings = HuggingFaceEmbeddings(
        model_name = model_name
    )
    return embeddings