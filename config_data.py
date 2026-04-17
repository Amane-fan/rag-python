import os
from dotenv import load_dotenv

load_dotenv()

md5_path = "./md5.text"

# chroma
collection_name = "rag"
persist_directory = "./chroma_db"
chunks_limit_size = 10 #限制embedding请求批大小
history_store_dir = "./chat_history"
default_session_id = "default"

# spliter
chunk_size = 1000
chunk_overlap = 100
separators = ["\n\n", "\n", " ", ".", ",", "，", "。", "！", "?", "？"]
max_split_char_number = 1000

# model
embedding_model = "text-embedding-v4"
chat_model = "qwen-plus"
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
DASHSCOPE_BASE_URL = os.getenv("DASHSCOPE_BASE_URL")

# 
similarity_top_k = 5         #相似度检索时返回的top k个结果
