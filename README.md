# Coupang MCP

Claude에서 쿠팡 상품을 검색할 수 있는 MCP입니다. 별도 API 설정 없이 바로 사용할 수 있습니다.

Claude Web, Claude Desktop, Claude Code, Cursor 모두 지원합니다.

## 특징

| 쿠팡 앱 | MCP |
|---------|-----|
| 앱 실행 → 검색 → 스크롤 → 비교 | "맥북 최저가" 한마디로 끝 |
| 광고 상품 혼재 | 광고 없는 결과 |
| 수동 가격 정렬 | 자동 정렬 |
| 베스트/골드박스 메뉴 탐색 필요 | 바로 조회 |

## 장점

- **시간 절약** - 앱 전환 없이 대화로 검색
- **간편한 비교** - 가격순 정렬로 한눈에
- **대화형 검색** - "맥북 검색" → "M4만" → "에어랑 프로 차이?" 순차적으로 좁혀가기
- **로켓배송 표시** - 🚀 이모지로 구분
- **숨은 상품** - 앱 추천에 노출되지 않는 상품도 검색 가능
- **다음 행동 제안** - 검색 후 뭘 해야 할지 알려줌

## 다음 행동 제안

검색 결과 끝에 다음에 할 수 있는 행동을 제안합니다.

```
---
**다음 행동:**
| 가격 비교 | 인기 상품 | 특가 확인 |
|----------|----------|----------|
| "맥북 비교표 만들어줘" | "베스트 상품 보여줘" | "오늘 특가 뭐 있어?" |

💡 **팁**: "가격순 정렬해줘", "로켓배송만" 으로 필터링 가능
```

## 사용 예시

**가격 비교할 때**
> "맥북 에어 M3 쿠팡 최저가 알려줘"
> "아이패드 프로 11인치 가격 비교"

**급하게 필요할 때**
> "오늘 도착하는 충전기 찾아줘" → 로켓배송 🚀 상품만
> "내일 오는 생수 2L 제일 싼 거"

**뭐 살지 모를 때**
> "요즘 무선이어폰 뭐가 잘 팔려?"
> "공기청정기 인기순위 top 5"

**특가 찾을 때**
> "오늘 쿠팡 타임딜 뭐 있어?"
> "골드박스에서 가전제품 할인하는 거"

## 이런 것도 됩니다

**블로그용 비교표**
> "다이슨 청소기 5개 검색해서 가격 비교표 만들어줘"

→ 마크다운 표로 바로 복붙 가능

**선물 고르기**
> "20대 여자 생일선물 5만원대 추천"
> "60대 아빠 생신선물 추천"
> "집들이선물 3만원대" / "출산선물 베스트 5개"

**쿠팡 vs 네이버**
> "맥북 에어 쿠팡이랑 네이버 어디가 더 싸?"

[네이버 검색 MCP](https://github.com/uju777/mcp-server-naver-search)와 함께 사용 (네이버는 API 키 필요)

## 설치

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

| 기능 | 설명 | 예시 |
|------|------|------|
| 상품 검색 | 키워드 검색 | "에어팟 검색해줘" |
| 베스트 상품 | 카테고리별 인기 상품 | "가전 베스트" |
| 골드박스 | 오늘의 특가 | "오늘 특가 뭐야" |
| 링크 단축 | URL 단축 | 공유용 |

## 카테고리

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

MCP for searching Coupang products from Claude. No API setup required.

Works with Claude Web, Claude Desktop, Claude Code, and Cursor.

### Features

| Coupang App | MCP |
|-------------|-----|
| Launch → Search → Scroll → Compare | Just say "MacBook price" |
| Ads mixed in | Clean results |
| Manual sorting | Auto-sorted |
| Menu navigation | Direct access |

### Benefits

- **Save time** - Search through conversation
- **Easy comparison** - Price-sorted at a glance
- **Conversational** - Narrow down step by step
- **Rocket delivery** - 🚀 emoji indicator
- **Hidden products** - Find items not in app recommendations
- **Next action suggestions** - Shows what to do next

### Next Action Suggestions

Each search result includes suggested next actions:

```
---
**Next actions:**
| Compare | Popular | Deals |
|---------|---------|-------|
| "Compare MacBook prices" | "Show bestsellers" | "Today's deals" |

💡 **Tip**: Filter with "sort by price" or "rocket delivery only"
```

### Examples

| Query | Result |
|-------|--------|
| "iPad lowest price" | Price-sorted results |
| "Electronics best sellers" | Best products |
| "Coupang deals today" | Gold Box deals |

### Use with Naver

Use with [Naver Search MCP](https://github.com/uju777/mcp-server-naver-search) for price comparison across platforms (Naver requires API key)

</details>

---

## License

MIT © [uju777](https://github.com/uju777)
