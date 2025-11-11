# import asyncio
from typing import Any, Dict, List, Optional, Union
from meilisearch.models.document import Document, DocumentsResults
import meilisearch.index
from meilisearch.index import Index
from mydemo.meili.client import MeiliSearchClient, safe_meili_call
from meilisearch.models.task import TaskInfo


class SearchService:
    # ------------------ 索引管理 ------------------
    @staticmethod
    def get_index_exists(index_name: str) -> bool:
        """检查索引是否存在（正确方式：捕获异常）"""
        try:
            MeiliSearchClient.get_sync_client().get_index(index_name)
            return True
        except meilisearch.errors.MeilisearchApiError as e:
            if e.code == "index_not_found":
                return False
            raise  # 其他错误（如权限、网络）继续抛出

    @staticmethod
    def get_index_info(index_name: str) -> Optional[Index]:
        return MeiliSearchClient.get_sync_client().get_index(index_name)

    @staticmethod
    def create_index(index_name: str, id: str) -> Optional[TaskInfo]:
        return MeiliSearchClient.get_sync_client().create_index(index_name, {'primaryKey': id})

    @staticmethod
    def delete_index(index_name: str) -> Optional[TaskInfo]:
        return MeiliSearchClient.get_sync_client().delete_index(index_name)

    # @staticmethod
    # def ensure_index_exists(index_name:str) -> Index:
    #     """确保索引存在，并设置搜索规则"""
    #     client = MeiliSearchClient.get_sync_client()
    #     try:
    #         index = client.get_index(index_name)
    #     except Exception:
    #         index = client.create_index(index_name, {"primaryKey": "uid"})
    #
    #     # 设置可搜索字段、过滤字段、排序字段（只需设置一次）
    #     index.update_searchable_attributes(["name", "description"])
    #     index.update_filterable_attributes(["categories", "in_stock", "price"])
    #     index.update_sortable_attributes(["price", "name"])
    #     index.update_ranking_rules([
    #         "words",
    #         "typo",
    #         "proximity",
    #         "attribute",
    #         "sort",
    #         "exactness"
    #     ])
    #     return index

    # ------------------ 文档操作 ------------------
    @staticmethod
    def get_doc_by_id(index_name: str, doc_id: str) -> Optional[Document]:
        return MeiliSearchClient.get_sync_client().index(index_name).get_document(doc_id)

    @staticmethod
    def del_document(index_name: str, doc_id: str) -> TaskInfo:
        """添加单个文档（同步）"""
        index = MeiliSearchClient.get_sync_client().index(index_name)
        return safe_meili_call(index.delete_document, index_name, doc_id)

    # 添加文档列表，或更新已存在的文档，文档的其余部分将保持不变。
    @staticmethod
    def add_documents(index_name: str, docs: list[dict[str, Any]]) -> TaskInfo:
        """批量添加文档（同步）"""
        index = MeiliSearchClient.get_sync_client().index(index_name)
        return safe_meili_call(index.add_documents, docs)

    # 修改老字段或添加新字段，文档的其余部分将保持不变。
    @staticmethod
    def update_documents(index_name: str, docs: list[dict[str, Any]]) -> TaskInfo:
        index = MeiliSearchClient.get_sync_client().index(index_name)
        return safe_meili_call(index.update_documents, docs)

    # ------------------ 搜索 ------------------

    @staticmethod
    def search(
            index_name: str,
            query: str,
            *,
            offset: int = 0,
            limit: int = 20,
            filter: Optional[str] = None,
            sort: Optional[List[str]] = None,
            facets: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        高级搜索
        返回结构: {
            "hits": [...],
            "offset": 0,
            "limit": 20,
            "nbHits": 100,
            "facetsDistribution": {...},
            ...
        }
        """
        index = MeiliSearchClient.get_sync_client().index(index_name)
        params = {
            "offset": offset,
            "limit": limit,
            "filter": filter,
            "sort": sort,
            "facets": facets,
            "highlightPreTag": "<em>",
            "highlightPostTag": "</em>",
        }
        # 移除 None 值，避免传入无效参数
        params = {k: v for k, v in params.items() if v is not None}
        return safe_meili_call(index.search, query, params)
