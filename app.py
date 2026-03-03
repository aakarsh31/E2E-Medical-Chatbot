#dependencies
from flask import Flask, render_template,request,jsonify
from src.helper import download_embeddings
from langchain_pinecone import PineconeVectorStore
from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain,create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from dotenv import load_dotenv
from src.prompt import *
import os

app = Flask(__name__)

load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

os.environ['PINECONE_API_KEY'] = PINECONE_API_KEY
os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

embeddings = download_embeddings()

index_name = 'ragmedibot'
docsearch =  PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings
)

chatModel = ChatOpenAI(model='gpt-4o')

retriever = docsearch.as_retriever(search_type = 'similarity',search_kwargs={"k":3})

contextualize_q_prompt = ChatPromptTemplate.from_messages(
[
("system",contextualize_q_system_prompt),
MessagesPlaceholder("chat_history"),
("human","{input}")
])

history_aware_retriever = create_history_aware_retriever(chatModel,retriever,contextualize_q_prompt)

qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}")
    ]
)

QA_chain = create_stuff_documents_chain(chatModel,qa_prompt)
rag_chain = create_retrieval_chain(history_aware_retriever,QA_chain)

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
    output_messages_key="answer"  # ← add this line
)

@app.route('/')
def index():
    return render_template('chat.html')

@app.route("/get",methods=['GET','POST'])
def chat():

    msg = request.form['msg']
    # temporary debug in /get route
    test_docs = history_aware_retriever.invoke({
    "input": msg,
    "chat_history": []
})
    print("HISTORY-AWARE RETRIEVED DOCS:", [d.page_content[:100] for d in test_docs])
    session_id = request.form["session_id"]
    print(msg)
    response = conversational_rag_chain.invoke({"input":msg},
                                               config={"configurable":{"session_id":session_id}})
    print("Response :", response["answer"])
    return jsonify({"answer": response['answer']})

if __name__ == '__main__':
    app.run(host='0.0.0.0',port = 8080,debug=True)




