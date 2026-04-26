from langchain_community.chat_message_histories import RedisChatMessageHistory
import os

def get_session_history(session_id, url=None):
    if url is None:
        url = os.getenv('REDIS_URL', 'redis://localhost:6379')
    history = RedisChatMessageHistory(session_id, url)
    return history