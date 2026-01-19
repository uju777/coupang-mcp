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


def format_price_range(price: int) -> str:
    """가격을 대략적인 범위로 표시 (API vs 실제 가격 차이 때문)"""
    if price < 5000:
        return "5천원 미만"
    elif price < 10000:
        return f"약 {price // 1000}천원대"
    elif price < 50000:
        # 1만~5만: 만원 단위
        base = (price // 10000) * 10000
        return f"약 {base // 10000}만원대"
    elif price < 100000:
        # 5만~10만: 5만원대, 6만원대...
        base = (price // 10000) * 10000
        return f"약 {base // 10000}만원대"
    elif price < 1000000:
        # 10만~100만: 10만원대, 20만원대...
        base = (price // 100000) * 100000
        high = base + 100000
        return f"{base // 10000}~{high // 10000}만원"
    else:
        # 100만 이상: 100만원대, 200만원대...
        base = (price // 1000000) * 1000000
        return f"약 {base // 10000}만원대"


def truncate_name(name: str, max_len: int = 30) -> str:
    """상품명 자르기 (가독성)"""
    if len(name) <= max_len:
        return name
    return name[:max_len-2] + ".."


# 카테고리별 구매 체크리스트 (팩트 기반, 할루시네이션 X)
# - 변하지 않는 스펙 항목만
# - 일반적인 조언만
# - 구체적 수치/가격 X
BUYING_TIPS = {
    # ============ 전자기기 ============
    "모니터": {
        "keywords": ["모니터", "monitor", "디스플레이"],
        "checks": ["해상도 (FHD/QHD/4K)", "주사율 (게임용은 높을수록)", "패널 종류 (IPS/VA/TN)"],
        "tip": "받으면 빛샘/데드픽셀 점검 (교환 기한 내)"
    },
    "노트북": {
        "keywords": ["노트북", "laptop", "맥북", "macbook", "그램", "갤럭시북", "thinkpad"],
        "checks": ["CPU 세대", "RAM 용량", "SSD 용량", "무게"],
        "tip": "배터리 실사용시간은 후기에서 확인"
    },
    "TV": {
        "keywords": ["tv", "티비", "텔레비전", "올레드", "qled"],
        "checks": ["패널 종류 (OLED/QLED/LED)", "화면 크기", "스마트TV 기능"],
        "tip": "설치비, 벽걸이 비용 별도인지 확인"
    },
    "스마트폰": {
        "keywords": ["폰", "phone", "아이폰", "iphone", "갤럭시", "galaxy"],
        "checks": ["저장용량", "카메라 성능", "배터리 용량"],
        "tip": "자급제 vs 약정 가격 비교"
    },
    "태블릿": {
        "keywords": ["태블릿", "아이패드", "ipad", "갤럭시탭"],
        "checks": ["화면 크기", "저장용량", "펜슬 지원 여부", "셀룰러 유무"],
        "tip": "키보드, 펜슬 별매인지 확인"
    },
    "이어폰": {
        "keywords": ["이어폰", "에어팟", "airpods", "버즈", "헤드폰", "헤드셋"],
        "checks": ["노이즈캔슬링 유무", "배터리 시간", "방수등급"],
        "tip": "이어팁 사이즈 후기 참고"
    },
    "스피커": {
        "keywords": ["스피커", "speaker", "블루투스스피커", "사운드바"],
        "checks": ["출력 (W)", "연결 방식 (블루투스/유선)", "방수 여부"],
        "tip": "실사용 음질은 후기 영상으로 확인"
    },
    "키보드": {
        "keywords": ["키보드", "keyboard", "기계식", "무접점"],
        "checks": ["스위치 타입", "배열 (풀배열/텐키리스)", "유선/무선"],
        "tip": "타건감은 직접 체험이 best"
    },
    "마우스": {
        "keywords": ["마우스", "mouse", "로지텍", "버티컬"],
        "checks": ["유선/무선", "그립감", "DPI"],
        "tip": "손목 불편하면 버티컬 마우스 고려"
    },
    "웹캠": {
        "keywords": ["웹캠", "webcam", "화상카메라"],
        "checks": ["해상도 (720p/1080p/4K)", "프레임 (30fps/60fps)", "마이크 내장"],
        "tip": "화각(시야각)도 확인"
    },
    "외장하드": {
        "keywords": ["외장하드", "외장ssd", "ssd", "hdd", "저장장치"],
        "checks": ["용량", "읽기/쓰기 속도", "연결 방식 (USB/썬더볼트)"],
        "tip": "SSD가 HDD보다 빠르고 충격에 강함"
    },
    "충전기": {
        "keywords": ["충전기", "어댑터", "케이블", "고속충전"],
        "checks": ["출력 (W)", "포트 개수", "호환 기기"],
        "tip": "정품 인증 제품인지 확인"
    },
    "프린터": {
        "keywords": ["프린터", "복합기", "잉크젯", "레이저"],
        "checks": ["잉크젯/레이저", "컬러/흑백", "복합기능 (스캔/복사)"],
        "tip": "잉크/토너 가격도 미리 확인"
    },

    # ============ 가전제품 ============
    "냉장고": {
        "keywords": ["냉장고", "김치냉장고"],
        "checks": ["용량 (L)", "에너지 효율 등급", "도어 타입"],
        "tip": "효율등급 따라 전기세 차이 있음"
    },
    "세탁기": {
        "keywords": ["세탁기", "건조기", "워시타워"],
        "checks": ["용량 (kg)", "에너지 효율", "통세척 기능"],
        "tip": "건조기는 히트펌프 방식이 효율 좋음"
    },
    "청소기": {
        "keywords": ["청소기", "로봇청소기", "무선청소기", "다이슨"],
        "checks": ["흡입력", "배터리 시간", "먼지통 용량"],
        "tip": "소모품 가격도 미리 확인"
    },
    "에어컨": {
        "keywords": ["에어컨", "에어콘", "냉난방기"],
        "checks": ["냉방 면적 (평수)", "에너지 효율", "인버터 유무"],
        "tip": "설치비 별도인 경우 많음"
    },
    "공기청정기": {
        "keywords": ["공기청정기", "미세먼지"],
        "checks": ["청정 면적", "필터 타입", "소음"],
        "tip": "필터 교체 주기/가격도 확인"
    },
    "제습기": {
        "keywords": ["제습기", "가습기"],
        "checks": ["제습/가습 용량", "적정 면적", "물통 크기"],
        "tip": "연속배수 가능하면 물 버리기 편함"
    },
    "전자레인지": {
        "keywords": ["전자레인지", "오븐", "광파오븐"],
        "checks": ["용량 (L)", "출력 (W)", "부가기능 (그릴/오븐)"],
        "tip": "내부 크기가 실제 조리 용량"
    },
    "밥솥": {
        "keywords": ["밥솥", "압력밥솥", "전기밥솥"],
        "checks": ["인원수 (인분)", "압력/일반", "내솥 재질"],
        "tip": "내솥 코팅 수명도 고려"
    },
    "선풍기": {
        "keywords": ["선풍기", "서큘레이터", "에어컨선풍기"],
        "checks": ["날개 유무 (일반/날개없는)", "풍량 단계", "타이머"],
        "tip": "소음 dB 확인 (침실용)"
    },
    "드라이기": {
        "keywords": ["드라이기", "헤어드라이어", "고데기"],
        "checks": ["출력 (W)", "온도/풍량 조절", "무게"],
        "tip": "머리카락 손상 적은 이온 기능 확인"
    },

    # ============ 가구/인테리어 ============
    "의자": {
        "keywords": ["의자", "체어", "chair", "게이밍체어", "사무용의자"],
        "checks": ["등받이 각도", "팔걸이 조절", "메쉬/쿠션"],
        "tip": "허리 안 좋으면 요추 지지대 확인"
    },
    "책상": {
        "keywords": ["책상", "데스크", "컴퓨터책상", "모션데스크", "스탠딩"],
        "checks": ["가로 길이", "높이 조절 여부", "상판 두께"],
        "tip": "모니터암 쓸 거면 상판 두께 확인"
    },
    "매트리스": {
        "keywords": ["매트리스", "침대", "토퍼"],
        "checks": ["경도 (단단함 정도)", "소재", "사이즈"],
        "tip": "개인차 크니 체험 가능 제품 추천"
    },
    "소파": {
        "keywords": ["소파", "쇼파", "리클라이너"],
        "checks": ["크기 (인용)", "소재 (가죽/패브릭)", "조립 필요 여부"],
        "tip": "배송 시 문 통과 가능한지 확인"
    },
    "수납장": {
        "keywords": ["수납장", "서랍장", "옷장", "행거"],
        "checks": ["크기", "칸 개수", "조립 필요 여부"],
        "tip": "조립 난이도 후기 확인"
    },
    "커튼": {
        "keywords": ["커튼", "블라인드", "암막"],
        "checks": ["크기 (창문에 맞는지)", "암막/일반", "세탁 가능 여부"],
        "tip": "창문 실측 후 구매"
    },

    # ============ 건강/뷰티 ============
    "영양제": {
        "keywords": ["영양제", "비타민", "오메가3", "유산균", "프로바이오틱스"],
        "checks": ["함량", "원료", "인증마크"],
        "tip": "복용 중인 약과 상호작용 확인"
    },
    "화장품": {
        "keywords": ["화장품", "스킨케어", "선크림", "에센스", "로션"],
        "checks": ["피부 타입", "성분", "유통기한"],
        "tip": "병행수입은 정품 여부 확인"
    },
    "체중계": {
        "keywords": ["체중계", "인바디", "체지방"],
        "checks": ["측정 항목 (체중만/체지방)", "앱 연동", "최대 측정 무게"],
        "tip": "체지방 수치는 참고용"
    },
    "안마기": {
        "keywords": ["안마기", "안마의자", "마사지기", "어깨안마기"],
        "checks": ["부위 (전신/부분)", "강도 조절", "크기"],
        "tip": "소음과 실제 마사지 강도 후기 확인"
    },

    # ============ 식품 ============
    "과일": {
        "keywords": ["사과", "배", "귤", "딸기", "포도", "수박", "과일", "망고", "바나나"],
        "checks": ["등급", "산지", "중량"],
        "tip": "제철 과일이 맛도 좋고 가격도 저렴"
    },
    "고기": {
        "keywords": ["소고기", "돼지고기", "닭고기", "한우", "삼겹살", "목살"],
        "checks": ["등급", "부위", "냉장/냉동", "원산지"],
        "tip": "g당 가격으로 비교"
    },
    "해산물": {
        "keywords": ["새우", "연어", "고등어", "참치", "회", "해산물", "전복"],
        "checks": ["원산지", "양식/자연산", "냉장/냉동"],
        "tip": "냉동이 오히려 신선할 수 있음 (선상냉동)"
    },
    "쌀": {
        "keywords": ["쌀", "현미", "잡곡"],
        "checks": ["품종", "도정일", "중량"],
        "tip": "도정일 최근일수록 신선"
    },
    "커피": {
        "keywords": ["커피", "원두", "캡슐커피", "드립백"],
        "checks": ["로스팅 날짜", "원산지", "분쇄 여부"],
        "tip": "원두는 로스팅 후 2주 내가 맛 좋음"
    },
    "생수": {
        "keywords": ["생수", "물", "탄산수", "미네랄워터"],
        "checks": ["용량", "경도 (연수/경수)", "원산지"],
        "tip": "무거우니 배송 추천"
    },
    "라면": {
        "keywords": ["라면", "컵라면", "봉지라면"],
        "checks": ["개수", "맛", "유통기한"],
        "tip": "박스 단위가 개당 가격 저렴"
    },

    # ============ 유아용품 ============
    "기저귀": {
        "keywords": ["기저귀", "팬티기저귀", "하기스", "팸퍼스"],
        "checks": ["사이즈 (체중 기준)", "흡수력", "피부 자극"],
        "tip": "아기마다 맞는 브랜드 다름"
    },
    "분유": {
        "keywords": ["분유", "앱솔루트", "남양", "매일"],
        "checks": ["단계 (개월수)", "성분"],
        "tip": "아기마다 맞는 분유 다르니 소량 테스트"
    },
    "유모차": {
        "keywords": ["유모차", "휴대용유모차", "디럭스유모차"],
        "checks": ["무게", "접이식 여부", "바퀴 크기"],
        "tip": "직접 접어보고 무게 확인 추천"
    },
    "카시트": {
        "keywords": ["카시트", "주니어카시트", "신생아카시트"],
        "checks": ["연령/체중 범위", "ISOFIX 지원", "인증마크"],
        "tip": "차량 시트와 호환되는지 확인"
    },

    # ============ 반려동물 ============
    "사료": {
        "keywords": ["사료", "강아지사료", "고양이사료", "습식", "건식"],
        "checks": ["주원료", "연령별", "알러지 성분"],
        "tip": "새 사료는 기존 것과 섞어서 천천히 전환"
    },
    "간식": {
        "keywords": ["강아지간식", "고양이간식", "덴탈껌", "츄르"],
        "checks": ["원료", "칼로리", "급여량"],
        "tip": "급여량 지키기 (비만 주의)"
    },
    "배변패드": {
        "keywords": ["배변패드", "패드", "배변판"],
        "checks": ["사이즈", "흡수력", "매수"],
        "tip": "대용량이 장당 가격 저렴"
    },

    # ============ 자동차용품 ============
    "블랙박스": {
        "keywords": ["블랙박스", "dashcam", "차량카메라"],
        "checks": ["채널 (전방/후방)", "화질", "주차모드"],
        "tip": "메모리 카드 별매인지 확인"
    },
    "타이어": {
        "keywords": ["타이어", "사계절타이어", "겨울타이어"],
        "checks": ["사이즈 (차량에 맞는지)", "계절", "제조일"],
        "tip": "제조일 3년 이내 추천"
    },
    "차량용품": {
        "keywords": ["차량용충전기", "거치대", "방향제", "핸들커버"],
        "checks": ["호환 차종", "크기"],
        "tip": "차량 내부 크기에 맞는지 확인"
    },

    # ============ 패션 ============
    "신발": {
        "keywords": ["신발", "운동화", "스니커즈", "구두", "슬리퍼"],
        "checks": ["사이즈", "발볼 (넓음/좁음)", "용도"],
        "tip": "브랜드마다 사이즈 다르니 후기 참고"
    },
    "가방": {
        "keywords": ["가방", "백팩", "크로스백", "토트백"],
        "checks": ["크기", "수납 공간", "무게"],
        "tip": "실제 수납력은 후기 사진 참고"
    },
    "시계": {
        "keywords": ["시계", "손목시계", "스마트워치"],
        "checks": ["사이즈 (손목 둘레)", "방수 등급", "배터리/충전"],
        "tip": "스마트워치는 폰 호환 여부 확인"
    },

    # ============ 생활용품 ============
    "수건": {
        "keywords": ["수건", "타월", "목욕타월"],
        "checks": ["사이즈", "소재 (면/극세사)", "중량"],
        "tip": "중량 높을수록 두껍고 흡수력 좋음"
    },
    "이불": {
        "keywords": ["이불", "침구", "베개", "토퍼"],
        "checks": ["사이즈", "충전재", "세탁 가능 여부"],
        "tip": "계절에 맞는 충전재 선택"
    },
    "세제": {
        "keywords": ["세제", "세탁세제", "섬유유연제", "주방세제"],
        "checks": ["용량", "액체/캡슐", "향"],
        "tip": "대용량이 ml당 저렴"
    },
    "휴지": {
        "keywords": ["휴지", "화장지", "키친타월", "물티슈"],
        "checks": ["롤수/매수", "겹수", "평량"],
        "tip": "대용량 박스가 롤당 저렴"
    },
}


def get_coupang_secret(keyword: str) -> str:
    """쿠팡 특화 꿀팁 - 제거 (할루시네이션 위험)"""
    return ""


def get_buying_tip(keyword: str) -> str:
    """검색 키워드에 맞는 구매 팁 반환 (가독성 좋게)"""
    keyword_lower = keyword.lower()
    for category, data in BUYING_TIPS.items():
        for kw in data["keywords"]:
            if kw in keyword_lower:
                # 체크리스트를 줄바꿈으로 보기 좋게
                checks = data.get("checks", [])
                tip = data.get("tip", "")

                result = f"\n📋 **{category} 살 때 체크할 것**\n"
                for check in checks:
                    result += f"  - {check}\n"
                if tip:
                    result += f"\n💡 {tip}\n"
                return result
    return ""


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
_Tip: `{keyword} 리퍼` 검색 → 30~70% 저렴 | 찜하면 가격알림_

**다음은?**
> 1) 가격순 정렬
> 2) 비교표로 보기
> 3) 베스트 TOP 10
> 4) 오늘의 특가
"""


def get_best_cta(category_name: str) -> str:
    return f"""
---
_Tip: 1~3위는 광고 가능성↑ 4위부터도 체크 | 첫구매 쿠폰 확인_

**다음은?**
> 1) 1위로 검색 (최저가)
> 2) 오늘의 특가
> 3) 다른 카테고리
> 4) 20개 더 보기
"""


def get_goldbox_cta() -> str:
    return """
---
_Tip: 50%↑ 할인은 원가 의심 | 찜하면 가격알림_

**다음은?**
> 1) 상품 검색
> 2) 베스트 TOP 10
> 3) 비교표로 보기
> 4) 20개 더 보기
"""


@mcp.tool()
async def search_coupang_products(keyword: str, limit: int = 5) -> str:
    """
    쿠팡에서 상품을 검색합니다.

    **트리거 키워드:** 쇼핑, 최저가, 뭐사지, 추천, 가격, 검색, 구매, 할인, 가성비

    ⚠️ 추상적 요청(뭐사지, 추천해줘)은 먼저 물어보기:
    "쿠팡 검색! 번호로 답해주세요:
    1. 최저가/가성비
    2. 로켓배송만
    3. 선물용
    4. 직접 검색어 입력

    예산 있으면 같이! (예: 30만원 이하)"

    Args:
        keyword: 검색 키워드
        limit: 결과 개수 (기본 5)
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

    # 구매 팁 + 쿠팡 꿀팁 (키워드 매칭)
    buying_tip = get_buying_tip(keyword)
    coupang_secret = get_coupang_secret(keyword)

    # 1줄 요약 + Claude 지시
    formatted_results = [
        f"# '{keyword}' 검색결과 TOP {len(products[:limit])}\n",
        f"> {int(min_price):,}원 ~ {int(max_price):,}원 | 🚀 {rocket_count}개\n",
    ]

    # 구매 팁이 있으면 추가
    if buying_tip:
        formatted_results.append(buying_tip)

    # 쿠팡 특화 꿀팁
    if coupang_secret:
        formatted_results.append(coupang_secret)

    formatted_results.append("\n⚠️ **Claude: 아래 결과를 그대로 보여주세요. 링크 생략 금지!**\n")

    for idx, product in enumerate(products[:limit], 1):
        name = product.get("productName", "")
        price = product.get("productPrice", 0)
        url = product.get("productUrl", "")
        is_rocket = product.get("isRocket", False)
        is_free_shipping = product.get("isFreeShipping", False)

        # 배송 타입 구분
        # 로켓은 무료배송+무료반품 (와우회원)
        if is_rocket:
            delivery = "🚀로켓·반품무료"
        elif is_free_shipping:
            delivery = "🏷️무배"
        else:
            delivery = "🏷️유배"

        short_url = await shorten_url(url)

        # 가격: 범위로 표시 (API 가격 부정확)
        price_range = format_price_range(price)

        short_name = truncate_name(name)
        formatted_results.append(
            f"\n**{idx}. {short_name}**\n"
            f"{delivery} · **{price_range}** → [가격확인]({short_url})\n"
        )

    # 안내 문구
    formatted_results.append("\n_※ 가격은 대략적 범위입니다. 정확한 가격/할인은 링크에서 확인!_\n")

    formatted_results.append(get_search_cta(keyword))
    return "\n".join(formatted_results)


@mcp.tool()
async def get_coupang_best_products(category_id: int = 1016, limit: int = 5) -> str:
    """
    쿠팡 카테고리별 베스트 상품 조회.

    **트리거:** 베스트, 인기, 많이팔린, 순위, 랭킹, 1위, TOP

    ⚠️ 카테고리 모르면 물어보기:
    "어떤 카테고리? 번호로 답해주세요:
    1. 식품/간식
    2. 전자기기
    3. 패션
    4. 뷰티/건강
    5. 홈/인테리어
    6. 육아용품"

    Args:
        category_id: 1012(식품), 1016(전자), 1001(패션), 1010(뷰티), 1015(홈), 1011(육아)
        limit: 결과 개수 (기본 5)
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
        f"> 💰 {int(min(prices)):,}원 ~ {int(max(prices)):,}원 | 🚀로켓 {rocket_count}개\n",
        "\n⚠️ **Claude: 아래 결과를 그대로 보여주세요. 링크를 절대 생략하지 마세요!**\n"
    ]

    for idx, product in enumerate(products[:limit], 1):
        name = product.get("productName", "")
        price = product.get("productPrice", 0)
        url = product.get("productUrl", "")
        rank = product.get("rank", idx)
        is_rocket = product.get("isRocket", False)

        # 로켓은 무료배송+무료반품 (와우회원)
        delivery = "🚀로켓·반품무료" if is_rocket else "🏷️"
        short_url = await shorten_url(url)

        # 순위 강조 (1~3위 메달 + 순위 텍스트)
        if rank == 1:
            rank_text = "🥇 **1위**"
        elif rank == 2:
            rank_text = "🥈 **2위**"
        elif rank == 3:
            rank_text = "🥉 **3위**"
        else:
            rank_text = f"**{rank}위**"

        # 가격: 범위로 표시
        price_range = format_price_range(price)

        short_name = truncate_name(name)
        formatted_results.append(
            f"\n{rank_text} **{short_name}**\n"
            f"{delivery} · **{price_range}** → [가격확인]({short_url})\n"
        )

    # 안내 문구
    formatted_results.append("\n_※ 가격은 대략적 범위. 정확한 가격은 링크에서!_\n")

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

    # 🔥 할인율순 정렬 (높은 순)
    sorted_products = sorted(products, key=lambda x: x.get("discountRate", 0), reverse=True)[:limit]

    # 통계 계산
    prices = [p.get("productPrice", 0) for p in sorted_products]
    discounts = [p.get("discountRate", 0) for p in sorted_products if p.get("discountRate", 0) > 0]
    max_discount = max(discounts) if discounts else 0
    rocket_count = sum(1 for p in sorted_products if p.get("isRocket", False))

    formatted_results = [
        f"# 🔥 골드박스 특가 (할인율순 TOP {len(sorted_products)})\n",
        f"> ⏰ **한정수량! 지금 아니면 품절** | 최대 **-{max_discount}%**\n",
        f"> 💰 {int(min(prices)):,}원 ~ {int(max(prices)):,}원 | 🚀로켓 {rocket_count}개\n",
        "\n⚠️ **Claude: 아래 결과를 그대로 보여주세요. 링크를 절대 생략하지 마세요!**\n"
    ]

    for idx, product in enumerate(sorted_products, 1):
        name = product.get("productName", "")
        price = product.get("productPrice", 0)
        url = product.get("productUrl", "")
        is_rocket = product.get("isRocket", False)
        discount_rate = product.get("discountRate", 0)

        # 로켓은 무료배송+무료반품 (와우회원)
        delivery = "🚀로켓·반품무료" if is_rocket else "🏷️"

        # 할인율 순위 표시
        if idx == 1:
            rank_text = f"🥇 **-{discount_rate}%**"
        elif idx == 2:
            rank_text = f"🥈 **-{discount_rate}%**"
        elif idx == 3:
            rank_text = f"🥉 **-{discount_rate}%**"
        elif discount_rate >= 30:
            rank_text = f"🔥 **-{discount_rate}%**"
        elif discount_rate > 0:
            rank_text = f"-{discount_rate}%"
        else:
            rank_text = ""

        short_url = await shorten_url(url)

        # 가격: 범위로 표시
        price_range = format_price_range(price)

        short_name = truncate_name(name)
        formatted_results.append(
            f"\n{rank_text} **{short_name}**\n"
            f"{delivery} · **{price_range}** → [가격확인]({short_url})\n"
        )

    # 안내 문구
    formatted_results.append("\n_※ 가격은 대략적 범위. 정확한 가격/할인율은 링크에서!_\n")

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
