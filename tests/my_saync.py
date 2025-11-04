import asyncio

# 定义协程函数：async def
async def greet(name):
    print(f"Hello, {name}!")
    return f"Hi {name}"


# ✅ 正确方式 1：在另一个 async 函数中 await
async def main():
    # 执行协程：必须用 await 或事件循环
    result = await greet("Alice")
    print(type(result))

async def fetch_data(url):
    print(f"开始获取 {url}")
    await asyncio.sleep(2)  # 模拟耗时 I/O（非阻塞！）
    print(f"完成获取 {url}")
    return f"data from {url}"

async def main0():
    # 顺序执行（总耗时 ~4秒）
    data1 = await fetch_data("A")
    data2 = await fetch_data("B")
    print(data1, data2)

# 并发方式 1：create_task()
async def main1():
    task1 = asyncio.create_task(fetch_data("A"))
    task2 = asyncio.create_task(fetch_data("B"))

    # 等待两个任务完成
    data1 = await task1
    data2 = await task2
    print(data1, data2)

# 并发方式 2：asyncio.gather()（更简洁）
async def main2():
    data1, data2 = await asyncio.gather(
        fetch_data("A"),
        fetch_data("B")
    )
    print(data1, data2)


async def main3():
    tasks = [
        asyncio.create_task(fetch_data("A")),
        asyncio.create_task(fetch_data("B"))
    ]
    done, pending = await asyncio.wait(tasks)
    for task in done:
        print(task.result())

# asyncio.run()
asyncio.run(main3())