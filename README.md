# 쿠팡 MCP

Claude, Cursor, Claude Code에서 쿠팡 상품을 검색하세요. API 키 필요 없음.

## 이런 점이 좋아요

- **최저가 비교** - 가격순으로 한눈에
- **로켓배송 표시** - 🚀 이모지로 바로 구분
- **중고상품도 검색** - 앱에서 잘 안 뜨는 상품들도 나옴
- **골드박스 특가** - 매일 앱 안 열어도 바로 확인

## 기능

- **상품 검색** - 키워드로 쿠팡 상품 검색
- **베스트 상품** - 카테고리별 인기 상품 조회
- **골드박스** - 오늘의 특가/할인 상품
- **링크 단축** - 긴 URL을 짧게

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

### 사용법

그냥 물어보세요:
- "쿠팡에서 에어팟 검색해줘"
- "가전 베스트 상품 보여줘"
- "오늘 골드박스 뭐 있어?"

## 카테고리 ID

| ID | 카테고리 |
|----|----------|
| 1001 | 여성패션 |
| 1002 | 남성패션 |
| 1010 | 뷰티 |
| 1012 | 식품 |
| 1016 | 가전디지털 |
| 1017 | 스포츠/레저 |
| 1024 | 헬스/건강식품 |
| 1029 | 반려동물용품 |

---

<details>
<summary>English</summary>

## Coupang MCP

Search Coupang products from Claude, Cursor, or Claude Code. No API key required.

### Why use this?

- **Price comparison** - See prices at a glance
- **Rocket delivery** - 🚀 emoji shows fast shipping
- **Hidden products** - Find items not shown in the app
- **Gold Box deals** - Check daily deals instantly

### Usage

Just ask:
- "Search AirPods on Coupang"
- "Show me best sellers in electronics"
- "What's on Gold Box today?"

</details>

---

MCP, Model Context Protocol, Coupang, 쿠팡, 최저가, 로켓배송, Claude, Cursor, Claude Code

## License

MIT
