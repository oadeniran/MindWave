from langchain.docstore.document import Document
import os
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate


def create_docs(text,):
    docs = []
    for i, text in enumerate(text):
        docs.append(Document(text, metadata={"id": i}))
    return docs

def create_embeddings_and_retriever(docs, api_key, user_id, embeddings_path):
    # Concatenate user ID and session ID for the embeddings directory
    persist_dir = f'{embeddings_path}/{user_id}'
    
    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    
    # Create embeddings and persist them
    vectorstore = Chroma.from_documents(documents=splits, persist_directory=persist_dir, embedding=OpenAIEmbeddings(api_key=api_key))
    
    # Create retriever from the vector store
    retriever = vectorstore.as_retriever()
    
    return retriever


def create_retriever(embeddings_path, api_key):
    if os.path.exists(embeddings_path):
        vstore = Chroma(persist_directory=embeddings_path, embedding_function=OpenAIEmbeddings(api_key=api_key))
    else:
        vstore = Chroma(embedding_function=OpenAIEmbeddings(api_key=api_key))
    return vstore.as_retriever()

def load_model(api_key, retriever, chat_history):
    llm = ChatOpenAI(api_key=api_key, model="gpt-4o-mini")

    system_prompt = (
    "You are a compassionate therapist, helping users talk about their emotions and providing support to help them feel better. "
    "You have access to the user's previous tests and can remember past conversations to provide more personalized guidance. "
    "When responding, acknowledge the user's feelings and offer thoughtful, emotionally supportive responses. "
    "If you feel the context is unclear, ask gentle, open-ended questions to better understand the user. "
    "Keep your tone empathetic and aim to help the user feel heard and understood."
    "When there is no message from user and chat history, you can start the conversation by asking something interesting based on context or generally."
    "\n\n"
    "{context}"
    "\n\n"
    "Chat History"
    f"{chat_history}"
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