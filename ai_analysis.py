import ollama
import re
import getPromData

class OllamaClient:
    def __init__(self, model="deepseek-r1:7b"):
        """
        初始化 Ollama 客户端
        :param model: 指定 Ollama 的 AI 模型（默认 deepseek-r1:7b）
        """
        self.model = model

    def clean_response(self, text):
        """
        清理 AI 返回的无关标记，例如 <think> 标签
        :param text: AI 原始返回的字符串
        :return: 处理后的纯文本
        """
        return re.sub(r"<.*?>", "", text).strip()

    def generate_response(self, prompt, context=None):
        """
        生成 AI 回复
        :param prompt: 用户输入的提示词
        :param context: 之前的对话上下文（可选）
        :return: 处理后的 AI 回复
        """
        response = ollama.generate(
            model=self.model,
            prompt=prompt
        )
        return self.clean_response(response["response"])

    def chat(self, messages):
        """
        进行多轮对话
        :param messages: 一个包含多轮对话的列表 [{"role": "user", "content": "你好"}]
        :return: AI 生成的对话内容
        """
        response = ollama.chat(
            model=self.model,
            messages=messages
        )
        return self.clean_response(response["message"]["content"])

    def analyze_prometheus_data(self, query, time_range="10m", step="1m"):
        """
        获取并分析 Prometheus 监控数据，并结合 AI 进行分析
        :param query: Prometheus 查询语句
        :param time_range: 查询时间范围（如 "10m", "1h"）
        :param step: 数据间隔时间
        :return: AI 对监控数据的分析
        """
        # 获取 Prometheus 数据
        prom = getPromData.create_prometheus_connection()
        prom_data = getPromData.get_prometheus_data(prom, query, time_range=time_range, step=step)

        # 解析数据，提取关键信息
        if prom_data is None or prom_data.empty:
            print("获取的数据为空，无法分析。")
            return None  # 避免后续代码报错

        # 将数据转换为 AI 可理解的格式
        formatted_data = f"Prometheus 数据查询 ({query}):\n{prom_data}"

        # 让 AI 进行数据分析
        analysis_prompt = f"请对以下 Prometheus 监控数据进行分析，并给出关键趋势和判断是否存在异常情况：\n\n{formatted_data}"
        return self.generate_response(analysis_prompt)


if __name__ == "__main__":
    ollama_client = OllamaClient(model="deepseek-r1:7b")

    # 1. 生成普通文本回复
    #print(ollama_client.generate_response("你好，你是谁？"))

    ## 2. 进行多轮对话
    #messages = [
    #    {"role": "system", "content": "你是一个智能助手"},
    #    {"role": "user", "content": "请介绍一下你自己"}
    #]
    #print(ollama_client.chat(messages))

    # 3. 结合 Prometheus 监控数据进行 AI 分析
    
    query = 'node_memory_MemFree_bytes'
    print(ollama_client.analyze_prometheus_data(query, time_range="2m", step="15s"))
