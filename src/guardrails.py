from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

classifier_prompt = """Identify the given statement as a legal, off_topic, harmful, return only 1 of these 3 labels, no additional wording.
Only label as 'harmful' if the query explicitly seeks to cause physical harm, harass, stalk, facilitate illegal violence, or obtain an illegal or harmful outcome against a person. This includes queries that seek to misuse legal processes to harm others (e.g. filing false charges, making false accusations, using legal mechanisms to harass).
If a query contains harmful intent anywhere in the message, label it as 'harmful' — this takes priority over all other labels.
If a query contains both a legal question AND an off_topic question with no harmful intent, label it as 'off_topic'.
Legal disputes, tenant issues, employment conflicts, and criminal procedure questions are always 'legal' even if adversarial in nature."""

qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", classifier_prompt),
        ("human", "{query}")
    ]
)
chatModel = ChatOpenAI(model='gpt-4o-mini')
chain = qa_prompt | chatModel

def guardrail(query):
    
    reponse = chain.invoke({"query": query})
    return reponse.content.strip().lower()