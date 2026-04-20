from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

classifier_prompt = """Identify the given statement as a medical, off_topic, harmful, return only 1 of these 3 labels, no additional wording."""

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