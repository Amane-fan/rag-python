from vector_store import VectorStoreService
import config_data as config
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

class RagService(object):
    def __init__(self):
        self.vector_store_service = VectorStoreService(
            embedding=OpenAIEmbeddings(
                model=config.embedding_model,
                base_url=config.DASHSCOPE_BASE_URL,
                api_key=config.DASHSCOPE_API_KEY,
                check_embedding_ctx_length=False,
                chunk_size=config.chunks_limit_size
            )
        )
        
        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", "以我提供的资料为主，简洁专业地回答我的问题，参考资料:\n\n{context}\n\n"),
                ("human", "{question}")
            ]
        )

        self.chat_model = ChatOpenAI(
            model=config.chat_model,
            base_url=config.DASHSCOPE_BASE_URL,
            api_key=config.DASHSCOPE_API_KEY
        )

        self.chain = self.get_chain()

    def get_chain(self):
        retriever = self.vector_store_service.get_retriever()
        output_parser = StrOutputParser()

        # 规定检索到文档后，如何将文档内容拼接到context中，作为系统提示词的输入
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        return (
            {
                "context": retriever | format_docs,
                "question": RunnablePassthrough(),
            }
            | self.prompt_template
            | self.chat_model
            | output_parser
        )
