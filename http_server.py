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
**💡 꿀팁:** `{keyword} 리퍼/B급/전시` → 30~70% 저렴 | 🚀로켓=빠른교환 | 🏷️판매자=가격↓

**🎯 다음 뭐 할까요? (번호로 답해주세요)**
1️⃣ **가격순** 정렬
2️⃣ **100g당 가격** 계산
3️⃣ **비교표**로 정리
4️⃣ `{keyword} 리퍼` 검색

⚠️ *검색 결과만 제공. 실시간 재고/배송 확인은 링크 클릭해서 쿠팡에서 직접 확인하세요.*
"""


def get_best_cta(category_name: str) -> str:
    return f"""
---
**💡 꿀팁:** 1~3위 광고 가능성↑ → 4~10위도 체크! | 같은상품 판매자별 가격 다름

**🎯 다음 뭐 할까요? (번호로 답해주세요)**
1️⃣ **1위 상품** 상세검색
2️⃣ **다른 카테고리** 베스트
3️⃣ **골드박스** 특가
4️⃣ **10개 더** 보기

⚠️ *검색 결과만 제공. 실시간 재고/배송 확인은 링크 클릭해서 쿠팡에서 직접 확인하세요.*
"""


def get_goldbox_cta() -> str:
    return """
---
**💡 꿀팁:** 골드박스 = 한정수량 (품절 빠름!) | 할인율 50%↑ = 원가 뻥튀기 의심

**🎯 다음 뭐 할까요? (번호로 답해주세요)**
1️⃣ 관심상품 **상세검색**
2️⃣ **카테고리별** 베스트
3️⃣ **가격순** 정렬
4️⃣ **비교표**로 정리

⚠️ *검색 결과만 제공. 실시간 재고/배송 확인은 링크 클릭해서 쿠팡에서 직접 확인하세요.*
"""


@mcp.tool()
async def search_coupang_products(keyword: str, limit: int = 5) -> str:
    """
    쿠팡에서 상품을 검색합니다.

    🎯 **이 도구를 호출해야 하는 키워드:**
    쇼핑, 최저가, 뭐사지, 뭐살까, 추천해줘, 가격, 검색, 사고싶다, 구매,
    얼마, 할인, 특가, 싼 거, 저렴한, 가성비, 로켓배송, 새벽배송

    ⚠️ 사용자가 추상적으로 요청하면 (예: "에어팟 찾아줘") 바로 검색하지 말고,
    먼저 아래 질문을 해주세요:
    "✅ 쿠팡에서 '{keyword}' 찾는 거 맞지? 아래 중 번호로 골라줘:
    1) 최저가 위주 2) 로켓배송만 3) 리뷰많은순 4) 선물용
    예산도 알려주면 더 정확해!"

    Args:
        keyword (str): 검색할 키워드 (예: "에어팟 프로2", "맥북프로 14인치")
        limit (int): 결과 개수 (기본 5개)

    Returns:
        TOP 5 상품 + 다음 행동 선택지
    """
    data = await call_api("search", {"keyword": keyword, "limit": limit})

    if "error" in data:
        return f"오류: {data.get('message', data['error'])}"

    if data.get("rCode") != "0":
        return f"API 오류: {data.get('rMessage', '알 수 없는 오류')}"

    products = data.get("data", {}).get("productData", [])

    if not products:
        return f"'{keyword}' 검색 결과가 없습니다."

    # 로켓배송 개수 카운트
    rocket_count = sum(1 for p in products[:limit] if p.get("isRocket", False))
    prices = [p.get("productPrice", 0) for p in products[:limit]]
    min_price = min(prices) if prices else 0
    max_price = max(prices) if prices else 0

    # 1줄 요약
    formatted_results = [
        f"# 🔍 '{keyword}' TOP {len(products[:limit])}\n",
        f"> 💰 {int(min_price):,}원 ~ {int(max_price):,}원 | 🚀로켓 {rocket_count}개\n"
    ]

    for idx, product in enumerate(products[:limit], 1):
        name = product.get("productName", "")
        price = product.get("productPrice", 0)
        url = product.get("productUrl", "")
        is_rocket = product.get("isRocket", False)
        is_free_shipping = product.get("isFreeShipping", False)

        # 배송 타입 구분
        if is_rocket:
            delivery = "🚀"
        else:
            delivery = "🏷️"

        if is_free_shipping:
            delivery += "무배"

        short_url = await shorten_url(url)

        formatted_results.append(
            f"**{idx}) {name}** {delivery}\n"
            f"💰 {int(price):,}원 → [이미지/리뷰 보기]({short_url})\n"
        )

    formatted_results.append(get_search_cta(keyword))
    return "\n".join(formatted_results)


@mcp.tool()
async def get_coupang_best_products(category_id: int = 1016, limit: int = 5) -> str:
    """
    쿠팡 카테고리별 베스트 상품을 조회합니다.

    🎯 **이 도구를 호출해야 하는 키워드:**
    베스트, 인기, 많이팔린, 잘나가는, 순위, 랭킹, 1위, TOP, 핫한

    ⚠️ 카테고리를 모르면 먼저 물어보세요:
    "어떤 카테고리 베스트 볼까? 1)가전 2)식품 3)패션 4)뷰티"

    Args:
        category_id: 1016=가전, 1012=식품, 1001=여성패션, 1002=남성패션, 1010=뷰티, 1024=건강식품
        limit: 결과 개수 (기본 5개)
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

    # 가격 범위 계산
    prices = [p.get("productPrice", 0) for p in products[:limit]]
    rocket_count = sum(1 for p in products[:limit] if p.get("isRocket", False))

    formatted_results = [
        f"# 🏆 [{category_name}] 베스트 TOP {len(products[:limit])}\n",
        f"> 💰 {int(min(prices)):,}원 ~ {int(max(prices)):,}원 | 🚀로켓 {rocket_count}개\n"
    ]

    for idx, product in enumerate(products[:limit], 1):
        name = product.get("productName", "")
        price = product.get("productPrice", 0)
        url = product.get("productUrl", "")
        rank = product.get("rank", idx)
        is_rocket = product.get("isRocket", False)

        delivery = "🚀" if is_rocket else "🏷️"
        short_url = await shorten_url(url)
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"{rank})")

        formatted_results.append(
            f"**{medal} {name}** {delivery}\n"
            f"💰 {int(price):,}원 → [이미지/리뷰 보기]({short_url})\n"
        )

    formatted_results.append(get_best_cta(category_name))
    return "\n".join(formatted_results)


@mcp.tool()
async def get_coupang_goldbox(limit: int = 10) -> str:
    """
    쿠팡 골드박스 (오늘의 특가/할인) 상품을 조회합니다.

    🎯 **이 도구를 호출해야 하는 키워드:**
    특가, 할인, 세일, 오늘만, 타임딜, 핫딜, 떨이, 골드박스, 반값

    한정수량 특가라 품절이 빠릅니다!

    Args:
        limit: 결과 개수 (기본 10개)
    """
    data = await call_api("goldbox", {"limit": limit})

    if "error" in data:
        return f"오류: {data.get('message', data['error'])}"

    if data.get("rCode") != "0":
        return f"API 오류: {data.get('rMessage', '알 수 없는 오류')}"

    products = data.get("data", [])

    if not products:
        return "골드박스 상품이 없습니다."

    # 통계 계산
    prices = [p.get("productPrice", 0) for p in products[:limit]]
    discounts = [p.get("discountRate", 0) for p in products[:limit] if p.get("discountRate", 0) > 0]
    avg_discount = sum(discounts) // len(discounts) if discounts else 0
    rocket_count = sum(1 for p in products[:limit] if p.get("isRocket", False))

    formatted_results = [
        f"# 🔥 골드박스 특가 TOP {len(products[:limit])}\n",
        f"> 💰 {int(min(prices)):,}원 ~ {int(max(prices)):,}원 | 평균 -{avg_discount}% | 🚀로켓 {rocket_count}개\n"
    ]

    for idx, product in enumerate(products[:limit], 1):
        name = product.get("productName", "")
        price = product.get("productPrice", 0)
        url = product.get("productUrl", "")
        is_rocket = product.get("isRocket", False)
        discount_rate = product.get("discountRate", 0)

        delivery = "🚀" if is_rocket else "🏷️"

        # 할인율 표시 (30% 이상이면 핫딜 강조)
        if discount_rate >= 30:
            discount_text = f" 🔥-{discount_rate}%"
        elif discount_rate > 0:
            discount_text = f" -{discount_rate}%"
        else:
            discount_text = ""

        short_url = await shorten_url(url)

        formatted_results.append(
            f"**{idx}) {name}** {delivery}{discount_text}\n"
            f"💰 {int(price):,}원 → [이미지/리뷰 보기]({short_url})\n"
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
