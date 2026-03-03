from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from typing import List
from langchain.schema import Document


#Extract data from pdf file
def load_pdf_files(data):
    loader = DirectoryLoader(
        data,
        glob="*.pdf",
        loader_cls=PyPDFLoader
    )

    documents = loader.load()
    return documents



def filterer(docs: List[Document]) -> List[Document]:

    """Given List of documents, return Documents with 'source' only in the metadata along with the content"""
    
    filtered_docs:List[Document] = []
    for doc in docs:
        src = doc.metadata.get("source")
        filtered_docs.append(
            Document(
                page_content=doc.page_content,
                metadata={"source":src}
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