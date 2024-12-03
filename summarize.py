import pysrt
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_ollama import ChatOllama
from langchain_ollama import OllamaEmbeddings

import prompt_engineering

MODEL_NAME="llama3.2-vision:11b"

def load_srt_as_documents(file_path):
    subtitles = pysrt.open(file_path)
    documents = []
    for subtitle in subtitles:
        content = subtitle.text.replace("\n", " ")
        metadata = {
            "start_timestamp": str(subtitle.start),
            "end_timestamp": str(subtitle.end),
        }
        documents.append(Document(page_content=content, metadata=metadata))
    return documents

# Initial Prompt
conversation_history = [
    prompt_engineering.SYSTEM_PROMPT
]

# 读取文件中的长文本
def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text

def write_file(file_path, content):
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def summary_with_langchain(srt_file):
    llm = ChatOllama(model=MODEL_NAME)

    # 定义系统提示
    prompt_template = "\n".join([prompt_engineering.SYSTEM_PROMPT['content'],
                    "Use the following pieces of SRT context to answer the question at the end. Be careful at the context related to timestamps(时间戳)"
                    "You can't make up a time if you don't know the answer"
                     "{context}",
                    ""
                    "Question: {question}",
                    "Helpful Answer:"])

    # 创建 Prompt 模板
    prompt = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
        )

    embeddings = OllamaEmbeddings(model=MODEL_NAME)

    raw_text = read_file(srt_file)

    # 创建向量数据库
    srt_documents = load_srt_as_documents(srt_file)
    vectorstore = FAISS.from_documents(srt_documents, embeddings)

    # 创建检索器
    retriever = vectorstore.as_retriever()

    # 创建问答链
    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever,
                                           chain_type_kwargs={
                                               "prompt": prompt,
                                           }
                                           )


    # 示例：查询 SRT 内容
#     query = f"""
# 请根据提供的你所能查阅的SRT内容，对其中讲述内容进行总结，并严格按照以下格式组织信息：
# 1. 确认信息
# 在正式内容之前，你需要用正文严格按照以下格式输出你的 确认信息：
# 「课程内容是关于[课程名称]的，内容包括了[主要内容或主题]。」
# 在这一段之后的下一行，使用标题写明与[课程内容]有关的正式标题。
#
# 2. 总结格式要求
# - 语法要求：总结必须严格使用语法正确的中文。
# - Markdown格式：
#     - 使用合理的标题（Heading）来区分不同主题和小节。
#     - 超过三点的内容请使用列表形式呈现。
#     - 如果内容涉及对比，请使用表格（Table）形式呈现。
# - 医学领域专业术语：使用医学领域的专业术语，并确保提供相应的解释或英文术语。
# - 数学公式：如果课程内容中涉及数学公式，请使用LaTeX格式进行表示。
# - 关键点参考：总结结束时提供简洁的关键点参考，帮助快速回顾主要内容。
# - 严谨性要求：不要忽略原文中的任何内容，确保每一块内容都得到涵盖。
#
# 3. 结构化内容
# 请根据时间轴内容，组织以下形式的总结：
# [课程名称]
# 1. [第一部分标题]（时间范围）
# - [小点标题]（开始时间）
#     - 简要正文（必要时可分点）
#
# 2. [第二部分标题]（时间范围）
# - [小点标题]（开始时间）
#     - 简要正文（必要时可分点）
#
# （依此类推，以时间顺序涵盖所有部分，不能省略）
#
# 4. 内容时间点
# 你的所提供的内容时间点必须符合时间轴，请反复检查。
#
#     """

    query2 = f"""
    基于你的context，告诉我灵敏度这一词在几分几秒（时间戳）被提及，基于你所了解的srt字幕文件
    """
    answer = qa_chain.invoke({"query": query2})
    return answer['result']
#
# # 提取关键信息
# def refine_structure(text):
#     requirement_prompt = f"""
# 我需要你帮助我分析以下课程内容，并生成一个详细的总结。请按照以下要求完成任务：
# 请根据以下提供的时间轴内容，对讲述内容进行总结，并严格按照以下格式组织信息：
# 1. 确认信息
# 在正式内容之前，您需要用正文严格按照以下格式输出你的 确认信息：
# 「课程内容是关于[课程名称]的，内容包括了[主要内容或主题]。」
# 在这一段之后的下一行，使用标题写明与[课程内容]有关的正式标题。
#
# 2. 总结格式要求
# - 语法要求：总结必须严格使用语法正确的中文。
# - Markdown格式：
#     - 使用合理的标题（Heading）来区分不同主题和小节。
#     - 超过三点的内容请使用列表形式呈现。
#     - 如果内容涉及对比，请使用表格（Table）形式呈现。
# - 医学领域专业术语：使用医学领域的专业术语，并确保提供相应的解释或英文术语。
# - 数学公式：如果课程内容中涉及数学公式，请使用LaTeX格式进行表示。
# - 关键点参考：总结结束时提供简洁的关键点参考，帮助快速回顾主要内容。
# - 严谨性要求：不要忽略原文中的任何内容，确保每一块内容都得到涵盖。
#
# 3. 结构化内容
# 请根据时间轴内容，组织以下形式的总结：
# [课程名称]
# 1. [第一部分标题]（时间范围）
# - [小点标题]（开始时间）
#     - 定义/描述: 简要概述核心概念或内容。
#     - 示例: 提供具体案例或应用场景。
#     - 目标/意义: 描述该部分内容的重要性或作用。
#
# 2. [第二部分标题]（时间范围）
# - [小点标题]（开始时间）
#     - 定义/描述: 简要概述核心概念或内容。
#     - 示例: 提供具体案例或应用场景。
#     - 目标/意义: 描述该部分内容的重要性或作用。
#
# （依此类推，涵盖所有部分）
#
# 4. 结尾部分：关键点参考 在总结的最后，请提供简洁的关键点参考，帮助快速回顾课程的主要内容。
# 请从以下时间轴内容中进行分析：\n
#     {text}
#     """
#     conversation_history.append({"role": "user", "content": requirement_prompt})
#     response = ollama.chat(
#         model=MODEL_NAME,
#         options={"temperature": 0.2},
#         messages=conversation_history,
#     )
#     conversation_history.append(response['message'])
#     return response['message']


if __name__ == "__main__":
    # 示例调用
    text = summary_with_langchain("temp/output.srt")

    print(text)