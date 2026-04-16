import streamlit as st

st.title("Amaneの文件上传")

uploaded_file = st.file_uploader(
    "选择一个文件上传",
    type=["txt"],
    accept_multiple_files=False #只接受一个文件上传
)

if uploaded_file is not None:
    file_name = uploaded_file.name
    file_size = uploaded_file.size / 1024  # 转换为KB
    file_type = uploaded_file.type

    st.subheader(f"文件名{file_name}")
    st.write(f"文件大小: {file_size:.2f} KB")
    st.write(f"文件类型: {file_type}")

    text = uploaded_file.getvalue().decode("utf-8")
    st.write(f"文件内容预览:{text}")