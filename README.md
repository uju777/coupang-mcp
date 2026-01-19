# Coupang MCP

Claude, Cursor, Claude Code에서 쿠팡 상품을 검색하세요. 별도 API 설정 필요 없이 바로 사용.

## 앱 vs MCP

| 📱 앱으로 검색할 때 | 🤖 MCP로 검색할 때 |
|---------------------|---------------------|
| 앱 열기 → 검색 → 스크롤 → 비교 | "맥북 최저가" 한마디 끝 |
| 광고 상품 섞여있음 | 광고 없이 깔끔 |
| 가격순 정렬 수동 | 자동 정렬 + 링크까지 |
| 베스트 찾으려면 메뉴 뒤적뒤적 | "가전 베스트" 바로 조회 |
| 골드박스 페이지 따로 들어가야 함 | "오늘 특가" 한마디 |
| 여러 상품 비교 = 탭 왔다갔다 | 한 화면에 정리 |

## 이런 점이 좋아요

- **시간 절약** - 앱 열고 스크롤하고 비교하고... MCP는 말 한마디로 끝
- **깔끔한 비교** - 가격순 정렬 + 한눈에 비교
- **대화하며 쇼핑** - "맥북 검색" → "M4만" → "에어랑 프로 차이?" 대화하듯 좁혀나가기
- **로켓배송 표시** - 🚀 이모지로 바로 구분
- **숨은 상품 발견** - 앱 추천에 안 뜨는 상품들도 검색됨

## 사용 예시

| 이렇게 말하면 | 이렇게 검색됨 |
|---------------|---------------|
| "아이패드 최저가" | 상품검색 → 가격순 |
| "가전 요즘 뭐 잘 팔려?" | 베스트(1016) |
| "오늘 쿠팡 세일 뭐야" | 골드박스 특가 |
| "고양이 사료 인기상품" | 베스트(1029) |

## 설치

### Claude Desktop / Cursor / Claude Code

MCP 설정에 추가:

```json
{
  "mcpServers": {
    "coupang": {
      "command": "sh",
      "args": [
        "-c",
        "cd /path/to/coupang-mcp/client && uv run --with 'mcp[cli]' --with httpx python server.py"
      ]
    }
  }
}
```

## 기능

| 도구 | 설명 | 예시 |
|------|------|------|
| 상품 검색 | 키워드로 검색 | "에어팟 최저가 찾아줘" |
| 베스트 상품 | 카테고리별 인기 | "가전 베스트 뭐야?" |
| 골드박스 | 오늘의 특가 | "오늘 쿠팡 특가 뭐 있어?" |
| 링크 단축 | URL → 짧은 링크 | 블로그/공유용 |

## 카테고리 ID

| ID | 카테고리 | ID | 카테고리 |
|----|----------|----|----------|
| 1001 | 여성패션 | 1002 | 남성패션 |
| 1010 | 뷰티 | 1011 | 출산/유아 |
| 1012 | 식품 | 1013 | 주방용품 |
| 1014 | 생활용품 | 1015 | 홈인테리어 |
| 1016 | 가전디지털 | 1017 | 스포츠/레저 |
| 1018 | 자동차용품 | 1024 | 헬스/건강식품 |
| 1029 | 반려동물용품 | | |

---

<details>
<summary>English</summary>

## Coupang MCP

Search Coupang products from Claude, Cursor, or Claude Code. No API setup required.

### App vs MCP

| 📱 App | 🤖 MCP |
|--------|--------|
| Open app → search → scroll → compare | Just say "MacBook lowest price" |
| Ads mixed in | Clean, no ads |
| Manual price sorting | Auto-sorted + links |
| Multiple tabs to compare | All in one view |

### Why use this?

- **Save time** - One sentence instead of app navigation
- **Easy comparison** - Price-sorted at a glance
- **Conversational** - Narrow down through dialogue
- **Rocket delivery** - 🚀 emoji shows fast shipping
- **Hidden products** - Find items not shown in app recommendations

### Usage

| Say this | Gets this |
|----------|-----------|
| "iPad lowest price" | Product search |
| "Electronics best sellers" | Best products |
| "Coupang deals today" | Gold Box |

</details>

---

MCP, Model Context Protocol, Coupang, 쿠팡, 최저가, 로켓배송, Claude, Cursor, Claude Code

## License

MIT
