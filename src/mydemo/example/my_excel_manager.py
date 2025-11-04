import pandas as pd
import os
from typing import Dict, List, Optional, Any


class ExcelManager:
    def __init__(self, filename: str, columns: Optional[List[str]] = None):
        """
        初始化 Excel 管理器

        :param filename: Excel 文件路径（.xlsx）
        :param columns: 列名列表（仅在新建文件时使用）
        """
        self.filename = filename
        self.columns = columns or []

        if os.path.exists(filename):
            # 文件存在：加载数据
            self.df = pd.read_excel(filename)
            # 确保列顺序一致（可选）
            if self.columns and list(self.df.columns) != self.columns:
                print("⚠️ 警告：现有列与指定列不一致")
        else:
            # 文件不存在：创建空 DataFrame
            if not self.columns:
                raise ValueError("新建文件时必须指定 columns")
            self.df = pd.DataFrame(columns=self.columns)
            self._save()  # 立即创建空文件

    # 添加一条记录
    def add_record(self, record: Dict):
        """追加单条记录"""
        # 可选：验证字段
        if self.columns:
            missing = set(self.columns) - set(record.keys())
            extra = set(record.keys()) - set(self.columns)
            if missing:
                raise ValueError(f"缺失字段: {missing}")
            if extra:
                print(f"⚠️ 警告：多余字段将被忽略: {extra}")
                record = {k: v for k, v in record.items() if k in self.columns}

        # 转为 DataFrame 并追加
        new_df = pd.DataFrame([record])
        self.df = pd.concat([self.df, new_df], ignore_index=True)
        self._save()

    # ===== 新增方法：增加列 =====
    def add_column(self, column_name: str, default_value: Any = None):
        """新增一列"""
        if column_name in self.df.columns:
            print(f"⚠️ 列 '{column_name}' 已存在，跳过创建")
            return
        self.df[column_name] = default_value
        self._save()

    # ===== 新增方法：按索引赋值单列 =====
    def set_cell(self, index: int, column: str, value: Any):
        """按行索引和列名设置单元格值"""
        if column not in self.df.columns:
            raise ValueError(f"列 '{column}' 不存在")
        if not (0 <= index < len(self.df)):
            raise IndexError(f"行索引 {index} 超出范围 [0, {len(self.df) - 1}]")
        self.df.loc[index, column] = value
        self._save()

    def search(self, column: str, keyword, case_sensitive=False) -> pd.DataFrame:
        """在指定列中搜索包含关键词的行"""
        if column not in self.df.columns:
            raise ValueError(f"列 '{column}' 不存在")

        # 处理 NaN 值，避免 str.contains 报错
        mask = self.df[column].astype(str).str.contains(
            str(keyword),
            case=case_sensitive,
            na=False  # NaN 视为 False
        )
        return self.df[mask].copy()

    def get_all(self) -> pd.DataFrame:
        """返回所有数据（副本）"""
        return self.df.copy()

    def _save(self):
        """内部保存方法"""
        self.df.to_excel(self.filename, index=False)

    def __len__(self):
        return len(self.df)

    def __repr__(self):
        return f"<ExcelManager: {self.filename} ({len(self)} records)>"

    def print(self):
        for row in self.df.itertuples():
            print(f"索引: {row.Index}, Name: {row.Name}")

    def iterate_column(self, column: str):
        """生成器：遍历指定列的 (index, value)"""
        if column not in self.df.columns:
            raise ValueError(f"列 '{column}' 不存在")
        return zip(self.df.index, self.df[column])

if __name__ == "__main__":
    # 定义列,只有创建时才有用
    cols = ["Name", "Author", "Category"]

    # 初始化管理器（自动创建或加载）
    em = ExcelManager("/Users/jiaxiaopeng/ppt/employees.xlsx", columns=cols)

    # # 追加记录
    # em.add_record({"ID": 1, "Name": "Alice", "Department": "HR", "Salary": 5000})
    # em.add_record({"ID": 2, "Name": "Bob", "Department": "IT", "Salary": 7000})
    # em.add_record({"ID": 3, "Name": "Charlie", "Department": "Finance", "Salary": 6000})
    #
    # # 再次运行时，会自动加载已有数据并追加
    # em.add_record({"ID": 5, "Name": "Diana", "Department": "IT", "Salary": 7500})
    #
    # print(em)  # <ExcelManager: employees.xlsx (4 records)>
    #
    # # 搜索
    # it_employees = em.search("Department", "IT")
    # print("\n🔍 IT 部门员工:")
    # print(it_employees)
    #
    # name_contains_a = em.search("Name", "a", case_sensitive=False)
    # print("\n🔍 名字包含 'a' 的员工:")
    # print(name_contains_a)
    #
    # # 获取全部数据
    # all_data = em.get_all()
    # print("\n📊 全部数据1:")
    # print(all_data)
    #
    # em.add_column("Like")
    # em.add_column("Age", default_value=0)
    # # 索引从0开始
    # em.set_cell(0, "Like", '唱歌')
    # all_data = em.get_all()
    # print("\n📊 全部数据2:")
    # print(all_data)
    # em.print()

    column = em.iterate_column('Name')
    em.set_cell(0,'Name','syllable')
    for idx, name in column:
        print(f"行 {idx}: {name}")