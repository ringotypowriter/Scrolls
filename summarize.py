import ollama

import prompt_engineering

MODEL_NAME="llama3.1:8b"



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

# 提取关键信息
def refine_structure(text):
    requirement_prompt = f"""
    我需要你帮助我分析以下课程内容，并生成一个详细的总结。请按照以下要求完成任务：
    1. 你需要在你的正式内容之前用正文，严格按照这个格式：「课程内容是关于**[课程名称]**的，内容包括了**[主要内容或主题]**。」作为你的acknowledgement。在这之后的下一行使用标题写明与[课程内容]有关的正式标题
    2. 你的总结应该严格使用语法正确的中文。
    3. 请使用Markdown格式来组织内容：
       - 不同的主题和小节应使用合理的标题（Heading）。
       - 超过三点的内容请使用列表。
       - 如果内容中有对比，请使用表格（Table）形式呈现。
    4. 在总结的结尾，提供简洁的**关键点参考**，帮助我快速回顾主要内容。
    5. 使用医学领域的专业术语，并确保提供相应的解释或英文术语。
    6. 如果课程内容中包含数学公式，请使用LaTeX格式表示。
    7. 你不能忽略原文中的任何一块内容。
    请从以下课程内容中进行分析：\n
    {text}
    """
    conversation_history.append({"role": "user", "content": requirement_prompt})
    response = ollama.chat(
        model=MODEL_NAME,
        options={"temperature": 0.5},
        messages=conversation_history,
    )
    conversation_history.append(response['message'])
    return response['message']

