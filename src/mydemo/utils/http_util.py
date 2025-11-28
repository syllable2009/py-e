import httpx
import json
from typing import Any, Dict, Union, Optional, List, Tuple

from playwright.async_api import Cookie
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


# 自定义异常（推荐）
class APIRequestError(Exception):
    def __init__(self, message: str, status_code: Optional[int] = None, url: str = ""):
        super().__init__(message)
        self.status_code = status_code
        self.url = url


# 全局复用的客户端（或作为类属性）
# 注意：在真实项目中，建议通过依赖注入传入 client
_http_client: Optional[httpx.AsyncClient] = None


def get_http_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(10.0),  # connect/read/write/ pool timeout
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 (compatible; MyApp/1.0)"},
        )
    return _http_client


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=5),  # 1s, 2s, 4s
    retry=retry_if_exception_type((httpx.NetworkError, httpx.TimeoutException)),
)
async def request(
        method: str,
        url: str,
        *,
        return_response: bool = False,
        **kwargs
) -> Union[str, Dict[str, Any]]:
    """
    发起 HTTP 请求并处理响应

    Args:
        method: HTTP 方法 ('GET', 'POST', ...)
        url: 请求 URL
        return_response: 是否返回原始文本（而非解析 JSON）
        **kwargs: 透传给 httpx.request 的参数（headers, params, json 等）

    Returns:
        str: 当 return_response=True
        dict: 正常 JSON 响应体

    Raises:
        APIRequestError: 业务或网络错误
    """
    client = get_http_client()

    try:
        response = await client.request(method, url, **kwargs)
    except httpx.RequestError as e:
        raise APIRequestError(f"网络请求失败: {e}", url=url) from e

    # 处理非 2xx 响应
    if response.status_code != 200:
        error_msg = f"HTTP {response.status_code} for {url}"
        # 尝试读取错误信息（避免 .text 阻塞）
        try:
            error_detail = response.text[:500]
        except Exception:
            error_detail = "<无法读取响应体>"
        print(f"❌ {error_msg} | Response: {error_detail}")

        if response.status_code in (403, 401):
            raise APIRequestError("权限不足或认证失败", status_code=response.status_code, url=url)
        elif response.status_code == 404:
            raise APIRequestError("资源未找到", status_code=404, url=url)
        elif response.status_code >= 500:
            # 5xx 可被 tenacity 重试（因 retry_if_exception_type 包含 NetworkError，但这里手动抛出也可）
            raise APIRequestError(f"服务器错误: {response.status_code}", status_code=response.status_code, url=url)
        else:
            raise APIRequestError(f"请求失败: {response.status_code}", status_code=response.status_code, url=url)

    # 返回原始响应文本
    if return_response:
        return response.text

    # 解析 JSON
    try:
        data: Dict[str, Any] = response.json()
    except json.JSONDecodeError as e:
        snippet = response.text[:200]
        raise APIRequestError(f"无效 JSON 响应: {snippet}...", url=url) from e

    # 处理业务错误（假设 API 返回 {"error": {...}}）
    if isinstance(data, dict) and data.get("error"):
        err_msg = data["error"].get("message") or str(data["error"])
        raise APIRequestError(f"API 业务错误: {err_msg}", url=url)

    return data

def convert_cookies(cookies: Optional[List[Cookie]]) -> Tuple[str, Dict]:
    if not cookies:
        return "", {}
    cookies_str = ";".join([f"{cookie.get('name')}={cookie.get('value')}" for cookie in cookies])
    cookie_dict = dict()
    for cookie in cookies:
        cookie_dict[cookie.get('name')] = cookie.get('value')
    return cookies_str, cookie_dict


if __name__ == "__main__":
    async def main():
        try:
            data = await request("GET", "https://httpbin.org/json")
            print(data)

            text = await request("GET", "https://example.com", return_response=True)
            print(text[:500])
        except APIRequestError as e:
            print(f"请求失败: {e}, 状态码: {e.status_code}, URL: {e.url}")


    # 运行
    import asyncio
    asyncio.run(main())