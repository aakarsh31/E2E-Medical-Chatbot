from src.helper import download_embeddings
from src.prompt import system_prompt
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

load_dotenv()
embeddings = download_embeddings()
index_name = 'counselai'
docsearch =  PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings
)

retriever = docsearch.as_retriever(search_type = 'similarity',search_kwargs={"k":5})

chat_model = ChatOpenAI(model='gpt-4o')

qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}")
    ]
)

baseline_chain = (
    RunnablePassthrough.assign(
        context=lambda x: retriever.invoke(x["input"])
    )
    | qa_prompt
    | chat_model
    | StrOutputParser()
)
        
dataset = [] 
for i in test_questions:
    response = baseline_chain.invoke({"input":i["user_input"]})
    docs = retriever.invoke(i["user_input"])
    contexts = [doc.page_content for doc in docs]
    dataset.append({
    "user_input": i["user_input"],
    "retrieved_contexts": contexts,
    "response": response,
    "reference": i["reference"]
})

ragaset = EvaluationDataset.from_list(dataset)

evaluator_model = ChatOpenAI(model='gpt-4o-mini')
evaluator = LangchainLLMWrapper(evaluator_model)
result = evaluate(
    dataset=ragaset,
    metrics=[LLMContextRecall(), Faithfulness(), LLMContextPrecisionWithReference(), ResponseRelevancy()],
    llm=evaluator
)

scores = result.to_pandas().select_dtypes(include='number').mean().to_dict()
with open('eval/results/baseline_scores.json', 'w') as f:
    json.dump(scores, f, indent=2)
print("Baseline scores:", scores)

