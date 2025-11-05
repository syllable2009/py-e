import os
import uuid

import pandas as pd
from typing import List, Any, Optional, Tuple

from mydemo.exception.business_exception import BusinessException
from mydemo.exception.business_exception_constant import ExceptionCode


class ExcelPandas:
    def __init__(self, file_name: str):
        self.file_name = file_name
        if os.path.exists(file_name):
            self._df_dict = pd.read_excel(file_name, sheet_name=None, dtype=str)  # 保持原始类型，避免数字变 float
        else:
            # 创建空文件：写入一个空的 Sheet1
            pd.DataFrame().to_excel(file_name, sheet_name='Sheet1', index=False)
            self._df_dict = {'Sheet1': pd.DataFrame()}
            print(f"🆕 创建新 Excel 文件 '{file_name}'，并添加 Sheet: 'Sheet1'")

    def add_sheet(self, sheet_name: str):
        if sheet_name in self._df_dict:
            print(f"⚠️ Sheet '{sheet_name}' 已存在，跳过创建。")
            return
        self._df_dict[sheet_name] = pd.DataFrame()
        self._save()
        print(f"➕ 新增 Sheet: '{sheet_name}'")

    def get_sheet_df(self, sheet_name: str) -> pd.DataFrame:
        if sheet_name not in self._df_dict:
            raise BusinessException(ExceptionCode.NOT_FOUND.name, ExceptionCode.NOT_FOUND.code)
        return self._df_dict[sheet_name]

    def set_header(self, sheet_name: str, header: List[str]):
        df = self.get_sheet_df(sheet_name)
        if df.empty or df.columns.empty or pd.isna(df.columns[0]):
            # 表为空或无有效表头 → 设置新表头
            self._df_dict[sheet_name] = pd.DataFrame(columns=header)
            self._save()
        else:
            print(f"⚠️ Sheet '{sheet_name}' 已有数据，跳过设置表头。")

    def set_row(self, sheet_name: str, row_index: Optional[int], data: List[Any]):
        df = self.get_sheet_df(sheet_name)
        # 数据长度
        n_data = len(data)
        # 列的长度
        n_cols = len(df.columns)

        # Step 1: 确定最终列结构
        if df.empty and n_cols == 0:
            # 表完全空白：直接用 data 创建列
            final_columns = [f"Column{i + 1}" for i in range(n_data)]
            aligned_data = data
        else:
            if n_data > n_cols:
                # 字段多了 → 扩展列
                extra_cols = [f"Column{i + 1}" for i in range(n_cols, n_data)]
                final_columns = df.columns.tolist() + extra_cols
                aligned_data = data  # 长度匹配 final_columns
            else:
                # 字段少了或相等 → 补 NA 到原列长度
                final_columns = df.columns.tolist()
                aligned_data = [
                    data[i] if i < n_data else pd.NA
                    for i in range(len(final_columns))
                ]

        # Step 2: 处理追加 or 指定行
        if row_index is None:
            # 追加模式：用 concat，pandas 自动对齐列（已有行在新列上为 NaN）
            new_row = pd.DataFrame([aligned_data], columns=final_columns)
            updated_df = pd.concat([df, new_row], ignore_index=True)
            self._df_dict[sheet_name] = updated_df

        else:
            # 指定行写入（Excel 行号）
            target_idx = row_index - 1
            if target_idx < 0:
                raise ValueError("row_index 必须 >= 1")

            # 扩展 DataFrame 的列（关键！）
            df = df.reindex(columns=final_columns, fill_value=pd.NA)

            # 扩展行数（如果需要）
            current_len = len(df)
            if target_idx >= current_len:
                raise ValueError("row_index不存在")

            # 写入当前行
            df.iloc[target_idx] = aligned_data
            self._df_dict[sheet_name] = df

        self._save()
        action = "追加" if row_index is None else f"设置第 {row_index} 行"
        print(f"✅ Sheet '{sheet_name}' {action} 成功。")

    def search_in_column(self, sheet_name: str, column_name: str, keyword: str) -> List[Tuple[int, Tuple[Any, ...]]]:
        df = self.get_sheet_df(sheet_name)

        # 列名匹配（不区分大小写）
        col_matches = [col for col in df.columns if str(col).lower() == str(column_name).lower()]
        if not col_matches:
            print(f"❌ 列 '{column_name}' 不存在！可用列：{list(df.columns)}")
            return []
        target_col = col_matches[0]

        # 搜索（忽略大小写，处理 NaN）
        mask = df[target_col].astype(str).str.contains(keyword, case=False, na=False)
        matched_rows = df[mask]

        # 返回 (Excel行号, 行数据元组) —— 注意：Excel 行号 = pandas index + 2（因为有表头）
        results = []
        for idx in matched_rows.index:
            excel_row_num = idx + 2  # pandas index 从 0 开始，对应 Excel 第2行起
            row_tuple = tuple(matched_rows.loc[idx].fillna("").tolist())
            results.append((excel_row_num, row_tuple))
        return results

    def _save(self):
        with pd.ExcelWriter(self.file_name, engine='openpyxl') as writer:
            for sheet_name, df in self._df_dict.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)


if __name__ == "__main__":
    file_path = "/Users/jiaxiaopeng/ppt/测试1.xlsx"
    ep = ExcelPandas(file_path)
    data = ['name', 'age']
    # ep.add_sheet('我的文档')
    # ep.set_header('Sheet1', ['name', 'age'])
    # ep.set_row('Sheet1', None, [uuid.uuid4().hex])
    ep.set_row('Sheet1', None, ['李四', 280, '联系'])

    # result = ep.search_in_column('我的文档', 'name', '三')
    # print(result)  # 输出: [(2, ('张三', '34'))]
