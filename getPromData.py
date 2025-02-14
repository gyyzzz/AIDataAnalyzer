from prometheus_api_client import PrometheusConnect
from datetime import datetime
from datetime import timedelta
import pandas as pd
import yaml

def create_prometheus_connection(url="http://localhost:9090/", disable_ssl=True):
    """创建 Prometheus 连接"""
    return PrometheusConnect(url=url, disable_ssl=disable_ssl)


def parse_time_range(time_range):
    """解析时间范围字符串（如 '10m', '1h', '1d'）为 datetime 计算"""
    time_unit = time_range[-1]  # 获取单位（m/h/d）
    delta = int(time_range[:-1])  # 获取数值部分

    now = datetime.now()
    if time_unit == "m":
        return now - timedelta(minutes=delta)
    elif time_unit == "h":
        return now - timedelta(hours=delta)
    elif time_unit == "d":
        return now - timedelta(days=delta)
    else:
        raise ValueError("Unsupported time range format. Use 'Xm', 'Xh', or 'Xd'.")


def parse_step(step):
    """解析 step（如 '1m', '5m', '1h'）为 timedelta"""
    step_unit = step[-1]
    step_value = int(step[:-1])

    if step_unit == "s":
        return timedelta(seconds=step_value)
    elif step_unit == "m":
        return timedelta(minutes=step_value)
    elif step_unit == "h":
        return timedelta(hours=step_value)
    elif step_unit == "d":
        return timedelta(days=step_value)
    else:
        raise ValueError("Unsupported step format. Use 'Xm', 'Xh', or 'Xd'.")


def get_prometheus_data(prom, query, start_time=None, end_time=None, time_range="10m", step="1m"):
    """
    从 Prometheus 获取指标数据并转换为 DataFrame 格式。

    :param prom: PrometheusConnect 实例
    :param query: PromQL 查询语句
    :param start_time: 开始时间（datetime 对象，可选）
    :param end_time: 结束时间（datetime 对象，可选）
    :param time_range: 时间范围（如 "10m", "1h", "1d"）
    :param step: 采样步长（如 "1m", "5m", "1h"）
    :return: DataFrame 格式的查询结果
    """

    # 解析时间范围
    if not start_time or not end_time:
        start_time = parse_time_range(time_range)
        end_time = datetime.now()
    else:
        start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        end_time = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
    

    # 解析 step 为 timedelta
    step_duration = parse_step(step)

    # 获取 Prometheus 数据
    try:
        result = prom.get_metric_range_data(
            metric_name=query,
            start_time=start_time,
            end_time=end_time,
            chunk_size=step_duration
        )
    except Exception as e:
        print(f"获取数据失败: {e}")
        return None

    # 解析数据到 DataFrame
    if not result or len(result) == 0:
        print("没有获取到数据")
        return None

    data_list = []
    for metric in result:
        instance = metric["metric"].get("instance", "unknown")
        job = metric["metric"].get("job", "unknown")

        for value in metric["values"]:
            timestamp = datetime.fromtimestamp(float(value[0]))
            value = float(value[1])

            data_list.append([timestamp, instance, job, value])

    df = pd.DataFrame(data_list, columns=["timestamp", "instance", "job", "value"])
    df.set_index("timestamp", inplace=True)
    print(f"列名: {df.columns}")
    return df


