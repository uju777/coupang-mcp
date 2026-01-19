# 쿠팡 MCP

**API 키 없이 바로 사용.** Claude, Cursor, Claude Code에서 쿠팡 상품을 검색하세요.

## 기능

- **상품 검색** - 키워드로 쿠팡 상품 검색
- **베스트 상품** - 카테고리별 인기 상품 조회
- **골드박스** - 오늘의 특가/할인 상품
- **링크 단축** - 쿠팡 URL을 짧은 링크로 변환

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

**No API Key Required.** Search Coupang products directly from Claude, Cursor, or Claude Code.

### Features

- **Product Search** - Search Coupang products by keyword
- **Best Sellers** - Get best selling products by category
- **Gold Box** - Today's deals and discounts
- **Deep Link** - Convert Coupang URLs to short links

### Usage

Just ask:
- "Search AirPods on Coupang"
- "Show me best sellers in electronics"
- "What's on Gold Box today?"

</details>

---

MCP, Model Context Protocol, Coupang, 쿠팡, Shopping, Korea, E-commerce, Claude, Cursor, Claude Code, AI Assistant

## License

MIT
