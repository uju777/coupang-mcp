# Coupang MCP

Claude Code 쓰다가 쿠팡 검색하려고 브라우저 왔다갔다 하는 게 귀찮아서 만들었어요.
별도 API 설정 없이 바로 쓸 수 있습니다.

## 왜 만들었나요?

| 쿠팡 앱으로 할 때 | MCP로 할 때 |
|-------------------|-------------|
| 앱 열고 → 검색하고 → 스크롤하고 → 비교하고 | "맥북 최저가" 한마디면 끝 |
| 광고 상품이 섞여있어서 헷갈림 | 광고 없이 깔끔하게 |
| 가격순 정렬 직접 해야 함 | 알아서 정렬해줌 |
| 베스트 상품 보려면 메뉴 찾아야 함 | "가전 베스트" 하면 바로 |
| 골드박스는 따로 들어가야 함 | "오늘 특가 뭐야" 하면 끝 |

## 쓰면서 좋았던 점

- **시간 절약** - 앱 열고 스크롤하고 비교하고... 이런 거 안 해도 돼요
- **비교가 편함** - 가격순으로 한눈에 볼 수 있어요
- **대화하듯 검색** - "맥북 검색" → "M4만" → "에어랑 프로 차이?" 이런 식으로 좁혀나갈 수 있어요
- **로켓배송 구분** - 🚀 이모지로 바로 보여요
- **숨은 상품 발견** - 앱 추천에 안 뜨던 상품들도 검색돼요

## 이렇게 쓰면 돼요

| 이렇게 물어보면 | 이렇게 나와요 |
|-----------------|---------------|
| "아이패드 최저가 찾아줘" | 가격순으로 정렬된 결과 |
| "가전 요즘 뭐 잘 팔려?" | 가전 베스트 상품 |
| "오늘 쿠팡 세일 뭐야" | 골드박스 특가 상품 |
| "고양이 사료 인기상품" | 반려동물 베스트 |

## 설치 방법

MCP 설정 파일에 이거 추가하면 됩니다:

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
| 상품 검색 | 키워드로 검색 | "에어팟 검색해줘" |
| 베스트 상품 | 카테고리별 인기 상품 | "가전 베스트 보여줘" |
| 골드박스 | 오늘의 특가 | "오늘 특가 뭐 있어?" |
| 링크 단축 | 긴 URL 짧게 | 공유할 때 편해요 |

## 카테고리 번호

베스트 상품 검색할 때 쓰는 번호예요.

| 번호 | 카테고리 | 번호 | 카테고리 |
|------|----------|------|----------|
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

I made this because I got tired of switching between Claude Code and the browser to search Coupang.
Works without any API setup.

### Why I made this

| Using Coupang app | Using MCP |
|-------------------|-----------|
| Open app → search → scroll → compare | Just say "MacBook price" |
| Ads mixed in results | Clean results |
| Manual price sorting | Auto-sorted |
| Navigate menus for best sellers | Just ask |

### What I like about it

- **Saves time** - No more app switching
- **Easy comparison** - Price-sorted at a glance
- **Conversational** - Narrow down through chat
- **Rocket delivery** - 🚀 emoji shows fast shipping
- **Hidden gems** - Finds products not in app recommendations

### How to use

| Say this | Get this |
|----------|----------|
| "iPad lowest price" | Price-sorted results |
| "Electronics best sellers" | Best products |
| "Coupang deals today" | Gold Box deals |

</details>

---

## License

MIT
