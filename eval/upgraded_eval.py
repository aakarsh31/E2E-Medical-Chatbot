from eval.test_questions import test_questions
from langchain_pinecone import PineconeVectorStore
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from ragas import evaluate, EvaluationDataset
from ragas.metrics import LLMContextRecall, Faithfulness, LLMContextPrecisionWithReference, ResponseRelevancy
from ragas.llms import LangchainLLMWrapper
from dotenv import load_dotenv
import json
import uuid

from src.helper import download_embeddings, load_pdf_files, filterer, chunker
from src.prompt import system_prompt, contextualize_q_system_prompt
from langchain_community.retrievers import BM25Retriever
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain.retrievers import EnsembleRetriever
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import MessagesPlaceholder

load_dotenv()

extracted_data = load_pdf_files(data='data/')
filtered_data = filterer(extracted_data)
chunked_data = chunker(filtered_data)

embeddings = download_embeddings()

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

dataset = []
for idx, q in enumerate(test_questions):
    if q["type"] == "conversational":
        session_id = "conv_session"
    else:
        session_id = str(uuid.uuid4())
    
    response = conversational_rag_chain.invoke(
        {"input": q["user_input"]},
        config={"configurable": {"session_id": session_id}}
    ).content
    
    docs = ensemble_retriever.invoke(q["user_input"])
    contexts = [doc.page_content for doc in docs]
    
    dataset.append({
        "user_input": q["user_input"],
        "retrieved_contexts": contexts,
        "response": response,
        "reference": q["reference"]
    })

# RAGAS evaluation — comes after loop
ragaset = EvaluationDataset.from_list(dataset)
evaluator = LangchainLLMWrapper(chatModel)
result = evaluate(
    dataset=ragaset,
    metrics=[LLMContextRecall(), Faithfulness(), LLMContextPrecisionWithReference(), ResponseRelevancy()],
    llm=evaluator
)

scores = result.to_pandas().select_dtypes(include='number').mean().to_dict()
with open('eval/results/upgraded_scores.json', 'w') as f:
    json.dump(scores, f, indent=2)
print("Upgraded scores:", scores)