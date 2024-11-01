import ragImplementation as rag
from core.chatActions import add_chat_to_db, get_chat_from_db
from langchain_core.messages import  HumanMessage

def get_chat_history_for_ai(uid, session_id):
    chat_history = get_chat_from_db(uid, session_id, rant=True)
    new_messages = []
    if not chat_history:
        return new_messages
    else:
        for message in chat_history:
            if message['type'] == 'human':
                temp_message = message['message']
                new_messages.append(HumanMessage(content=temp_message))
            else:
                # message = message['message']
                temp_message = message['message']
                new_messages.append(temp_message)

        return new_messages

def save_session_embeddings(text, user_id, api_key, embeddings_path):
    docs = rag.create_docs(text)
    rag.create_embeddings_and_retriever(docs, api_key, user_id, embeddings_path)
    return "saved"

def create_retriever(embeddings_path, api_key):
    return rag.create_retriever(embeddings_path, api_key)

def load_model(retriever, api_key, uid, session_id):
    return rag.load_model(api_key, retriever, get_chat_history_for_ai(uid, session_id))

def letsTalk(message, model, uid, session_id):
    add_chat_to_db(uid, session_id, "user", message, {}, rant=True)
    response = model.invoke({"input": message})
    answer = response["answer"]
    print("Answer:", answer)
    add_chat_to_db(uid, session_id, "system", answer, {}, rant=True)
    return answer

def talkToMe(uid, session_id, message, api_key, embeddings_path):
    retriever = create_retriever(embeddings_path, api_key)
    model = load_model(retriever, api_key, uid, session_id)
    return letsTalk(message, model, uid, session_id)
    