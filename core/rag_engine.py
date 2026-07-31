import os

try:
    from langchain_mistralai import ChatMistralAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.runnables import RunnablePassthrough, RunnableLambda
except Exception as exc:
    ChatMistralAI = None
    ChatPromptTemplate = None
    StrOutputParser = None
    RunnablePassthrough = None
    RunnableLambda = None
    _LANGCHAIN_IMPORT_ERROR = exc
else:
    _LANGCHAIN_IMPORT_ERROR = None

from core.vector_store import build_vector_store, load_vector_store, get_retriever


def _require_langchain():
    if _LANGCHAIN_IMPORT_ERROR is not None:
        raise RuntimeError("LangChain dependencies are not available. Please install requirements first.") from _LANGCHAIN_IMPORT_ERROR


def get_llm():
    _require_langchain()
    return ChatMistralAI(
        model="mistral-small-latest",
        mistral_api_key=os.getenv("MISTRAL_API_KEY"),
        temperature=0.3,
    )


def format_docs(docs):
    return "\n\n".join([doc.page_content for doc in docs])


def build_rag_chain(transcript: str):
    _require_langchain()
    vector_store = build_vector_store(transcript)
    retriever = get_retriever(vector_store, k=4)
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert meeting assistant. Answer the user's question "
                   "based ONLY on the meeting transcript context provided below.\n\n"
                   "If the answer is not found in the context, say: "
                   '"I could not find this information in the meeting transcript."\n\n'
                   "Always be concise and precise. If quoting someone, mention it clearly.\n\n"
                   "Context from meeting transcript:\n{context}"),
        ("human", "{question}"),
    ])
    rag_chain = (
        {"context": retriever | RunnableLambda(format_docs), "question": RunnablePassthrough()}
        | prompt | llm | StrOutputParser()
    )
    return rag_chain


def load_rag_chain():
    _require_langchain()
    vector_store = load_vector_store()
    retriever = get_retriever(vector_store)
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert meeting assistant. Answer the user's question "
                   "based ONLY on the meeting transcript context provided below.\n\n"
                   "If the answer is not found in the context, say: "
                   '"I could not find this information in the meeting transcript."\n\n'
                   "Always be concise and precise. If quoting someone, mention it clearly.\n\n"
                   "Context from meeting transcript:\n{context}"),
        ("human", "{question}"),
    ])
    rag_chain = (
        {"context": retriever | RunnableLambda(format_docs), "question": RunnablePassthrough()}
        | prompt | llm | StrOutputParser()
    )
    return rag_chain


def ask_question(rag_chain, question: str) -> str:
    print(f"Question: {question}")
    answer = rag_chain.invoke(question)
    print(f"Answer: {answer}")
    return answer
