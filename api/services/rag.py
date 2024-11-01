import os

from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ..config import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o")


def load_pdf_to_documents(pdf_path):
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()
    return docs


def create_rag_service(docs):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)

    vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())
    retriever = vectorstore.as_retriever()

    system_prompt = (
        "You are an assistant for question-answering tasks. "
        "Use the following pieces of retrieved context to answer "
        "the question. If you don't know the answer, say that you "
        "don't know. Use three sentences maximum and keep the "
        "answer concise."
        "\n\n"
        "{context}"
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
        ]
    )

    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    return rag_chain


def answer_question(pdf_path: str, user_question: str):
    docs = load_pdf_to_documents(pdf_path)
    rag_chain = create_rag_service(docs)

    result = rag_chain.invoke({"input": user_question})

    answer = result.get("answer", "Sorry, I couldn’t find an answer to your question.")

    return answer
