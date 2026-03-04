#dependencies
from flask import Flask, render_template,request,jsonify

from src.helper import download_embeddings,load_pdf_files,filterer,chunker
from src.prompt import *

from langchain_pinecone import PineconeVectorStore
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.retrievers import BM25Retriever
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain.retrievers import EnsembleRetriever
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

import os

app = Flask(__name__)

load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

os.environ['PINECONE_API_KEY'] = PINECONE_API_KEY
os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

embeddings = download_embeddings()

extracted_data = load_pdf_files(data='data/')
filtered_data = filterer(extracted_data)
chunked_data = chunker(filtered_data)

index_name = 'ragmedibot'
docsearch =  PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings
)

chatModel = ChatOpenAI(model='gpt-4o')

retriever = docsearch.as_retriever(search_type = 'similarity',search_kwargs={"k":5})

bm25_retriever = BM25Retriever.from_documents(chunked_data,k=5)

ensemble_retriever = EnsembleRetriever(retrievers=[retriever,bm25_retriever],weights=[0.5,0.5])

reranker_model = HuggingFaceCrossEncoder(model_name = 'cross-encoder/ms-marco-MiniLM-L-6-v2')
reranker = CrossEncoderReranker(model=reranker_model,top_n=5)

contextualize_q_prompt = ChatPromptTemplate.from_messages(
[
("system",contextualize_q_system_prompt),
MessagesPlaceholder("chat_history"),
("human","{input}")
])


qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}")
    ]
)


rag_chain = (
    RunnablePassthrough.assign(
        standalone_question=(contextualize_q_prompt | chatModel | StrOutputParser())
    )
    | RunnablePassthrough.assign(
        context=lambda x: reranker.compress_documents(
            ensemble_retriever.invoke(x['standalone_question']),
            x['standalone_question']
        )
    )
    | qa_prompt
    | chatModel
)

# SESSION STORE - store sessions across conversations
store = {}
def get_session_history(session_id):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

conversational_rag_chain = RunnableWithMessageHistory(
    rag_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)

@app.route('/')
def index():
    return render_template('chat.html')

@app.route("/get",methods=['GET','POST'])
def chat():

    msg = request.form['msg']
    session_id = request.form["session_id"]
    print(msg)
    response = conversational_rag_chain.invoke({"input":msg},
    config={"configurable":{"session_id":session_id}})
    print("Response :", response.content)
    return jsonify({"answer": response.content})

if __name__ == '__main__':
    app.run(host='0.0.0.0',port = 8080,debug=True)




