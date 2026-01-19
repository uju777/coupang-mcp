import os
import hmac
import hashlib
import httpx
from time import strftime, gmtime
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from urllib.parse import urlencode

# .env 파일 로드
load_dotenv()

COUPANG_ACCESS_KEY = os.getenv("COUPANG_ACCESS_KEY")
COUPANG_SECRET_KEY = os.getenv("COUPANG_SECRET_KEY")

if not COUPANG_ACCESS_KEY or not COUPANG_SECRET_KEY:
    raise ValueError("Error: .env 파일에 COUPANG_ACCESS_KEY와 COUPANG_SECRET_KEY를 설정해주세요.")

DOMAIN = "https://api-gateway.coupang.com"

mcp = FastMCP("Coupang")


def generate_hmac(method: str, url_path: str, datetime: str) -> str:
    """HMAC 서명 생성 - 쿠팡 API 형식"""
    # 형식: datetime + method + path + query (공백 없이 연결)
    # url_path에는 쿼리스트링이 포함될 수 있음 (예: /path?param=value)
    message = datetime + method + url_path
    signature = hmac.new(
        COUPANG_SECRET_KEY.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return signature


def get_authorization_header(method: str, path: str, query_string: str = "") -> dict:
    """인증 헤더 생성"""
    # GMT 시간 사용: yymmddTHHmmssZ 형식
    datetime = strftime('%y%m%d', gmtime()) + 'T' + strftime('%H%M%S', gmtime()) + 'Z'

    # path + query_string 조합 (? 없이 직접 연결)
    url_path = path + query_string
    signature = generate_hmac(method, url_path, datetime)

    authorization = f"CEA algorithm=HmacSHA256, access-key={COUPANG_ACCESS_KEY}, signed-date={datetime}, signature={signature}"

    return {
        "Authorization": authorization,
        "Content-Type": "application/json;charset=UTF-8"
    }


@mcp.tool()
async def search_coupang_products(keyword: str, limit: int = 5) -> str:
    """
    쿠팡 API로 상품을 검색합니다.

    Args:
        keyword (str): 검색할 키워드 (예: "에어팟", "맥북프로")
        limit (int): 가져올 결과 개수 (기본 5개, 최대 100개)

    Returns:
        상품 목록 (이름, 가격, 상품 링크 포함)
    """
    path = "/v2/providers/affiliate_open_api/apis/openapi/v1/products/search"
    params = {
        "keyword": keyword,
        "limit": min(limit, 100)
    }
    query_string = urlencode(params)

    # HMAC 서명에 쿼리스트링 포함
    headers = get_authorization_header("GET", path, query_string)
    full_url = f"{DOMAIN}{path}?{query_string}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(full_url, headers=headers, timeout=30.0)
            response.raise_for_status()
            data = response.json()

            if data.get("rCode") != "0":
                return f"API 오류: {data.get('rMessage', '알 수 없는 오류')}"

            products = data.get("data", {}).get("productData", [])

            if not products:
                return f"'{keyword}' 검색 결과가 없습니다."

            formatted_results = [f"## 🛒 '{keyword}' 검색 결과\n"]

            for idx, product in enumerate(products[:limit], 1):
                name = product.get("productName", "")
                price = product.get("productPrice", 0)
                url = product.get("productUrl", "")
                image = product.get("productImage", "")
                is_rocket = product.get("isRocket", False)
                is_free_shipping = product.get("isFreeShipping", False)

                rocket_badge = "🚀 로켓배송" if is_rocket else ""
                shipping_badge = "📦 무료배송" if is_free_shipping else ""
                badges = " ".join(filter(None, [rocket_badge, shipping_badge]))

                # 이미지 마크다운 (있으면 표시)
                image_md = f"![{name[:20]}]({image})\n\n" if image else ""

                formatted_results.append(
                    f"### {idx}. {name}\n\n"
                    f"{image_md}"
                    f"- **가격**: {int(price):,}원 {badges}\n"
                    f"- **구매링크**: [{name[:30]}...]({url})\n"
                )

            return "\n".join(formatted_results)

        except httpx.HTTPStatusError as e:
            return f"HTTP 오류: {e.response.status_code} - {e.response.text}"
        except Exception as e:
            return f"오류 발생: {str(e)}"


@mcp.tool()
async def get_coupang_best_products(category_id: int = 1001, limit: int = 5) -> str:
    """
    쿠팡 카테고리별 베스트 상품을 조회합니다.

    Args:
        category_id (int): 카테고리 ID
            - 1001: 여성패션
            - 1002: 남성패션
            - 1010: 뷰티
            - 1011: 출산/유아동
            - 1012: 식품
            - 1013: 주방용품
            - 1014: 생활용품
            - 1015: 홈인테리어
            - 1016: 가전디지털
            - 1017: 스포츠/레저
            - 1018: 자동차용품
            - 1019: 도서/음반/DVD
            - 1020: 완구/취미
            - 1021: 문구/오피스
            - 1024: 헬스/건강식품
            - 1025: 국내여행
            - 1026: 해외여행
            - 1029: 반려동물용품
        limit (int): 가져올 결과 개수 (기본 5개, 최대 100개)

    Returns:
        베스트 상품 목록
    """
    category_names = {
        1001: "여성패션", 1002: "남성패션", 1010: "뷰티",
        1011: "출산/유아동", 1012: "식품", 1013: "주방용품",
        1014: "생활용품", 1015: "홈인테리어", 1016: "가전디지털",
        1017: "스포츠/레저", 1018: "자동차용품", 1019: "도서/음반/DVD",
        1020: "완구/취미", 1021: "문구/오피스", 1024: "헬스/건강식품",
        1025: "국내여행", 1026: "해외여행", 1029: "반려동물용품"
    }

    # categoryId는 path에 포함
    path = f"/v2/providers/affiliate_open_api/apis/openapi/products/bestcategories/{category_id}"
    params = {
        "limit": min(limit, 100)
    }
    query_string = urlencode(params)

    # HMAC 서명에 쿼리스트링 포함
    headers = get_authorization_header("GET", path, query_string)
    full_url = f"{DOMAIN}{path}?{query_string}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(full_url, headers=headers, timeout=30.0)
            response.raise_for_status()
            data = response.json()

            if data.get("rCode") != "0":
                return f"API 오류: {data.get('rMessage', '알 수 없는 오류')}"

            products = data.get("data", [])

            if not products:
                return f"카테고리 {category_id} 베스트 상품이 없습니다."

            category_name = category_names.get(category_id, str(category_id))
            formatted_results = [f"## 🏆 [{category_name}] 베스트 상품\n"]

            for idx, product in enumerate(products[:limit], 1):
                name = product.get("productName", "")
                price = product.get("productPrice", 0)
                url = product.get("productUrl", "")
                image = product.get("productImage", "")
                rank = product.get("rank", idx)
                is_rocket = product.get("isRocket", False)

                rocket_badge = "🚀 로켓배송" if is_rocket else ""
                image_md = f"![{name[:20]}]({image})\n\n" if image else ""

                formatted_results.append(
                    f"### {rank}위. {name}\n\n"
                    f"{image_md}"
                    f"- **가격**: {int(price):,}원 {rocket_badge}\n"
                    f"- **구매링크**: [{name[:30]}...]({url})\n"
                )

            return "\n".join(formatted_results)

        except httpx.HTTPStatusError as e:
            return f"HTTP 오류: {e.response.status_code} - {e.response.text}"
        except Exception as e:
            return f"오류 발생: {str(e)}"


@mcp.tool()
async def generate_coupang_deeplink(original_url: str) -> str:
    """
    쿠팡 상품 URL을 딥링크로 변환합니다.

    Args:
        original_url (str): 쿠팡 상품 페이지 URL

    Returns:
        변환된 딥링크
    """
    path = "/v2/providers/affiliate_open_api/apis/openapi/v1/deeplink"

    headers = get_authorization_header("POST", path)
    full_url = f"{DOMAIN}{path}"

    body = {
        "coupangUrls": [original_url]
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(full_url, headers=headers, json=body, timeout=30.0)
            response.raise_for_status()
            data = response.json()

            if data.get("rCode") != "0":
                return f"API 오류: {data.get('rMessage', '알 수 없는 오류')}"

            links = data.get("data", [])

            if not links:
                return "딥링크 생성에 실패했습니다."

            deeplink = links[0].get("shortenUrl", "")

            return f"## 🔗 딥링크 생성 완료\n\n**원본 URL**: {original_url}\n\n**상품 링크**: {deeplink}\n\n> 이 링크로 구매 가능합니다."

        except httpx.HTTPStatusError as e:
            return f"HTTP 오류: {e.response.status_code} - {e.response.text}"
        except Exception as e:
            return f"오류 발생: {str(e)}"


@mcp.tool()
async def get_coupang_goldbox(limit: int = 10) -> str:
    """
    쿠팡 골드박스 (오늘의 특가/할인) 상품을 조회합니다.

    Args:
        limit (int): 가져올 결과 개수 (기본 10개, 최대 100개)

    Returns:
        골드박스 특가 상품 목록
    """
    path = "/v2/providers/affiliate_open_api/apis/openapi/products/goldbox"
    params = {"limit": min(limit, 100)}
    query_string = urlencode(params)

    headers = get_authorization_header("GET", path, query_string)
    full_url = f"{DOMAIN}{path}?{query_string}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(full_url, headers=headers, timeout=30.0)
            response.raise_for_status()
            data = response.json()

            if data.get("rCode") != "0":
                return f"API 오류: {data.get('rMessage', '알 수 없는 오류')}"

            products = data.get("data", [])

            if not products:
                return "골드박스 상품이 없습니다."

            formatted_results = ["## 🎁 골드박스 특가 상품\n"]

            for idx, product in enumerate(products[:limit], 1):
                name = product.get("productName", "")
                price = product.get("productPrice", 0)
                original_price = product.get("originalPrice", price)
                url = product.get("productUrl", "")
                image = product.get("productImage", "")
                is_rocket = product.get("isRocket", False)
                discount_rate = product.get("discountRate", 0)

                rocket_badge = "🚀 로켓배송" if is_rocket else ""
                discount_text = f"({discount_rate}% 할인)" if discount_rate else ""
                image_md = f"![{name[:20]}]({image})\n\n" if image else ""

                formatted_results.append(
                    f"### {idx}. {name}\n\n"
                    f"{image_md}"
                    f"- **특가**: {int(price):,}원 {discount_text} {rocket_badge}\n"
                    f"- **구매링크**: [{name[:30]}...]({url})\n"
                )

            return "\n".join(formatted_results)

        except httpx.HTTPStatusError as e:
            return f"HTTP 오류: {e.response.status_code} - {e.response.text}"
        except Exception as e:
            return f"오류 발생: {str(e)}"


if __name__ == "__main__":
    mcp.run()
