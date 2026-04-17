import config_data as config
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
class VectorStoreService(object):
    def __init__(self, embedding: OpenAIEmbeddings):
        self.embedding = embedding

        self.vector_store = Chroma(
            collection_name=config.collection_name,
            persist_directory=config.persist_directory,
            embedding_function=self.embedding
        )

    def get_retriever(self):
        """获取向量数据库的检索器"""
        return self.vector_store.as_retriever(search_kwargs={"k": config.similarity_top_k})    