# LangChain RAG Demo

一个基于 Streamlit + LangChain + Chroma 的本地 RAG 示例项目。

当前版本支持：
- 上传 `txt` / `md` 文件写入知识库
- 基于知识库进行多轮对话
- 将会话历史持久化到本地 JSON 文件
- 通过 Chroma 持久化向量数据

项目默认通过 OpenAI 兼容接口访问模型，当前配置示例使用 DashScope 兼容端点。

## 功能概览

- `streamlit_app.py`
  - Streamlit 聊天界面入口
  - 支持创建/切换会话、清空会话、上传知识库文件
- `knowledge_base.py`
  - 文本切分
  - 文档去重（基于 MD5）
  - 写入 Chroma 向量库
- `rag.py`
  - 检索增强问答主流程
  - 管理会话历史
- `file_history_store.py`
  - 将聊天记录存入本地 `chat_history/*.json`
- `config_data.py`
  - 集中管理模型、切分、向量库和路径配置

## 环境要求

- Python 3.10+
- 可用的 OpenAI 兼容模型服务

## 安装依赖

建议先创建虚拟环境：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 环境变量

在项目根目录创建 `.env` 文件：

```env
DASHSCOPE_API_KEY=your_api_key
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

说明：
- `DASHSCOPE_API_KEY`：模型服务的 API Key
- `DASHSCOPE_BASE_URL`：OpenAI 兼容接口地址

如果你使用其他兼容 OpenAI API 的模型服务，也可以替换成对应地址。

## 启动方式

```bash
streamlit run streamlit_app.py
```

启动后可以在页面中：
- 在左侧上传 `txt` 或 `md` 文件写入知识库
- 创建或切换聊天会话
- 在主区域直接提问

## 目录结构

```text
.
├── streamlit_app.py      # Streamlit 页面入口
├── rag.py                # RAG 对话链路
├── knowledge_base.py     # 文档入库逻辑
├── vector_store.py       # Chroma 检索封装
├── file_history_store.py # 本地历史记录存储
├── config_data.py        # 项目配置
├── requirements.txt      # Python 依赖
├── chroma_db/            # Chroma 持久化目录
├── chat_history/         # 本地聊天记录
└── md5.text              # 文档去重记录
```

## 关键配置

可以在 `config_data.py` 中调整以下参数：

- `embedding_model`：Embedding 模型名称
- `chat_model`：对话模型名称
- `chunk_size`：文本切片大小
- `chunk_overlap`：切片重叠长度
- `similarity_top_k`：检索返回的文档数量
- `persist_directory`：Chroma 数据目录
- `history_store_dir`：历史会话目录

## 当前限制

- 当前上传能力只支持 `txt` 和 `md`
- 尚未实现引用来源展示
- 尚未实现 PDF、DOCX 等格式导入
- 当前聊天页面与业务逻辑仍在同一个 Streamlit 入口文件中

## 后续可扩展方向

- 增加 PDF / DOCX / HTML 文档导入
- 在回答中展示召回片段和来源信息
- 支持删除知识库文档
- 增加多页面管理界面
- 补充单元测试和集成测试
