from operator import itemgetter

from file_history_store import (
    FileHistoryStore,
    build_history_file_path,
    list_history_session_ids,
)
from vector_store import VectorStoreService
import config_data as config
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory

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
                MessagesPlaceholder(variable_name="history"),
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

        chain = (
            {
                "context": itemgetter("question") | retriever | format_docs,
                "history": itemgetter("history"),
                "question": itemgetter("question"),
            }
            | self.prompt_template
            | self.chat_model
            | output_parser
        )

        return RunnableWithMessageHistory(
            chain,
            self.get_session_history,
            input_messages_key="question",
            history_messages_key="history"
        )

    def get_session_history(self, session_id: str) -> FileHistoryStore:
        history_file_path = build_history_file_path(
            config.history_store_dir,
            session_id
        )
        return FileHistoryStore(history_file_path)

    def invoke(self, question: str, session_id: str = config.default_session_id) -> str:
        return self.chain.invoke(
            {"question": question},
            config={"configurable": {"session_id": session_id}}
        )

    def get_history(self, session_id: str = config.default_session_id):
        return self.get_session_history(session_id).messages

    def clear_history(self, session_id: str = config.default_session_id) -> None:
        self.get_session_history(session_id).clear()

    def list_sessions(self):
        return list_history_session_ids(config.history_store_dir)
