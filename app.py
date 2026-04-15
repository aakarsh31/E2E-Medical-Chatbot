#dependencies
from flask import Flask, render_template,request,jsonify, Response

from src.helper import download_embeddings,load_pdf_files,filterer,chunker
from src.prompt import *

from langchain_pinecone import PineconeVectorStore
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.retrievers import BM25Retriever
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain.retrievers import EnsembleRetriever
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import logger as _logger_config  #Triggers only basicConfig
import logging
import os

logger = logging.getLogger(__name__)
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

def get_session_history(session_id,url='redis://localhost:6379'):
    history = RedisChatMessageHistory(session_id,url)
    return history

conversational_rag_chain = RunnableWithMessageHistory(
    rag_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)

@app.route('/')
def index():
    return render_template('chat.html')

@app.route("/get", methods=['GET', 'POST'])
def chat():
    try:
        msg = request.form['msg']
        if not msg:
            return jsonify({"error":"Empty user message"}), 400
        session_id = request.form["session_id"]
        logger.info(f"Received user message: {msg}")
    except Exception as e:
        logger.warning(f'Invalid request: {e}')
        return jsonify({"error": "Invalid/Empty user message"}), 400

    try:
        response = conversational_rag_chain.stream(
            {"input": msg},
            config={"configurable": {"session_id": session_id}}
        )
    except Exception as e:
        logger.error(f"Pipeline failure: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

    def generate():
        for chunk in response:
            if chunk.content:
                yield f"data: {chunk.content}\n\n"
        yield "data: [DONE]\n\n"

    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0',port = 8080,debug=True)


