import os
import config_data as config
import hashlib
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from datetime import datetime

def check_md5(md5_str: str):
    """检查传入的md5字符串是否被处理过"""
    if not os.path.exists(config.md5_path):
        # 如果md5记录文件不存在，则创建一个空文件
        open(config.md5_path, "w", encoding="utf-8").close()
        return False
    else:
        for line in open(config.md5_path, "r", encoding="utf-8").readlines():
            line = line.strip()
            # 如果传入的md5字符串在文件中已经存在，则返回True
            if line == md5_str:
                return True
        return False

def save_md5(md5_str: str):
    """将传入的md5字符串记录到文件内保存"""
    with open(config.md5_path, "a", encoding="utf-8") as f:
        f.write(md5_str + "\n")

def get_string_md5(input_str: str, encoding="utf-8"):
    """获取字符串的md5值"""
    input_str.encode(encoding)
    md5_obj = hashlib.md5()
    md5_obj.update(input_str.encode(encoding))
    md5_str = md5_obj.hexdigest()
    return md5_str

class KnowledgeBaseService(object):
    def __init__(self):
        # 初始化Chroma数据库和文本分割器
        self.chroma = Chroma(
            collection_name=config.collection_name, 
            persist_directory=config.persist_directory,
            embedding_function=OllamaEmbeddings(model=config.embedding_model_name)
        )
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size, 
            chunk_overlap=config.chunk_overlap,
            separators=config.separators,
            length_function=len
        )
    
    def upload_by_str(self, data: str, filename: str):
        """将传入的字符串向量化后存入数据库中"""
        md5_str = get_string_md5(data)
        if check_md5(md5_str):
            return f"{filename} 已存在，跳过处理..."
        
        # 存入md5
        save_md5(md5_str)

        # 若在一定阈值内，则不需要分块
        chunks = []
        meta_data = {
            "source": filename,
            "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operator": "Amane"
        }
        if len(data) > config.max_split_char_number:
            chunks = self.spliter.split_text(data)
        else:
            chunks = [data]
        # 加入向量库
        self.chroma.add_texts(chunks, metadatas=[meta_data for _ in chunks])
        return f"{filename} 处理完成，已存入数据库中..."
    
if __name__ == "__main__":
    service = KnowledgeBaseService()
    result = service.upload_by_str("Amaneの测试", "test.txt")
    print(result)