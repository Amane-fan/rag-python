import streamlit as st
from knowledge_base import KnowledgeBaseService
import time

st.title("Amaneの文件上传")

uploaded_file = st.file_uploader(
    "选择一个文件上传",
    type=["txt", "md", "pdf"],
)

# 确保service单例
if "service" not in st.session_state:
    st.session_state["service"] = KnowledgeBaseService()


if uploaded_file is not None:
    file_name = uploaded_file.name
    file_size = uploaded_file.size / 1024  # 转换为KB
    file_type = uploaded_file.type

    st.subheader(f"文件名{file_name}")
    st.write(f"文件大小: {file_size:.2f} KB")
    st.write(f"文件类型: {file_type}")

    text = uploaded_file.getvalue().decode("utf-8")
    st.write(f"文件内容预览:{text[:200]}...")

    with st.spinner("正在处理文件..."):
        time.sleep(1)  # 模拟处理时间
        result = st.session_state["service"].upload_by_str(text, file_name)
        st.write(result)