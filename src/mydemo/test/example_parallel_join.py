# 文件路径: dags/example_parallel_join.py

from datetime import datetime, timedelta
from airflow import DAG
import time
import random

from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import TaskGroup


# 模拟任务函数
def extract_data(**context):
    print("▶️ 开始提取数据...")
    time.sleep(2)
    print("✅ 数据提取完成")

def process_a(**context):
    print("▶️ 开始处理 A...")
    time.sleep(3)
    # 模拟偶尔失败（可选）
    # if random.random() < 0.3:
    #     raise Exception("Process A 临时故障！")
    print("✅ 处理 A 完成")

def process_b(**context):
    print("▶️ 开始处理 B...")
    time.sleep(4)
    print("✅ 处理 B 完成")

def join_tasks(**context):
    print("▶️ 所有上游已完成，开始汇聚逻辑...")
    time.sleep(1)
    print("✅ 汇聚完成")

def load_final(**context):
    print("▶️ 加载最终结果到数据库...")
    time.sleep(2)
    print("✅ 加载成功！")

# DAG 定义
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    'example_parallel_join',
    default_args=default_args,
    description='演示顺序 + 并行 + join + 超时',
    schedule_interval=None,  # 手动触发
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=['example', 'parallel', 'join'],
) as dag:

    start = PythonOperator(
        task_id='start',
        python_callable=lambda: print("🚀 流程开始"),
    )

    extract = PythonOperator(
        task_id='extract_data',
        python_callable=extract_data,
        execution_timeout=timedelta(minutes=10),  # ⏱️ 超时 10 分钟
    )

    # 并行分支：使用 TaskGroup 更清晰（可选）
    with TaskGroup("processing") as processing_group:
        task_a = PythonOperator(
            task_id='process_A',
            python_callable=process_a,
            execution_timeout=timedelta(minutes=10),
        )

        task_b = PythonOperator(
            task_id='process_B',
            python_callable=process_b,
            execution_timeout=timedelta(minutes=10),
        )

    # Join 任务：默认 trigger_rule="all_success"（即等待所有上游成功）
    join = PythonOperator(
        task_id='join',
        python_callable=join_tasks,
        execution_timeout=timedelta(minutes=10),
    )

    load = PythonOperator(
        task_id='load_final',
        python_callable=load_final,
        execution_timeout=timedelta(minutes=10),
    )

    end = PythonOperator(
        task_id='end',
        python_callable=lambda: print("🎉 流程结束"),
    )

    # 设置依赖关系
    start >> extract >> processing_group >> join >> load >> end