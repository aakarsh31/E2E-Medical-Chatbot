from dotenv import load_dotenv
import os
from src.helper import load_pdf_files,chunker,filterer, download_embeddings

from pinecone import Pinecone
from pinecone import ServerlessSpec
from langchain_pinecone import PineconeVectorStore


load_dotenv()
embeddings = download_embeddings()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

os.environ['PINECONE_API_KEY'] = PINECONE_API_KEY
os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

extracted_data = load_pdf_files(data='data/')
filtered_data = filterer(extracted_data)
chunked_data = chunker(filtered_data)

pinecone_api_key = PINECONE_API_KEY
pc = Pinecone(api_key=pinecone_api_key)

index_name = "ragmedibot"

if not pc.has_index(index_name):
    pc.create_index(
        name = index_name,\
        dimension=384,
        metric= 'cosine',
        spec = ServerlessSpec(cloud='aws', region = 'us-east-1')
    )

index = pc.Index(index_name)

docsearch = PineconeVectorStore.from_documents(
    documents=chunked_data,
    embedding=embeddings,
    index_name=index_name
)