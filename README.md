Scrolls: 医学教育的 AI 助手
===
Scrolls 是一款专注于医学教育领域的智能助手，旨在帮助医学学生和其他相关学科领域的学生分析所学课程内容，特别是通过讲义转录提供深度学习支持。

---

## 🌟 Scrolls 的特点

> “您好！我是 Scrolls，一名专注于医学教育领域的 AIAssistant。我的主要功能是在帮助医学学生等相关学科领域学生分析所学课程内容，尤其是通过讲义转录提供的知识。”

### Scrolls 如何帮助您？

* 帮助您梳理复杂的概念。
* 提供准确且全面的信息，使学习更加轻松。


### 创造者的愿景

Scrolls 的开发者 RingoTypewriter 专注于开发帮助学生提高学习效率并深入理解知识的工具。这一愿景推动 Scrolls 成为医学知识探索的有力伙伴。

---

## 🚀 安装与运行

环境要求
* Python: 3.9.13 (为了能够正确运行Whisper）
* 依赖项: 项目需要的依赖列在 requirements.txt 中

安装步骤

> 注意:
> 需要手动将 **ollama-cli** 的可执行文件放置到 `platform` 文件夹中。
> * **Mac 平台**: 放入 `darwin` 文件夹。
> * **Windows 平台**: 放入 `windows` 文件夹。
> 
> 运行 streamlit 应用后，程序将自动启动 ollama-cli，并通过 subprocess 调用对应模型。

1.	克隆项目

2.	创建虚拟环境并激活：
```
python -m venv venv
source venv/bin/activate  # Linux/MacOS
venv\Scripts\activate     # Windows
```

3.	安装依赖：

```
pip install -r requirements.txt
```

4.	启动应用：
```
streamlit run app.py
```

5.	访问应用： 打开浏览器并访问 http://localhost:8501。

---

⚙️ 功能模块

* 音频处理：
  * 加载各种格式的音频文件。
  * 将音频内容分段并生成时间戳。
* 讲义转录：
  * 自动识别和分析音频内容。
  * 提供分段式内容摘要。
* Prompt Engineering：
  * 智能提示生成，提高内容理解效率。

---

🧠 使用的模型与技术

* UI: Streamlit
  * 协议: Apache-2.0 license 
  * 链接:https://github.com/streamlit/streamlit

* 音频转文本模型：OpenAI Whisper Medium
  *	参数量: 769M
  *	协议: MIT License
  * 链接: https://github.com/openai/whisper
	
* 文本处理模型：Meta LLaMA 3.2 
  * 参数量: 11B
  * 协议: LLAMA 3 COMMUNITY LICENSE AGREEMENT
  * 链接: https://github.com/meta-llama/llama

* Ollama
  * 协议: MIT License
  * 链接: https://github.com/ollama/ollama

这些模型的结合为 Scrolls 提供了从音频到文本生成和分析的完整解决方案，助力提升学习效率。

> 代码仓库不直接包含上述任何资源，需通过 pip 或由程序自动从源地址下载和安装相关依赖。

---

🧑‍💻 贡献指南

欢迎社区贡献！您可以通过以下方式参与：
1.	提交 Issue 或功能建议。
2. Fork 项目并提交 Pull Request。
3.	分享您的使用体验和改进意见。

---

📄 许可证

> Scrolls 使用 MIT 许可证，允许自由使用、修改和分发。

如果您对 Scrolls 有任何问题或需要帮助，请随时与我们联系！感谢您支持 Scrolls，祝您学习旅途愉快！