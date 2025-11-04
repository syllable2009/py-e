# 赋值
status = "成年人" if age >= 18 else "未成年人"
海象运算符 :=（Python 3.8+）
使用海象运算符（只调用一次）
if (n := len(data)) > 10:
    print(f"数据太长: {n} 项")

config = {"debug": True}
mode = config.get("mode", "production")  # 如果没有 "mode"，默认为 "production",没有和存在为None值

# 数据结构
列表（list）—— 有序、可变、允许重复
lst = [1, 2, 3]
lst = list("abc")  # ['a', 'b', 'c']
lst.append(4)
lst.insert(0, 'x')
字典（dict）—— 无序（Python 3.7+ 有序）、键值对、键唯一
d = {'name': 'Alice', 'age': 25}
d = dict(name='Alice', age=25)
d['name'] 或 d.get('name', 'default')
d['city'] = 'Beijing'
字符串（str）—— 有序、不可变、字符序列

元组（tuple）—— 有序、不可变、允许重复
tup = (1, 2, 3)
tup = 1, 2, 3       # 括号可省略
single = (1,) 

集合（set）—— 无序、不重复、可变
s = {1, 2, 3}
s = set([1, 2, 2, 3])  # {1, 2, 3}
empty_set = set()      # 注意：{} 是空字典

# yield：生成器（Generator）的关键字
用于定义生成器函数（返回迭代器），节省内存：不一次性生成所有数据，按需生成
函数执行到 yield 时暂停，返回值；下次调用时从暂停处继续
def count_up_to(n):
    i = 1
    while i <= n:
        yield i  # 每次返回一个值
        i += 1

gen = count_up_to(3)
print(next(gen))  # 1
print(next(gen))  # 2
print(next(gen))  # 3

# map()：函数式编程工具
语法：map(function, iterable)
将 function 应用于 iterable 的每个元素，返回map 对象（也是迭代器）
惰性求值：不立即计算，遍历时才执行

def square_numbers(numbers):
    # 直接将 map 对象的结果逐个 yield 出来
    yield from map(lambda x: x**2, numbers)
gen = square_numbers([1, 2, 3])
print(list(gen))  # [1, 4, 9]

# for ... in ... 是最核心、最常用的循环结构
for 变量 in 可迭代对象:
    # 循环体
    pass

fruits = ['apple', 'banana', 'cherry']
for fruit in fruits:
    pass
for index, fruit in enumerate(fruits): # 使用 enumerate() 获取索引 + 值
    print(f"{index}: {fruit}")

同时遍历 key 和 value（推荐！）
for key, value in person.items():
    print(f"{key}: {value}")

with open('file.txt', 'r') as f:
    for line in f:           # 每次读一行，内存友好
        print(line.strip())

def count_up_to(n):
    i = 1
    while i <= n:
        yield i
        i += 1
遍历生成器
for num in count_up_to(3):
    print(num)  # 1, 2, 3



