import concurrent.futures
import time
import random

class TaskProcessor:
    def __init__(self, max_workers=4):
        # 初始化线程池
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)

    def do_task(self, task_id):
        """模拟一个耗时任务"""
        delay = random.uniform(0.5, 2.0)
        time.sleep(delay)
        result = f"Task {task_id} completed after {delay:.2f}s"
        print(result)
        return result

    def submit_tasks(self, task_ids):
        """提交多个任务到线程池并获取结果"""
        futures = [self.executor.submit(self.do_task, tid) for tid in task_ids]
        results = []
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as exc:
                print(f"Task generated an exception: {exc}")
        return results

    def shutdown(self):
        """关闭线程池"""
        self.executor.shutdown(wait=True)

# 使用示例
if __name__ == "__main__":
    processor = TaskProcessor(max_workers=3)
    task_list = list(range(1, 6))  # 任务ID: 1 到 5
    results = processor.submit_tasks(task_list)
    print("All tasks done.")
    processor.shutdown()