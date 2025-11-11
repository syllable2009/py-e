from mydemo.meili.service import SearchService
# from mydemo.meili.models import Product
import meilisearch
import json

# def demo_sync():
#     # 1. 确保索引存在
#     SearchService.ensure_index_exists()
#
#     # 2. 添加文档
#     products = [
#         Product(1, "Laptop", "Powerful laptop", 1200.0, ["electronics"], True),
#         Product(2, "Book", "Python Guide", 30.0, ["books"], True),
#     ]
#     result = SearchService.add_documents(products)
#     print("Add result:", result)
#
#     # 3. 搜索
#     resp = SearchService.search(
#         "laptop",
#         filter="in_stock=true",
#         sort=["price:desc"],
#         facets=["categories"]
#     )
#     print("Hits:", len(resp["hits"]))
#     print("Facets:", resp.get("facetDistribution"))
#
#     # 4. 删除
#     SearchService.delete_document(2)

def to_dict(obj):
    return getattr(obj, "__dict__", {})

if __name__ == "__main__":

    # client = meilisearch.Client('http://localhost:7700', 'R5T5WDon_QrPqhFK97NgGlTVa81iuVlN44TMLiClTTg')
    # indexes = client.get_indexes({'limit': 30})
    # print(indexes)
    by_id = SearchService.get_doc_by_id('bbb', '1')
    print(to_dict(by_id))
