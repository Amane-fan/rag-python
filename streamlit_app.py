import re
import time

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage

import config_data as config
from knowledge_base import KnowledgeBaseService
from rag import RagService


st.set_page_config(
    page_title="Amane RAG Assistant",
    page_icon="💬",
    layout="wide",
)


def get_knowledge_service() -> KnowledgeBaseService:
    if "knowledge_service" not in st.session_state:
        st.session_state["knowledge_service"] = KnowledgeBaseService()
    return st.session_state["knowledge_service"]


def get_rag_service() -> RagService:
    if "rag_service" not in st.session_state:
        st.session_state["rag_service"] = RagService()
    return st.session_state["rag_service"]


def normalize_session_id(session_id: str) -> str:
    normalized_session_id = session_id.strip() or config.default_session_id
    return re.sub(r"[^a-zA-Z0-9._-]", "_", normalized_session_id)


def ensure_current_session(rag_service: RagService) -> str:
    sessions = rag_service.list_sessions()
    current_session_id = normalize_session_id(
        st.session_state.get("current_session_id", config.default_session_id)
    )

    if current_session_id not in sessions and current_session_id != config.default_session_id:
        current_session_id = config.default_session_id

    st.session_state["current_session_id"] = current_session_id
    return current_session_id


def render_sidebar(rag_service: RagService, knowledge_service: KnowledgeBaseService) -> str:
    sessions = rag_service.list_sessions()
    current_session_id = ensure_current_session(rag_service)

    with st.sidebar:
        st.markdown("## 会话管理")

        new_session_id = st.text_input(
            "新会话 ID",
            placeholder="例如: product-docs",
            help="仅支持字母、数字、点号、下划线和中划线，其他字符会自动替换。",
        )
        if st.button("创建/切换会话", use_container_width=True):
            target_session_id = normalize_session_id(new_session_id or "")
            st.session_state["current_session_id"] = target_session_id
            rag_service.get_history(target_session_id)
            st.rerun()

        options = [config.default_session_id, *[sid for sid in sessions if sid != config.default_session_id]]
        session_index = options.index(current_session_id) if current_session_id in options else 0
        selected_session_id = st.selectbox(
            "历史会话",
            options=options,
            index=session_index,
        )
        if selected_session_id != current_session_id:
            st.session_state["current_session_id"] = selected_session_id
            st.rerun()

        if st.button("清空当前会话", use_container_width=True):
            rag_service.clear_history(st.session_state["current_session_id"])
            st.rerun()

        st.divider()
        st.markdown("## 知识库上传")
        uploaded_file = st.file_uploader(
            "选择一个文件上传",
            type=["txt", "md"],
        )

        if uploaded_file is not None:
            file_name = uploaded_file.name
            file_size = uploaded_file.size / 1024
            file_type = uploaded_file.type or "unknown"

            st.caption(f"文件名: {file_name}")
            st.caption(f"大小: {file_size:.2f} KB")
            st.caption(f"类型: {file_type}")

            text = uploaded_file.getvalue().decode("utf-8")
            st.text_area("文件内容预览", value=text[:500], height=180, disabled=True)

            if st.button("写入知识库", use_container_width=True):
                try:
                    with st.spinner("正在处理文件..."):
                        time.sleep(0.5)
                        result = knowledge_service.upload_by_str(text, file_name)
                    st.success(result)
                except Exception as exc:
                    st.error(f"文件处理失败: {exc}")

    return st.session_state["current_session_id"]


def render_message_history(rag_service: RagService, session_id: str) -> None:
    messages = rag_service.get_history(session_id)
    if not messages:
        with st.chat_message("assistant"):
            st.markdown(
                "你好，我已经连接到当前知识库。你可以直接提问，或先在左侧上传 `txt/md` 文档。"
            )
        return

    for message in messages:
        if isinstance(message, HumanMessage):
            role = "user"
        elif isinstance(message, AIMessage):
            role = "assistant"
        else:
            role = "assistant"

        with st.chat_message(role):
            st.markdown(message.content)


def main() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(215, 236, 255, 0.85), transparent 34%),
                linear-gradient(180deg, #f6f8fb 0%, #eef3f8 100%);
        }
        div[data-testid="stChatMessage"] {
            border: 1px solid rgba(15, 23, 42, 0.08);
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.82);
            backdrop-filter: blur(10px);
        }
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f172a 0%, #162033 100%);
        }
        section[data-testid="stSidebar"] * {
            color: #e5eef8;
        }
        section[data-testid="stSidebar"] .stButton > button {
            width: 100%;
            border: 1px solid rgba(148, 163, 184, 0.28);
            border-radius: 12px;
            background: linear-gradient(180deg, #eff6ff 0%, #dbeafe 100%);
            color: #0f172a !important;
            font-weight: 600;
            opacity: 1 !important;
        }
        section[data-testid="stSidebar"] .stButton > button:hover {
            border-color: rgba(96, 165, 250, 0.75);
            background: linear-gradient(180deg, #dbeafe 0%, #bfdbfe 100%);
            color: #020617 !important;
        }
        section[data-testid="stSidebar"] .stButton > button:disabled {
            opacity: 1 !important;
            color: #334155 !important;
            background: linear-gradient(180deg, #e2e8f0 0%, #cbd5e1 100%);
        }
        section[data-testid="stSidebar"] .stButton > button * {
            color: inherit !important;
            fill: currentColor !important;
            opacity: 1 !important;
        }
        section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
            background: rgba(248, 250, 252, 0.98);
            border: 1px solid rgba(148, 163, 184, 0.25);
        }
        section[data-testid="stSidebar"] div[data-baseweb="select"] * {
            color: #0f172a !important;
        }
        section[data-testid="stSidebar"] .stTextInput input {
            color: #0f172a;
            background: rgba(248, 250, 252, 0.98);
        }
        section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
            background: rgba(248, 250, 252, 0.96);
            border: 1px dashed rgba(148, 163, 184, 0.45);
        }
        section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] * {
            color: #0f172a !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    rag_service = get_rag_service()
    knowledge_service = get_knowledge_service()
    session_id = render_sidebar(rag_service, knowledge_service)

    st.title("Amane の RAG Chat")
    st.caption(f"当前会话: `{session_id}`")

    render_message_history(rag_service, session_id)

    question = st.chat_input("输入你的问题")
    if not question:
        return

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        try:
            with st.spinner("正在检索并生成回答..."):
                answer = rag_service.invoke(question, session_id=session_id)
            st.markdown(answer)
        except Exception as exc:
            st.error(f"回答生成失败: {exc}")
            return

    st.rerun()


if __name__ == "__main__":
    main()
