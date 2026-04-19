from langchain_community.chat_message_histories import RedisChatMessageHistory

def get_session_history(session_id,url='redis://localhost:6379'):
    history = RedisChatMessageHistory(session_id,url)
    return history

