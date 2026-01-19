"""
쿠팡 MCP HTTP 서버 (Hugging Face Spaces용)
- Streamable HTTP transport로 원격 접속 지원
"""
import os
import json
import httpx
from mcp.server.fastmcp import FastMCP
from urllib.parse import urlencode
from starlette.responses import JSONResponse, FileResponse
from starlette.routing import Route

# 서버 URL
API_SERVER = os.getenv("COUPANG_API_SERVER", "https://coupang-mcp.netlify.app/.netlify/functions/coupang")

# Server Card for Smithery scanning
SERVER_CARD = {
    "version": "1.0",
    "serverInfo": {
        "name": "Coupang",
        "version": "1.0.0",
        "title": "쿠팡 상품 검색",
        "description": "쿠팡에서 상품 검색, 베스트 상품, 골드박스 특가를 조회합니다.",
        "iconUrl": "https://yuju777-coupang-mcp.hf.space/icon.svg"
    },
    "transport": {
        "type": "streamable-http",
        "endpoint": "/mcp"
    },
    "capabilities": {
        "tools": {}
    },
    "tools": [
        {
            "name": "search_coupang_products",
            "description": "쿠팡에서 상품을 검색합니다."
        },
        {
            "name": "get_coupang_best_products",
            "description": "쿠팡 카테고리별 베스트 상품을 조회합니다."
        },
        {
            "name": "get_coupang_goldbox",
            "description": "쿠팡 골드박스 (오늘의 특가/할인) 상품을 조회합니다."
        }
    ]
}

async def server_card_endpoint(request):
    """/.well-known/mcp/server-card.json 엔드포인트"""
    return JSONResponse(SERVER_CARD)

async def icon_endpoint(request):
    """/icon.svg 엔드포인트"""
    icon_path = os.path.join(os.path.dirname(__file__), "static", "icon.svg")
    return FileResponse(icon_path, media_type="image/svg+xml")

mcp = FastMCP("Coupang")


def extract_page_key(url: str) -> str:
    """상품 링크에서 pageKey 추출"""
    import re
    match = re.search(r'pageKey=(\d+)', url)
    return match.group(1) if match else ""


async def shorten_url(product_url: str) -> str:
    """상품 URL을 단축 링크로 변환"""
    page_key = extract_page_key(product_url)
    if not page_key:
        return product_url

    original_url = f"https://www.coupang.com/vp/products/{page_key}"

    try:
        data = await call_api("deeplink", {"url": original_url})
        if data.get("rCode") == "0" and data.get("data"):
            return data["data"][0].get("shortenUrl", product_url)
    except:
        pass

    return product_url


async def call_api(action: str, params: dict = None) -> dict:
    """API 서버 호출"""
    params = params or {}
    params["action"] = action
    url = f"{API_SERVER}?{urlencode(params)}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=30.0)
        return response.json()


def get_search_cta(keyword: str) -> str:
    return f"""
---
**다음 행동:**
| 가격 비교 | 인기 상품 | 특가 확인 |
|----------|----------|----------|
| "{keyword} 비교표 만들어줘" | "베스트 상품 보여줘" | "오늘 특가 뭐 있어?" |

💡 **팁**: "가격순 정렬해줘", "로켓배송만" 으로 필터링 가능
"""


def get_best_cta(category_name: str) -> str:
    return f"""
---
**다음 행동:**
| 특가 확인 | 상품 검색 | 다른 카테고리 |
|----------|----------|-------------|
| "골드박스 특가" | "1위 상품 더 검색해줘" | "식품 베스트" |

💡 **팁**: "비교표로 정리해줘" 하면 한눈에 비교 가능
"""


def get_goldbox_cta() -> str:
    return """
---
**다음 행동:**
| 상품 검색 | 베스트 확인 | 카테고리별 |
|----------|-----------|-----------|
| "관심 상품 검색" | "가전 베스트" | "뷰티 베스트" |

💡 **팁**: 할인율 높은 순으로 보려면 "할인율 순 정렬"
"""


@mcp.tool()
async def search_coupang_products(keyword: str, limit: int = 5) -> str:
    """
    쿠팡에서 상품을 검색합니다.

    Args:
        keyword (str): 검색할 키워드 (예: "에어팟", "맥북프로")
        limit (int): 가져올 결과 개수 (기본 5개, 최대 100개)

    Returns:
        상품 목록 (이름, 가격, 구매 링크 포함)
    """
    data = await call_api("search", {"keyword": keyword, "limit": limit})

    if "error" in data:
        return f"오류: {data.get('message', data['error'])}"

    if data.get("rCode") != "0":
        return f"API 오류: {data.get('rMessage', '알 수 없는 오류')}"

    products = data.get("data", {}).get("productData", [])

    if not products:
        return f"'{keyword}' 검색 결과가 없습니다."

    formatted_results = [f"## '{keyword}' 검색 결과\n"]

    for idx, product in enumerate(products[:limit], 1):
        name = product.get("productName", "")
        price = product.get("productPrice", 0)
        url = product.get("productUrl", "")
        image = product.get("productImage", "")
        is_rocket = product.get("isRocket", False)
        is_free_shipping = product.get("isFreeShipping", False)

        badges = []
        if is_rocket:
            badges.append("🚀 로켓배송")
        if is_free_shipping:
            badges.append("무료배송")
        badge_text = f" ({', '.join(badges)})" if badges else ""

        short_url = await shorten_url(url)
        image_md = f"[![{name}]({image})]({short_url})\n\n" if image else ""

        formatted_results.append(
            f"### {idx}. {name}\n\n"
            f"{image_md}"
            f"- **가격**: {int(price):,}원{badge_text}\n"
            f"- [구매하기]({short_url})\n"
        )

    formatted_results.append(get_search_cta(keyword))
    return "\n".join(formatted_results)


@mcp.tool()
async def get_coupang_best_products(category_id: int = 1016, limit: int = 5) -> str:
    """
    쿠팡 카테고리별 베스트 상품을 조회합니다.

    Args:
        category_id (int): 카테고리 ID (1016: 가전디지털, 1001: 여성패션, 1012: 식품 등)
        limit (int): 가져올 결과 개수 (기본 5개, 최대 100개)

    Returns:
        베스트 상품 목록
    """
    category_names = {
        1001: "여성패션", 1002: "남성패션", 1010: "뷰티",
        1011: "출산/유아동", 1012: "식품", 1013: "주방용품",
        1014: "생활용품", 1015: "홈인테리어", 1016: "가전디지털",
        1017: "스포츠/레저", 1018: "자동차용품", 1024: "헬스/건강식품",
        1029: "반려동물용품"
    }

    data = await call_api("best", {"category_id": category_id, "limit": limit})

    if "error" in data:
        return f"오류: {data.get('message', data['error'])}"

    if data.get("rCode") != "0":
        return f"API 오류: {data.get('rMessage', '알 수 없는 오류')}"

    products = data.get("data", [])

    if not products:
        return f"카테고리 {category_id} 베스트 상품이 없습니다."

    category_name = category_names.get(category_id, str(category_id))
    formatted_results = [f"## [{category_name}] 베스트 상품\n"]

    for idx, product in enumerate(products[:limit], 1):
        name = product.get("productName", "")
        price = product.get("productPrice", 0)
        url = product.get("productUrl", "")
        image = product.get("productImage", "")
        rank = product.get("rank", idx)
        is_rocket = product.get("isRocket", False)

        rocket_text = " (🚀 로켓배송)" if is_rocket else ""
        short_url = await shorten_url(url)
        image_md = f"[![{name}]({image})]({short_url})\n\n" if image else ""

        formatted_results.append(
            f"### {rank}위. {name}\n\n"
            f"{image_md}"
            f"- **가격**: {int(price):,}원{rocket_text}\n"
            f"- [구매하기]({short_url})\n"
        )

    formatted_results.append(get_best_cta(category_name))
    return "\n".join(formatted_results)


@mcp.tool()
async def get_coupang_goldbox(limit: int = 10) -> str:
    """
    쿠팡 골드박스 (오늘의 특가/할인) 상품을 조회합니다.

    Args:
        limit (int): 가져올 결과 개수 (기본 10개, 최대 100개)

    Returns:
        골드박스 특가 상품 목록
    """
    data = await call_api("goldbox", {"limit": limit})

    if "error" in data:
        return f"오류: {data.get('message', data['error'])}"

    if data.get("rCode") != "0":
        return f"API 오류: {data.get('rMessage', '알 수 없는 오류')}"

    products = data.get("data", [])

    if not products:
        return "골드박스 상품이 없습니다."

    formatted_results = ["## 골드박스 특가 상품\n"]

    for idx, product in enumerate(products[:limit], 1):
        name = product.get("productName", "")
        price = product.get("productPrice", 0)
        url = product.get("productUrl", "")
        image = product.get("productImage", "")
        is_rocket = product.get("isRocket", False)
        discount_rate = product.get("discountRate", 0)

        rocket_text = " (🚀 로켓배송)" if is_rocket else ""
        discount_text = f" ({discount_rate}% 할인)" if discount_rate else ""
        short_url = await shorten_url(url)
        image_md = f"[![{name}]({image})]({short_url})\n\n" if image else ""

        formatted_results.append(
            f"### {idx}. {name}\n\n"
            f"{image_md}"
            f"- **특가**: {int(price):,}원{discount_text}{rocket_text}\n"
            f"- [구매하기]({short_url})\n"
        )

    formatted_results.append(get_goldbox_cta())
    return "\n".join(formatted_results)


if __name__ == "__main__":
    import uvicorn

    # 포트 설정 (Hugging Face Spaces는 7860 사용)
    port = int(os.getenv("PORT", "7860"))

    # FastMCP 설정
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = port
    mcp.settings.transport_security.allowed_hosts.append("yuju777-coupang-mcp.hf.space")
    mcp.settings.transport_security.allowed_hosts.append("*.hf.space")

    # MCP 앱 가져오기
    mcp_app = mcp.streamable_http_app()

    # server-card 및 icon 라우트를 MCP 앱에 직접 추가
    mcp_app.routes.insert(0, Route("/.well-known/mcp/server-card.json", server_card_endpoint, methods=["GET"]))
    mcp_app.routes.insert(0, Route("/icon.svg", icon_endpoint, methods=["GET"]))

    uvicorn.run(mcp_app, host="0.0.0.0", port=port)
