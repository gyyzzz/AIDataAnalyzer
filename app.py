import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import yaml
import os
from getPromData import create_prometheus_connection, get_prometheus_data
from ai_analysis import OllamaClient

# 生成交互式折线图
def generate_interactive_plot(df, query):
    fig = px.line(df, x=df.index, y='value', title=f"Prometheus 数据: {query}")
    fig.update_layout(xaxis_title="时间", yaxis_title="值")
    return fig

# 主函数
def main():
    st.title('AI运维数据分析平台')
    
    # 用户输入
    query = st.text_input('请输入查询语句', 'node_memory_MemFree_bytes')
    start_time_str = st.text_input('请输入开始时间 (格式: YYYY-MM-DD HH:MM:SS)', '')
    end_time_str = st.text_input('请输入结束时间 (格式: YYYY-MM-DD HH:MM:SS)', '')
    time_range_input = st.text_input('请输入时间范围 (如: 2m, 1h)', '1m')
    step = st.text_input('请输入采样步长 (如: 15s, 1m)', '15s')
    
    # 读取配置文件
    current_path = os.path.abspath(__file__)
    with open(os.path.join(os.path.dirname(current_path), "config.yaml"), "r") as f:
        config = yaml.safe_load(f)
        prom_url = config.get('prometheus_url')
    
    # 创建 Prometheus 连接
    prom = create_prometheus_connection(prom_url)
    
    if st.button('查询'):
        try:
            
            # 获取 Prometheus 数据
            df = get_prometheus_data(prom, query, start_time=start_time_str, end_time=end_time_str, time_range=time_range_input, step=step)
            
            if df is not None and not df.empty:
                # 展示数据表
                st.write("### 原始数据", df)
                
                # 生成图表
                fig = generate_interactive_plot(df, query)
                st.plotly_chart(fig)
                
                # 创建 OllamaClient 实例
                ollama_client = OllamaClient(model="deepseek-r1:7b")
                
                # 进行 AI 分析
                with st.spinner('AI 正在分析数据...'):
                    analysis_result = ollama_client.analyze_prometheus_data(df, query)
                
                # 展示AI分析结果
                st.write("### AI 分析结果")
                st.write(analysis_result)
            else:
                st.write("未获取到数据，请检查查询语句和时间范围。")
        except Exception as e:
            st.write(f"发生错误: {e}")

# 运行 Streamlit 应用
if __name__ == "__main__":
    main()
