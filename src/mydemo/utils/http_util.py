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
            headers={
                "accept": "application/json, text/plain, */*",
                "accept-language": "zh-CN,zh;q=0.9",
                "cache-control": "no-cache",
                "content-type": "application/json;charset=UTF-8",
                "origin": "https://www.xiaohongshu.com",
                "pragma": "no-cache",
                "priority": "u=1, i",
                "referer": "https://www.xiaohongshu.com/",
                "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site",
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
            },
        )
    return _http_client


async def close_http_client():
    global _http_client
    if _http_client is not None:
        await _http_client.aclose()
        _http_client = None


# @retry(
#     stop=stop_after_attempt(1),
#     wait=wait_exponential(multiplier=1, min=1, max=5),  # 1s, 2s, 4s
#     retry=retry_if_exception_type((httpx.NetworkError, httpx.TimeoutException)),
# )
async def http_get(
        url: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None, ) -> httpx.Response:
    client = get_http_client()
    try:
        response = await client.get(
            url,
            params=params,
            headers=headers if headers else client.headers,
            cookies=cookies,
            timeout=timeout if timeout is not None else client.timeout
        )
        response.raise_for_status()  # 自动抛出 4xx/5xx 异常
        return response
    except httpx.HTTPStatusError as e:
        # 可选：记录日志或自定义异常
        raise APIRequestError(f"网络请求状态异常: {e}", url=url) from e
    except httpx.RequestError as e:
        # 如连接超时、DNS 失败等
        raise APIRequestError(f"网络请求失败: {e}", url=url) from e


async def http_post(
        url: str,
        *,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None, ) -> httpx.Response:
    client = get_http_client()
    try:
        response = await client.post(
            url,
            data=data,
            json=json,
            params=params,
            headers=headers if headers else client.headers,
            cookies=cookies,
            timeout=timeout if timeout is not None else client.timeout
        )
        response.raise_for_status()
        return response
    except httpx.HTTPStatusError as e:
        raise APIRequestError(f"网络请求状态异常: {e}", url=url) from e
    except httpx.RequestError as e:
        raise APIRequestError(f"网络请求失败: {e}", url=url) from e


def convert_cookies(cookies: Optional[List[Dict[str, str]]]) -> Tuple[str, Dict[str, str]]:
    if not cookies:
        return "", {}

    cookie_dict: Dict[str, str] = {}
    valid_pairs: List[str] = []

    for cookie in cookies:
        name = cookie.get("name")
        value = cookie.get("value")

        # 跳过 name 或 value 为空/None 的项
        if not name or not value:
            continue

        # 确保 name 和 value 是字符串（防御性）
        name = str(name)
        value = str(value)

        cookie_dict[name] = value
        valid_pairs.append(f"{name}={value}")

    cookie_str = ";".join(valid_pairs)
    return cookie_str, cookie_dict


async def main():
    resp = await http_get("https://httpbin.org/json", params={"key": "value"})
    # 返回json信息，但会丢失响应元信息（如状态码、headers）。按需选择即可。
    print(f"{resp.json()}")
    # POST 表单数据
    resp = await http_post("https://httpbin.org/post", data={"user": "Bob"})
    print(resp.text)
    await close_http_client()


if __name__ == "__main__":
    # 运行
    import asyncio

    asyncio.run(main())
