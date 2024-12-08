from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents.base import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ..config import settings


def load_pdf_to_documents(pdf_path):
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()
    return docs


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def create_rag_service(docs: list[Document]):
    RAG_TEMPLATE = """
    You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.

    <context>
    {context}
    </context>

    Answer the following question:

    {question}
    """

    prompt = ChatPromptTemplate.from_template(RAG_TEMPLATE)

    model = ChatOllama(base_url=settings.OLLAMA_URL, model=settings.OLLAMA_MODEL)

    local_embeddings = OllamaEmbeddings(model="nomic-embed-text")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
    all_splits = text_splitter.split_documents(docs)

    vectorstore = Chroma.from_documents(
        documents=all_splits, embedding=local_embeddings
    )

    retriever = vectorstore.as_retriever()

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | model
        | StrOutputParser()
    )

    return chain


def answer_question(pdf_path: str, question: str):
    docs = load_pdf_to_documents(pdf_path)
    chain = create_rag_service(docs)
    answer = chain.invoke(question)

    return answer
