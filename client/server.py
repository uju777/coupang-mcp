"""
쿠팡 MCP 클라이언트
- 이 MCP는 HTTP API 서버를 통해 쿠팡 상품을 검색합니다.
- API 키가 필요 없습니다! (서버에서 처리)
"""
import os
import httpx
from mcp.server.fastmcp import FastMCP
from urllib.parse import urlencode

# 서버 URL (Netlify 배포 후 수정)
API_SERVER = os.getenv("COUPANG_API_SERVER", "https://coupang-mcp.netlify.app/.netlify/functions/coupang")

mcp = FastMCP("Coupang")


async def get_real_image_url(image_url: str) -> str:
    """쿠팡 파트너스 이미지 URL을 실제 CDN URL로 변환"""
    if not image_url:
        return ""
    try:
        async with httpx.AsyncClient(follow_redirects=False) as client:
            response = await client.head(image_url, timeout=5.0)
            if response.status_code == 302:
                return response.headers.get("location", image_url)
    except:
        pass
    return image_url


def extract_page_key(url: str) -> str:
    """파트너스 링크에서 pageKey 추출"""
    import re
    match = re.search(r'pageKey=(\d+)', url)
    return match.group(1) if match else ""


async def shorten_url(product_url: str) -> str:
    """상품 URL을 단축 링크로 변환 (수익 유지)"""
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


@mcp.tool()
async def search_coupang_products(keyword: str, limit: int = 5) -> str:
    """
    쿠팡에서 상품을 검색합니다. 쿠팡 가격, 쿠팡 최저가, 쿠팡 검색, 쿠팡 쇼핑 요청 시 이 도구를 사용하세요.

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

        # URL 단축 (수익 유지)
        short_url = await shorten_url(url)

        # 이미지 클릭 시 수익 링크로 연결
        image_md = f"[![{name}]({image})]({short_url})\n\n" if image else ""

        formatted_results.append(
            f"### {idx}. {name}\n\n"
            f"{image_md}"
            f"- **가격**: {int(price):,}원{badge_text}\n"
            f"- [구매하기]({short_url})\n"
        )

    return "\n".join(formatted_results)


@mcp.tool()
async def get_coupang_best_products(category_id: int = 1016, limit: int = 5) -> str:
    """
    쿠팡 카테고리별 베스트 상품을 조회합니다. 쿠팡 베스트, 쿠팡 인기, 쿠팡 랭킹, 많이 팔리는 상품 요청 시 사용하세요.

    Args:
        category_id (int): 카테고리 ID
            - 1001: 여성패션, 1002: 남성패션, 1010: 뷰티
            - 1011: 출산/유아동, 1012: 식품, 1013: 주방용품
            - 1014: 생활용품, 1015: 홈인테리어, 1016: 가전디지털
            - 1017: 스포츠/레저, 1018: 자동차용품, 1024: 헬스/건강식품
            - 1029: 반려동물용품
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

        # URL 단축 (수익 유지)
        short_url = await shorten_url(url)

        # 이미지 클릭 시 수익 링크로 연결
        image_md = f"[![{name}]({image})]({short_url})\n\n" if image else ""

        formatted_results.append(
            f"### {rank}위. {name}\n\n"
            f"{image_md}"
            f"- **가격**: {int(price):,}원{rocket_text}\n"
            f"- [구매하기]({short_url})\n"
        )

    return "\n".join(formatted_results)


@mcp.tool()
async def get_coupang_goldbox(limit: int = 10) -> str:
    """
    쿠팡 골드박스 (오늘의 특가/할인) 상품을 조회합니다. 쿠팡 특가, 쿠팡 할인, 쿠팡 세일, 오늘의 딜 요청 시 사용하세요.

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

        # URL 단축 (수익 유지)
        short_url = await shorten_url(url)

        # 이미지 클릭 시 수익 링크로 연결
        image_md = f"[![{name}]({image})]({short_url})\n\n" if image else ""

        formatted_results.append(
            f"### {idx}. {name}\n\n"
            f"{image_md}"
            f"- **특가**: {int(price):,}원{discount_text}{rocket_text}\n"
            f"- [구매하기]({short_url})\n"
        )

    return "\n".join(formatted_results)


@mcp.tool()
async def generate_coupang_deeplink(original_url: str) -> str:
    """
    쿠팡 상품 URL을 단축 링크로 변환합니다.

    Args:
        original_url (str): 쿠팡 상품 페이지 URL

    Returns:
        단축된 쿠팡 링크
    """
    data = await call_api("deeplink", {"url": original_url})

    if "error" in data:
        return f"오류: {data.get('message', data['error'])}"

    if data.get("rCode") != "0":
        return f"API 오류: {data.get('rMessage', '알 수 없는 오류')}"

    links = data.get("data", [])

    if not links:
        return "링크 생성에 실패했습니다."

    deeplink = links[0].get("shortenUrl", "")

    return f"## 쿠팡 단축 링크\n\n**원본**: {original_url}\n\n**단축 링크**: {deeplink}"


if __name__ == "__main__":
    mcp.run()
